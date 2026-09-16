"""
OMR reader for the photographed A1/B1 bubble answer sheets.

Deterministic: the sheet geometry is not guessed, it is the same geometry the
renderer draws with (see _bubble_sheet in tools/generate_a1_exam.py). The photo
is rectified onto that geometry using the four solid corner markers, then every
bubble is sampled at its known position.

    1. find the 4 solid 8 mm corner squares
    2. perspective-warp the sheet to a flat A4 canvas at SCALE px/mm
    3. flatten shading (divide by a large-kernel background estimate)
    4. per bubble, measure the dark-pixel fraction inside the ring
    5. pick the darkest bubble; flag rows that are blank or too close to call

Marks count whether they are a filled bubble, a tick or an X drawn over the
choice — anything that darkens the ring.

Writes:  .tmp/bubble_reads_<tag>.json      (same schema grade_bubble_sheets eats)
         .tmp/omr_debug_<tag>/<sheet>.png  (annotated overlay, for eyeballing)

Run: py tools/read_bubble_sheets.py "PM 101 A1 Weekly Exam" exam_a1_u11-15_future.json pm101w
"""

import json
import os
import sys
import glob

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# ── sheet geometry, in millimetres from the top-left of the A4 page ──────────
# mirrors tools/generate_a1_exam.py: BUBBLE_R, ROW_H, GRID_TOP, COL_X, ...
PAGE_W_MM, PAGE_H_MM = 210.0, 297.0
MARKER_XY = ((16.0, 16.0), (194.0, 16.0), (194.0, 281.0), (16.0, 281.0))  # centres
GRID_TOP_MM = 66.0
ROW_H_MM = 11.0
COL_X_MM = (34.0, 122.0)
BUBBLE_X0_MM = 8.0
BUBBLE_DX_MM = 11.0
BUBBLE_R_MM = 3.2

SCALE = 6                      # px per mm on the rectified canvas
SAMPLE_R_MM = 2.15             # sample disc, inside the printed ring
DARK_REL = 0.78                # pixel counts as ink below this share of paper

SEARCH_MM = 5.0                # how far the grid lock-on may correct the warp
RING_MIN = 0.20                # below this the sheet did not rectify properly

PICK_MIN = 0.16                # a mark must darken this share of the disc
PICK_GAP = 0.10                # winner must beat runner-up by this much
PICK_RATIO = 2.0               # ...or by this factor

MARKED_MIN = 0.50              # a second bubble this dark means the row was changed
                               # (deliberately high: smudges and erased marks sit
                               #  around 0.3-0.4, real second marks at 0.55+)
STRIKE_R_MM = 5.0              # radius of the paper ring watched for strike-through
STRIKE_OUT = 0.035             # ink out there = the choice was crossed out
                               # (a clean fill measures 0.00-0.02, a struck one 0.05+)


def _order_quad(pts):
    """corners as TL, TR, BR, BL."""
    pts = np.array(pts, dtype=np.float32)
    s, d = pts.sum(1), np.diff(pts, axis=1).ravel()
    return np.array([pts[np.argmin(s)], pts[np.argmin(d)],
                     pts[np.argmax(s)], pts[np.argmax(d)]], dtype=np.float32)


ASPECT = (MARKER_XY[2][1] - MARKER_XY[0][1]) / (MARKER_XY[1][0] - MARKER_XY[0][0])  # 265/178
SIDE_FRAC = 8.0 / (MARKER_XY[1][0] - MARKER_XY[0][0])          # marker side vs quad width


def flatten(gray):
    """Divide out the lighting so a shadowed photo thresholds like a flat one."""
    bg = cv2.medianBlur(gray, 101).astype(np.float32)
    bg[bg < 30] = 30
    return np.clip(gray.astype(np.float32) / bg * 200.0, 0, 255).astype(np.uint8)


def marker_candidates(gray):
    """Solid dark squares, pooled over a few thresholds and deduped."""
    h, w = gray.shape
    flat = flatten(cv2.GaussianBlur(gray, (5, 5), 0))
    found = []
    for thr in (90, 110, 130, 150):
        _, binv = cv2.threshold(flat, thr, 255, cv2.THRESH_BINARY_INV)
        binv = cv2.morphologyEx(binv, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
        n, _, stats, cent = cv2.connectedComponentsWithStats(binv, 8)
        for i in range(1, n):
            x, y, bw, bh, area = stats[i]
            if bw < 10 or bh < 10 or bw > w * 0.12 or bh > h * 0.12:
                continue
            if not 0.65 <= bw / bh <= 1.55:
                continue
            if area / float(bw * bh) < 0.72:              # solid, not an outline
                continue
            found.append((cent[i][0], cent[i][1], (bw + bh) / 2.0))

    merged = []
    for cx, cy, s in found:
        for m in merged:
            if abs(m[0] - cx) < s and abs(m[1] - cy) < s:
                break
        else:
            merged.append((cx, cy, s))
    return merged


def _quad_ok(quad, sizes=None):
    wid = (np.linalg.norm(quad[1] - quad[0]) + np.linalg.norm(quad[2] - quad[3])) / 2
    hei = (np.linalg.norm(quad[3] - quad[0]) + np.linalg.norm(quad[2] - quad[1])) / 2
    if wid < 200 or hei < 200:
        return 0.0
    if not 0.88 <= (hei / wid) / ASPECT <= 1.12:
        return 0.0
    if sizes is not None:
        side = float(np.mean(sizes))
        if not 0.6 <= (side / wid) / SIDE_FRAC <= 1.6:
            return 0.0
        if max(sizes) / max(min(sizes), 1e-6) > 1.8:
            return 0.0
    return wid * hei


def _refine_corner(gray, guess, side):
    """Find the real marker near a predicted corner.

    Perspective means the parallelogram guess can miss by well over a marker's
    width, and a marker touching the dark desk merges into it, so blob analysis
    is unreliable here. Match a black square inside a white margin instead —
    that shape only scores on an isolated square, not on a big dark region.
    """
    flat = flatten(cv2.GaussianBlur(gray, (5, 5), 0))
    side = int(round(side))
    pad = max(4, side // 2)
    tpl = np.full((side + 2 * pad, side + 2 * pad), 255, np.uint8)
    tpl[pad:pad + side, pad:pad + side] = 0

    r = int(side * 7)
    x0, y0 = int(max(0, guess[0] - r)), int(max(0, guess[1] - r))
    x1, y1 = int(min(gray.shape[1], guess[0] + r)), int(min(gray.shape[0], guess[1] + r))
    win = flat[y0:y1, x0:x1]
    if win.shape[0] <= tpl.shape[0] or win.shape[1] <= tpl.shape[1]:
        return [(np.array(guess, dtype=np.float32), 0.0)]

    res = cv2.matchTemplate(win, tpl, cv2.TM_CCOEFF_NORMED)
    out = []
    for _ in range(3):                                    # keep a few peaks and
        _, peak, _, loc = cv2.minMaxLoc(res)               # let the grid fit judge
        if peak < 0.40:
            break
        out.append((np.array([x0 + loc[0] + pad + side / 2.0,
                              y0 + loc[1] + pad + side / 2.0], np.float32), peak))
        cv2.circle(res, loc, int(side), 0.0, -1)           # suppress this peak
    out.append((np.array(guess, dtype=np.float32), 0.0))   # ...and the plain guess
    return out


def candidate_quads(gray):
    """Plausible corner quads, best-guess first. The caller picks by grid fit."""
    cands = marker_candidates(gray)
    if len(cands) < 3:
        return []
    pts = np.array([[c[0], c[1]] for c in cands], dtype=np.float32)
    sizes = np.array([c[2] for c in cands], dtype=np.float32)
    n = len(cands)
    out = []

    for i in range(n):                                   # exhaustive: n is small
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                for l in range(k + 1, n):
                    idx = [i, j, k, l]
                    quad = _order_quad(pts[idx])
                    if len(np.unique(quad, axis=0)) != 4:
                        continue
                    area = _quad_ok(quad, sizes[idx])
                    if area > 0:
                        out.append((area + 1e9, quad))    # complete quads win ties

    # three markers only — the fourth is regularly lost to shadow or to the dark
    # desk it touches. Rebuild it as the parallelogram corner, then snap it onto
    # the real square (perspective can put it 100+ px from the guess).
    for i in range(n):
        for j in range(n):
            for k in range(n):
                if len({i, j, k}) != 3:
                    continue
                tl, tr, bl = pts[i], pts[j], pts[k]
                wid, hei = np.linalg.norm(tr - tl), np.linalg.norm(bl - tl)
                if wid < 200 or hei < 200:
                    continue
                if not 0.86 <= (hei / wid) / ASPECT <= 1.14:
                    continue
                if abs(float(np.dot(tr - tl, bl - tl)) / (wid * hei)) > 0.18:
                    continue                              # corners are ~90°
                side = float(np.mean(sizes[[i, j, k]]))
                if not 0.6 <= (side / wid) / SIDE_FRAC <= 1.6:
                    continue
                for br, peak in _refine_corner(gray, tr + bl - tl, side):
                    quad = np.array([tl, tr, br, bl], dtype=np.float32)
                    if _quad_ok(quad) > 0:
                        out.append((wid * hei * (1 + peak), quad))

    out.sort(key=lambda t: -t[0])
    keep, seen = [], []
    for _, quad in out:                                   # drop near-duplicates
        if any(np.max(np.abs(quad - q)) < 12 for q in seen):
            continue
        seen.append(quad)
        keep.append(quad)
        if len(keep) >= 12:
            break
    return keep


def warp_to_page(img, quad):
    dst = np.array([[x * SCALE, y * SCALE] for x, y in MARKER_XY], dtype=np.float32)
    M = cv2.getPerspectiveTransform(quad, dst)
    size = (int(PAGE_W_MM * SCALE), int(PAGE_H_MM * SCALE))
    flat = cv2.warpPerspective(img, M, size, flags=cv2.INTER_CUBIC,
                               borderValue=(255, 255, 255))
    g = cv2.cvtColor(flat, cv2.COLOR_BGR2GRAY)
    bg = cv2.medianBlur(g, 101).astype(np.float32)
    bg[bg < 40] = 40
    norm = np.clip(g.astype(np.float32) / bg, 0, 2.0)     # 1.0 = paper, <1 = ink
    return flat, norm


def _ring_patch():
    r = int(BUBBLE_R_MM * SCALE)
    size = 2 * (r + 2) + 1
    tpl = np.zeros((size, size), np.float32)
    cv2.circle(tpl, (r + 2, r + 2), r, 1.0, 2)
    return tpl


def refine_by_rings(flat, centres, search_mm=7.0):
    """Re-warp using the printed rings themselves as control points.

    The corner markers give a homography from four points at the extreme edges;
    a curled or steeply-shot page still leaves millimetres of error in the
    middle. Each printed ring is a control point, so re-fitting on all of them
    corrects the shape rather than just sliding the grid around.
    """
    g = cv2.cvtColor(flat, cv2.COLOR_BGR2GRAY)
    bg = cv2.medianBlur(g, 101).astype(np.float32)
    bg[bg < 40] = 40
    ink = (np.clip(g.astype(np.float32) / bg, 0, 2.0) < 0.86).astype(np.float32)

    tpl = _ring_patch()
    half = tpl.shape[0] // 2
    s = int(search_mm * SCALE)
    src, dst = [], []
    for x_mm, y_mm in centres:
        cx, cy = int(round(x_mm * SCALE)), int(round(y_mm * SCALE))
        y0, y1 = cy - half - s, cy + half + s + 1
        x0, x1 = cx - half - s, cx + half + s + 1
        if y0 < 0 or x0 < 0 or y1 > ink.shape[0] or x1 > ink.shape[1]:
            continue
        res = cv2.matchTemplate(ink[y0:y1, x0:x1], tpl, cv2.TM_CCOEFF_NORMED)
        _, peak, _, loc = cv2.minMaxLoc(res)
        if peak < 0.35:
            continue
        src.append([x0 + loc[0] + half, y0 + loc[1] + half])
        dst.append([cx, cy])

    if len(src) < 24:
        return None
    H, mask = cv2.findHomography(np.array(src, np.float32), np.array(dst, np.float32),
                                 cv2.RANSAC, 3.0)
    if H is None or int(mask.sum()) < 24:
        return None
    size = (int(PAGE_W_MM * SCALE), int(PAGE_H_MM * SCALE))
    out = cv2.warpPerspective(flat, H, size, flags=cv2.INTER_CUBIC,
                              borderValue=(255, 255, 255))
    g2 = cv2.cvtColor(out, cv2.COLOR_BGR2GRAY)
    bg2 = cv2.medianBlur(g2, 101).astype(np.float32)
    bg2[bg2 < 40] = 40
    return out, np.clip(g2.astype(np.float32) / bg2, 0, 2.0)


def rectify(img, centres):
    """Warp the sheet flat, choosing the corner quad whose grid actually lands."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    best = None
    for quad in candidate_quads(gray):
        flat, norm = warp_to_page(img, quad)
        fit = align_grid(norm, centres)
        if best is None or fit[6] > best[2][6]:
            best = (flat, norm, fit)
        if fit[6] > 0.40:                                 # clearly the right one
            break
    if best is None:
        return None, None, None

    flat, norm, fit = best
    for _ in range(2):
        if fit[6] > 0.42:
            break
        refined = refine_by_rings(flat, centres)
        if refined is None:
            break
        r_flat, r_norm = refined
        r_fit = align_grid(r_norm, centres)
        if r_fit[6] <= fit[6] + 0.005:
            break
        flat, norm, fit = r_flat, r_norm, r_fit
    return flat, norm, fit


def rectify_best(img, centres):
    """Try every candidate quad, refit each on the rings, keep the best fit.

    Slower than rectify(), and only needed for the awkward photos: a sheet whose
    fourth marker is cropped out of frame or swallowed by the dark desk gets a
    skewed first guess, and the ring refit has to pull it back.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    best = None
    for quad in candidate_quads(gray):
        flat, norm = warp_to_page(img, quad)
        fit = align_grid(norm, centres)
        for _ in range(3):
            refined = refine_by_rings(flat, centres, search_mm=9.0)
            if refined is None:
                break
            r_flat, r_norm = refined
            r_fit = align_grid(r_norm, centres)
            if r_fit[6] <= fit[6] + 0.005:
                break
            flat, norm, fit = r_flat, r_norm, r_fit
        if best is None or fit[6] > best[2][6]:
            best = (flat, norm, fit)
        if fit[6] > 0.45:
            break
    return best if best else (None, None, None)


def _ring_template(shape, centres):
    """Synthetic picture of the empty grid: just the printed rings."""
    tpl = np.zeros(shape, np.float32)
    for x, y in centres:
        cv2.circle(tpl, (int(round(x * SCALE)), int(round(y * SCALE))),
                   int(BUBBLE_R_MM * SCALE), 1.0, 2)
    return tpl


def _ring_energy(ink, centres, dx, dy, sx, sy, cx, cy):
    """How well the printed rings line up under this correction."""
    r_out = int(3.7 * SCALE)
    r_in = int(2.6 * SCALE)
    yy, xx = np.ogrid[-r_out:r_out + 1, -r_out:r_out + 1]
    d2 = yy * yy + xx * xx
    ann = (d2 <= r_out * r_out) & (d2 >= r_in * r_in)
    tot, n = 0.0, 0
    for x, y in centres:
        px = int(round((cx + (x - cx) * sx + dx) * SCALE))
        py = int(round((cy + (y - cy) * sy + dy) * SCALE))
        y0, y1, x0, x1 = py - r_out, py + r_out + 1, px - r_out, px + r_out + 1
        if y0 < 0 or x0 < 0 or y1 > ink.shape[0] or x1 > ink.shape[1]:
            continue
        tot += float(ink[y0:y1, x0:x1][ann].mean())
        n += 1
    return tot / max(n, 1)


def align_grid(norm, centres):
    """Lock the nominal grid onto the rings actually printed on this photo.

    The corner markers put us within a few millimetres; a shadowed or curled
    sheet can still leave a drift big enough to sample the neighbouring bubble.
    The printed rings are always there, marked or not, so we align to them.
    Returns (dx, dy, sx, sy, cx, cy) in millimetres / ratios.
    """
    ink = (norm < 0.86).astype(np.float32)
    cx = float(np.mean([p[0] for p in centres]))
    cy = float(np.mean([p[1] for p in centres]))

    # The grid repeats every 11 mm down and 88 mm across, so an unbounded search
    # happily locks onto the wrong row or the wrong column. The corner markers
    # already put us close, so only ever look for a small correction.
    coarse_pts = centres[::3]
    dx = dy = 0.0
    best_s = -1.0
    for ddx in np.arange(-SEARCH_MM, SEARCH_MM + 0.01, 0.5):
        for ddy in np.arange(-SEARCH_MM, SEARCH_MM + 0.01, 0.5):
            s = _ring_energy(ink, coarse_pts, ddx, ddy, 1, 1, cx, cy)
            if s > best_s:
                dx, dy, best_s = ddx, ddy, s

    best_s = _ring_energy(ink, centres, dx, dy, 1, 1, cx, cy)
    for ddx in np.arange(-0.6, 0.61, 0.2):
        for ddy in np.arange(-0.6, 0.61, 0.2):
            s = _ring_energy(ink, centres, dx + ddx, dy + ddy, 1, 1, cx, cy)
            if s > best_s:
                dx, dy, best_s = dx + ddx, dy + ddy, s

    sx, sy = 1.0, 1.0
    best_s = _ring_energy(ink, centres, dx, dy, sx, sy, cx, cy)
    for cand_sy in np.arange(0.955, 1.0451, 0.005):
        s = _ring_energy(ink, centres, dx, dy, 1.0, cand_sy, cx, cy)
        if s > best_s:
            sy, best_s = cand_sy, s
    for cand_sx in np.arange(0.955, 1.0451, 0.005):
        s = _ring_energy(ink, centres, dx, dy, cand_sx, sy, cx, cy)
        if s > best_s:
            sx, best_s = cand_sx, s
    for ddx in np.arange(-1.0, 1.01, 0.2):               # final nudge after scaling
        for ddy in np.arange(-1.0, 1.01, 0.2):
            s = _ring_energy(ink, centres, dx + ddx, dy + ddy, sx, sy, cx, cy)
            if s > best_s:
                dx, dy, best_s = dx + ddx, dy + ddy, s
    return dx, dy, sx, sy, cx, cy, best_s


def bubble_centres(total_q, tf_rows):
    """{q: [(letter, x_mm, y_mm), ...]} exactly where the renderer put them."""
    rows_per_col = (total_q + 1) // 2
    out = {}
    for col in range(2):
        for row in range(rows_per_col):
            q = col * rows_per_col + row + 1
            if q > total_q:
                break
            y = GRID_TOP_MM + row * ROW_H_MM
            x0 = COL_X_MM[col] + BUBBLE_X0_MM
            letters = ("t", "f") if q in tf_rows else ("a", "b", "c", "d")
            out[q] = [(l, x0 + k * BUBBLE_DX_MM, y) for k, l in enumerate(letters)]
    return out


def score_bubble(norm, x_mm, y_mm):
    """(fill, outside) for one bubble.

    fill    share of the disc that is ink — shape-blind, because students mark
            with solid fills, scribbled loops and ticks, and all of them count.
    outside ink in the ring of paper just beyond the bubble. A cancelled answer
            is struck through, and the stroke runs past the circle; a fill,
            however heavy, stays inside it. That is what separates 'I chose
            this' from 'I crossed this out' — the sheet's own legend, 'Correct:
            ● Wrong: ⊘', is exactly this distinction.
    """
    r = int(SAMPLE_R_MM * SCALE)
    r_out = int(STRIKE_R_MM * SCALE)
    cx, cy = int(round(x_mm * SCALE)), int(round(y_mm * SCALE))
    if (cy - r_out < 0 or cx - r_out < 0
            or cy + r_out + 1 > norm.shape[0] or cx + r_out + 1 > norm.shape[1]):
        return 0.0, 0.0

    yy, xx = np.ogrid[-r:r + 1, -r:r + 1]
    disc = (yy * yy + xx * xx) <= r * r
    inner = norm[cy - r:cy + r + 1, cx - r:cx + r + 1]
    fill = float((inner[disc] < DARK_REL).mean())

    yy, xx = np.ogrid[-r_out:r_out + 1, -r_out:r_out + 1]
    d2 = yy * yy + xx * xx
    ring = (d2 <= r_out * r_out) & (d2 >= (BUBBLE_R_MM + 0.6) ** 2 * SCALE * SCALE)
    outer = norm[cy - r_out:cy + r_out + 1, cx - r_out:cx + r_out + 1]
    return fill, float((outer[ring] < DARK_REL).mean())


def read_sheet(path, total_q, tf_rows):
    img = cv2.imread(path)
    if img is None:
        raise RuntimeError(f"unreadable image: {path}")
    nominal = bubble_centres(total_q, tf_rows)
    pts = [(x, y) for opts in nominal.values() for _, x, y in opts]
    flat, norm, fit = rectify(img, pts)
    if flat is not None and fit[6] < RING_MIN:
        flat, norm, fit = rectify_best(img, pts)
    if flat is None:
        return None, None, None
    dx, dy, sx, sy, cx, cy, energy = fit
    grid = {q: [(l, cx + (x - cx) * sx + dx, cy + (y - cy) * sy + dy)
                for l, x, y in opts] for q, opts in nominal.items()}

    answers, uncertain, scores = {}, [], {}
    for q, opts in grid.items():
        s = [(letter,) + score_bubble(norm, x, y) for letter, x, y in opts]
        scores[q] = {l: (round(f, 3), round(o, 3)) for l, f, o in s}
        marked = [t for t in s if t[1] >= MARKED_MIN]

        if len(marked) > 1:
            # changed answer: whatever is struck through is the abandoned one
            live = [t for t in marked if t[2] < STRIKE_OUT]
            gone = [t[0] for t in marked if t[2] >= STRIKE_OUT]
            if len(live) == 1:
                answers[str(q)] = live[0][0]
                uncertain.append({"q": q, "note": f"crossed out {','.join(gone)}, "
                                                 f"stands as {live[0][0]}"})
            else:
                best = max(marked, key=lambda t: t[1])
                answers[str(q)] = "?"
                uncertain.append({"q": q, "note": "two bubbles marked, neither crossed out ("
                                  + ", ".join(f"{l}={f:.2f}" for l, f, _ in marked)
                                  + f"); darkest was {best[0]}"})
            continue

        ranked = sorted(((l, f) for l, f, _ in s), key=lambda t: -t[1])
        top, second = ranked[0], ranked[1]
        if top[1] < PICK_MIN:
            answers[str(q)] = "-"
            uncertain.append({"q": q, "note": f"nothing marked (best {top[0]}={top[1]:.2f})"})
        elif top[1] - second[1] < PICK_GAP and top[1] < second[1] * PICK_RATIO:
            answers[str(q)] = top[0]
            uncertain.append({"q": q, "note": f"close call {top[0]}={top[1]:.2f} vs "
                                             f"{second[0]}={second[1]:.2f}"})
        else:
            answers[str(q)] = top[0]
    return answers, uncertain, (flat, scores, grid, (dx, dy, sx, sy, energy))


def debug_overlay(flat, scores, answers, grid, out_path):
    vis = flat.copy()
    for q, opts in grid.items():
        pick = answers[str(q)]
        for letter, x, y in opts:
            cx, cy = int(x * SCALE), int(y * SCALE)
            fill, outside = scores[q][letter]
            hit = letter == pick
            struck = fill >= MARKED_MIN and outside >= STRIKE_OUT
            colour = (0, 0, 220) if struck else (0, 170, 0) if hit else (200, 200, 200)
            cv2.circle(vis, (cx, cy), int(BUBBLE_R_MM * SCALE), colour,
                       2 if (hit or struck) else 1)
            cv2.putText(vis, f"{fill:.2f}|{outside:.2f}", (cx - 24, cy + int(6.5 * SCALE)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.30,
                        (0, 120, 0) if hit else (140, 140, 140), 1, cv2.LINE_AA)
        x0 = opts[0][1]
        cv2.putText(vis, f"{q}:{pick.upper()}", (int((x0 - 15) * SCALE), int(y * SCALE) + 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 220), 2, cv2.LINE_AA)
    cv2.imwrite(out_path, vis)


def load_manual(tag, total_q):
    """Hand-typed answers for sheets the reader cannot rectify.

    A photo that crops or shadows out a corner marker has no reliable geometry
    to warp against — no amount of tuning fixes a marker that is not in frame.
    Those sheets get read by eye and recorded in .tmp/manual_reads_<tag>.json as
    {"file.jpg": {"answers": "abcd...", "note": "..."}} — one letter per
    question, '-' for blank, '?' for a row with two live marks.
    """
    path = os.path.join(ROOT, ".tmp", f"manual_reads_{tag}.json")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    out = {}
    for fname, entry in raw.items():
        letters = entry["answers"].strip().lower()
        if len(letters) != total_q:
            raise ValueError(f"{fname}: {len(letters)} answers, expected {total_q}")
        out[fname] = ({str(i + 1): letters[i] for i in range(total_q)},
                      entry.get("note", "read by eye"))
    return out


def main():
    folder = sys.argv[1]
    config = sys.argv[2]
    tag = sys.argv[3]

    with open(os.path.join(HERE, config), encoding="utf-8") as f:
        cfg = json.load(f)
    tf_rows = set(cfg.get("tf_rows", []))
    total_q = sum(len(p.get("items") or p.get("statements") or []) for p in cfg["parts"])

    dbg_dir = os.path.join(ROOT, ".tmp", f"omr_debug_{tag}")
    os.makedirs(dbg_dir, exist_ok=True)

    manual = load_manual(tag, total_q)

    reads, failed = [], []
    for path in sorted(glob.glob(os.path.join(ROOT, folder, "*.jpg"))):
        fname = os.path.basename(path)
        row = {"file": fname, "name_written": os.path.splitext(fname)[0]}

        if fname in manual:
            answers, note = manual[fname]
            row.update({"answers": answers, "uncertain": [], "source": "manual"})
            reads.append(row)
            print(f"  {fname:26s} {''.join(answers[str(q)] for q in range(1, total_q + 1))}"
                  f"  MANUAL — {note}")
            continue

        answers, uncertain, extra = read_sheet(path, total_q, tf_rows)
        if answers is None:
            failed.append(fname)
            print(f"  !! {fname}: corner markers not found")
            continue
        flat, scores, grid, fit = extra
        debug_overlay(flat, scores, answers, grid,
                      os.path.join(dbg_dir, fname.replace(".jpg", ".png")))
        row.update({"answers": answers, "uncertain": uncertain, "source": "omr",
                    "fit": {"dx_mm": round(fit[0], 2), "dy_mm": round(fit[1], 2),
                            "sx": round(fit[2], 3), "sy": round(fit[3], 3),
                            "ring_energy": round(fit[4], 3)}})
        reads.append(row)
        if fit[4] < RING_MIN:
            print(f"     ^^ weak grid lock (ring {fit[4]:.2f}) — check this overlay by eye")
        flags = f"  [{len(uncertain)} to check]" if uncertain else ""
        print(f"  {fname:26s} {''.join(answers[str(q)] for q in range(1, total_q + 1))}"
              f"  fit dx{fit[0]:+.1f} dy{fit[1]:+.1f} sx{fit[2]:.3f} sy{fit[3]:.3f} "
              f"ring{fit[4]:.2f}{flags}")

    out = os.path.join(ROOT, ".tmp", f"bubble_reads_{tag}.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(reads, f, indent=1, ensure_ascii=False)
    print(f"\n{len(reads)} sheets read · {len(failed)} failed · {total_q} questions")
    print(f"reads:   {out}")
    print(f"overlays:{dbg_dir}")


if __name__ == "__main__":
    main()
