import pytest
from flask import Flask
from datetime import datetime, timedelta
from app import app as flask_app, db
from api.models import Appointment, Patient, Doctor, PhysicianProtocol, AvailabilitySlot


@pytest.fixture(scope="session")
def app():
    """Creates a mock Flask application instance configured with an in-memory database."""
    flask_app.config["TESTING"] = True
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    return app.test_client()


@pytest.fixture(scope="function", autouse=True)
def clean_db_tables(app):
    with app.app_context():
        db.session.query(Appointment).delete()
        db.session.query(AvailabilitySlot).delete()
        db.session.query(PhysicianProtocol).delete()
        db.session.query(Patient).delete()
        db.session.query(Doctor).delete()
        db.session.commit()


def _seed_api_test_data():
    chen = Doctor(name="Dr. Maria Chen", accepts_new_patients=True)
    db.session.add(chen)
    db.session.commit()

    protocol = PhysicianProtocol(
        doctor_id=chen.id, body_part="Knee", issue_type="Sports Medicine"
    )
    db.session.add(protocol)

    tomorrow = datetime.utcnow().date() + timedelta(days=1)
    slot = AvailabilitySlot(
        id=101,
        doctor_id=chen.id,
        location="MAIN",
        start_time=datetime.combine(tomorrow, datetime.min.time()) + timedelta(hours=9),
        is_booked=False,
    )
    db.session.add(slot)
    db.session.commit()
    return chen


def test_create_new_patient_endpoint(client):
    """Validates that a unique name and DOB successfully creates a new patient."""
    payload = {"name": "Alice Smith", "dob": "1988-11-23"}
    response = client.post("/patients", json=payload)

    assert response.status_code == 201
    data = response.get_json()
    assert data["name"] == "Alice Smith"
    assert data["is_new_patient"] is True
    assert "id" in data


def test_lookup_existing_patient_endpoint(client, app):
    """Ensures existing patients are looked up gracefully instead of recreated."""
    with app.app_context():
        existing = Patient(name="Bob Jones", dob="1975-04-12", is_new_patient=False)
        db.session.add(existing)
        db.session.commit()

    payload = {"name": "Bob Jones", "dob": "1975-04-12"}
    response = client.post("/patients", json=payload)

    assert response.status_code == 200
    data = response.get_json()
    assert data["is_new_patient"] is False


def test_get_slots_success(client, app):
    """Validates retrieval of matched slots when the patient parameters match protocols."""
    _seed_api_test_data()
    with app.app_context():
        p = Patient(name="Test Patient", dob="1990-01-01", is_new_patient=True)
        db.session.add(p)
        db.session.commit()
        p_id = p.id

    response = client.get(
        f"/slots?patient_id={p_id}&body_part=Knee&issue_type=Sports+Medicine"
    )
    assert response.status_code == 200
    slots = response.get_json()
    assert len(slots) == 1
    assert slots[0]["doctor_name"] == "Dr. Maria Chen"
    assert slots[0]["location"] == "MAIN"


def test_book_appointment_atomic_success(client, app):
    """Verifies successful booking atomically marks the selected slot as taken."""
    _seed_api_test_data()
    with app.app_context():
        p = Patient(name="Test Patient", dob="1990-01-01", is_new_patient=True)
        db.session.add(p)
        db.session.commit()
        p_id = p.id

    booking_payload = {"patient_id": p_id, "slot_id": 101, "reason": "Torn meniscus"}
    response = client.post("/appointments", json=booking_payload)
    
    assert response.status_code == 201
    data = response.get_json()
    assert data["status"] == "confirmed"

    # Confirm the slot is now locked down and marked as booked
    with app.app_context():
        slot = AvailabilitySlot.query.get(101)
        assert slot.is_booked is True


def test_get_patient_appointments(client, app):
    """Confirms retrieval of all current appointments mapped under a target patient's profile."""
    doc = _seed_api_test_data()
    with app.app_context():
        p = Patient(name="Test Patient", dob="1990-01-01", is_new_patient=True)
        db.session.add(p)
        db.session.commit()
        
        # Manually link an appointment to history
        appt = Appointment(patient_id=p.id, slot_id=101, doctor_id=doc.id, reason="Checkup")
        db.session.add(appt)
        db.session.commit()
        p_id = p.id

    response = client.get(f"/appointments/{p_id}")
    assert response.status_code == 200
    appointments = response.get_json()
    assert len(appointments) == 1
    assert appointments[0]["reason"] == "Checkup"
