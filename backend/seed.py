from app import app
from models import db, Doctor, PhysicianProtocol, AvailabilitySlot
from datetime import datetime, timedelta

with app.app_context():
    db.create_all()

    # Clear old data if restarting
    db.session.query(AvailabilitySlot).delete()
    db.session.query(PhysicianProtocol).delete()
    db.session.query(Doctor).delete()

    # Create Doctors
    chen = Doctor(name="Dr. Maria Chen", accepts_new_patients=True)
    walsh = Doctor(name="Dr. James Walsh", accepts_new_patients=True)
    patel = Doctor(name="Dr. Aisha Patel", accepts_new_patients=False)
    db.session.add_all([chen, walsh, patel])
    db.session.commit()

    # Create Protocols
    protocols = [
        PhysicianProtocol(doctor_id=chen.id, body_part="Knee", issue_type="Joint Replacement"),
        PhysicianProtocol(doctor_id=chen.id, body_part="Knee", issue_type="Sports Medicine"),
        PhysicianProtocol(doctor_id=chen.id, body_part="Hip", issue_type="Joint Replacement"),
        
        PhysicianProtocol(doctor_id=walsh.id, body_part="Knee", issue_type="Fracture"),
        PhysicianProtocol(doctor_id=walsh.id, body_part="Knee", issue_type="Sports Medicine"),
        PhysicianProtocol(doctor_id=walsh.id, body_part="Foot/Ankle", issue_type="Fracture"),
        
        PhysicianProtocol(doctor_id=patel.id, body_part="Hip", issue_type="Joint Replacement"),
        PhysicianProtocol(doctor_id=patel.id, body_part="Spine", issue_type="General")
    ]
    db.session.add_all(protocols)

    # Seed Open Slots (Tomorrow at 9 AM and 10 AM)
    tomorrow = datetime.utcnow().date() + timedelta(days=1)
    slots = [
        AvailabilitySlot(doctor_id=chen.id, location="MAIN", start_time=datetime.combine(tomorrow, datetime.min.time()) + timedelta(hours=9)),
        AvailabilitySlot(doctor_id=walsh.id, location="NORTH", start_time=datetime.combine(tomorrow, datetime.min.time()) + timedelta(hours=10)),
        AvailabilitySlot(doctor_id=patel.id, location="MAIN", start_time=datetime.combine(tomorrow, datetime.min.time()) + timedelta(hours=11))
    ]
    db.session.add_all(slots)
    db.session.commit()
    print("Database seeded smoothly!")
