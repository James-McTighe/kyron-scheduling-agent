from .models import Doctor, PhysicianProtocol, AvailabilitySlot, db

def get_valid_slots(body_part: str, issue_type: str, is_new_patient: bool):
    """
    Queries slots based strictly on body part, issue type, and patient status constraints.
    """
    # 1. Base query for unbooked slots matching the targeted body part
    query = db.session.query(AvailabilitySlot).join(Doctor).join(PhysicianProtocol)
    
    query = query.filter(
        AvailabilitySlot.is_booked == False,
        PhysicianProtocol.body_part.ilike(body_part)
    )

    # 2. Issue Type Constraint Rule
    # If a doctor only lists "General" for a body part, they do NOT handle specialized issues
    # If the patient is calling about a fracture/sports medicine, they must explicitly match it
    if issue_type.lower() != 'general':
        query = query.filter(PhysicianProtocol.issue_type.ilike(issue_type))
    else:
        query = query.filter(PhysicianProtocol.issue_type.ilike('general'))

    # 3. New Patient Constraint Rule
    if is_new_patient:
        query = query.filter(Doctor.accepts_new_patients == True)

    return query.order_by(AvailabilitySlot.start_time.asc()).all()
