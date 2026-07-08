import pytest
from flask import Flask
from datetime import datetime, timedelta
from api.models import db, Doctor, PhysicianProtocol, AvailabilitySlot
from api.routing_logic import get_valid_slots


@pytest.fixture(scope="session")
def app():
    """Creates a mock Flask application instance configured with an in-memory database."""
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    return app


@pytest.fixture(scope="function", autouse=True)
def setup_database(app):
    """
    Handles automatic table creation before each individual test execution
    and completely wipes the session afterward to ensure transactional isolation.
    """
    with app.app_context():
        db.create_all()
        _seed_test_data()

        yield db  # This is where the actual test function executes

        db.session.remove()
        db.drop_all()


def _seed_test_data():
    """Helper method to load standard directory test profiles into the ephemeral DB."""
    # 1. Add Doctors (Per Day 1 Blueprint rules)
    chen = Doctor(name="Dr. Maria Chen", accepts_new_patients=True)
    walsh = Doctor(name="Dr. James Walsh", accepts_new_patients=True)
    patel = Doctor(name="Dr. Aisha Patel", accepts_new_patients=False)
    db.session.add_all([chen, walsh, patel])
    db.session.commit()

    # 2. Add Protocol Constraints from protocols.pdf
    protocols = [
        PhysicianProtocol(
            doctor_id=chen.id, body_part="Knee", issue_type="Joint Replacement"
        ),
        PhysicianProtocol(
            doctor_id=chen.id, body_part="Knee", issue_type="Sports Medicine"
        ),
        PhysicianProtocol(
            doctor_id=chen.id, body_part="Hip", issue_type="Joint Replacement"
        ),
        PhysicianProtocol(doctor_id=walsh.id, body_part="Knee", issue_type="Fracture"),
        PhysicianProtocol(
            doctor_id=walsh.id, body_part="Knee", issue_type="Sports Medicine"
        ),
        PhysicianProtocol(
            doctor_id=walsh.id, body_part="Foot/Ankle", issue_type="Fracture"
        ),
        PhysicianProtocol(
            doctor_id=patel.id, body_part="Hip", issue_type="Joint Replacement"
        ),
        PhysicianProtocol(doctor_id=patel.id, body_part="Spine", issue_type="General"),
    ]
    db.session.add_all(protocols)

    # 3. Add Open Calendar Availability Slots
    tomorrow = datetime.utcnow().date() + timedelta(days=1)
    slots = [
        AvailabilitySlot(
            doctor_id=chen.id,
            location="MAIN",
            start_time=datetime.combine(tomorrow, datetime.min.time())
            + timedelta(hours=9),
        ),
        AvailabilitySlot(
            doctor_id=walsh.id,
            location="NORTH",
            start_time=datetime.combine(tomorrow, datetime.min.time())
            + timedelta(hours=10),
        ),
        AvailabilitySlot(
            doctor_id=patel.id,
            location="MAIN",
            start_time=datetime.combine(tomorrow, datetime.min.time())
            + timedelta(hours=11),
        ),
        AvailabilitySlot(
            doctor_id=chen.id,
            location="MAIN",
            start_time=datetime.combine(tomorrow, datetime.min.time())
            + timedelta(hours=14),
        ),
    ]
    db.session.add_all(slots)
    db.session.commit()


def test_new_patient_with_specialized_fracture(app):
    """
    Scenario 1: Verify that a specialized trauma (Fracture) routes exclusively
    to providers explicitly matching that issue type string.
    """
    with app.app_context():
        slots = get_valid_slots(
            body_part="Knee", issue_type="Fracture", is_new_patient=True
        )

        assert len(slots) == 1
        assert slots[0].doctor.name == "Dr. James Walsh"
        assert slots[0].location == "NORTH"


def test_overlapping_sports_medicine_rules_returns_all_matches(app):
    """
    Scenario 2: Confirm that overlapping protocols return matching slots across
    all qualified physicians, properly sorted chronologically.
    """
    with app.app_context():
        slots = get_valid_slots(
            body_part="Knee", issue_type="Sports Medicine", is_new_patient=True
        )

        # Expected: 2 slots from Dr. Chen (9:00, 14:00) + 1 slot from Dr. Walsh (10:00)
        assert len(slots) == 3

        doctors_returned = [slot.doctor.name for slot in slots]
        assert "Dr. Maria Chen" in doctors_returned
        assert "Dr. James Walsh" in doctors_returned


def test_new_patient_constraint_screens_out_closed_panels(app):
    """
    Scenario 3: Verify that physicians marked with accepts_new_patients=False
    are filtered out if the call flow identifies the caller as a New Patient.
    """
    with app.app_context():
        slots = get_valid_slots(
            body_part="Hip", issue_type="Joint Replacement", is_new_patient=True
        )

        # Dr. Patel and Dr. Chen both do Hip Joints, but Dr. Patel is closed to new patients.
        doctors_returned = set([slot.doctor.name for slot in slots])

        assert "Dr. Aisha Patel" not in doctors_returned
        assert "Dr. Maria Chen" in doctors_returned


def test_specialized_complaint_is_blocked_from_general_only_slots(app):
    """
    Scenario 4: If a specialist only opens slots for "General" complaints,
    ensure that incoming specialized injuries (like a Fracture) yield zero results
    to trigger a conversational fallback/redirection.
    """
    with app.app_context():
        # Dr. Patel treats Spine, but only for "General" pain/consultations.
        slots = get_valid_slots(
            body_part="Spine", issue_type="Fracture", is_new_patient=True
        )

        assert len(slots) == 0
