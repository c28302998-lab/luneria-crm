with open("backend/app/schemas/schemas.py", "r") as f:
    content = f.read()

import re

old_partner_base = """class PartnerBase(BaseModel):
    company_name: str
    contact: Optional[str] = None"""

new_partner_base = """class PartnerBase(BaseModel):
    company_name: str
    contact: Optional[str] = None
    country: Optional[str] = None
    seats: Optional[int] = 0
    payment_terms: Optional[str] = None
    experience: Optional[str] = None
    registration_time: Optional[str] = None
    response_time: Optional[str] = None
    rating: Optional[float] = None
    last_contact_date: Optional[str] = None"""

content = content.replace(old_partner_base, new_partner_base)

with open("backend/app/schemas/schemas.py", "w") as f:
    f.write(content)
