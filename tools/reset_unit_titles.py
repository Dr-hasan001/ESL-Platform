"""Reset all unit titles to 'Unit N' format."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal
from app.models.book import Unit

db = SessionLocal()
units = db.query(Unit).all()
for unit in units:
    expected = f"Unit {unit.unit_number}"
    if unit.title != expected:
        print(f"  Book {unit.book_id} Unit {unit.unit_number}: '{unit.title}' -> '{expected}'")
        unit.title = expected
db.commit()
print(f"Done. {len(units)} units checked.")
db.close()
