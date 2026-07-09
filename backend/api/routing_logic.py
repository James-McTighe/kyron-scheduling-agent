from .models import Doctor, PhysicianProtocol, AvailabilitySlot, db


def get_valid_slots(patient, body_part: str, issue_type: str, location=None):
    """
    Queries slots based strictly on body part, issue type, location, and patient status constraints.
    """
    matching_protocols = PhysicianProtocol.query.filter_by(
        body_part=body_part, issue_type=issue_type
    ).all()

    if not matching_protocols:
        return []

    valid_doctor_ids = [p.doctor_id for p in matching_protocols]

    slot_query = AvailabilitySlot.query.filter(
        AvailabilitySlot.doctor_id.in_(valid_doctor_ids),
        AvailabilitySlot.is_booked == False,
    )

    if location:
        slot_query = slot_query.filter(AvailabilitySlot.location == location)

    all_potential_slots = slot_query.all()
    final_slots = []

    for slot in all_potential_slots:
        doctor = slot.doctor
        if patient.is_new_patient and doctor.accepts_new_patients:
            final_slots.append(slot)

    return final_slots
