from flask import Flask, request, jsonify
from api.models import db, Patient, Doctor, AvailabilitySlot, Appointment, CallLog
from api.routing_logic import get_valid_slots

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///scheduling.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


@app.route("/patients", methods=["POST"])
def handle_patient():
    data = request.json or {}
    name = data.get("name")
    dob = data.get("dob")

    if not name or not dob:
        return jsonify({"error": "Missing name or dob"}), 400

    patient = Patient.query.filter_by(name=name, dob=dob).first()

    if patient:
        return jsonify(
            {
                "id": patient.id,
                "name": patient.name,
                "dob": patient.dob,
                "is_new_patient": False,
            }
        ), 200

    new_patient = Patient(name=name, dob=dob, is_new_patient=True)

    return jsonify(
        {
            "id": new_patient.id,
            "name": new_patient.name,
            "dob": new_patient.dob,
            "is_new_patient": True,
        }
    ), 201


@app.route("/slots", methods=["GET"])
def get_slots():
    patient_id = request.args.get("patient_id")
    body_part = request.args.get("body_part")
    issue_type = request.args.get("issue_type")
    location = request.args.get("location")

    if not any([patient_id, body_part, issue_type]):
        return jsonify({"error": "Missing patient_id, body_part, or issue_type"}), 400

    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    slots = get_valid_slots(patient, body_part, issue_type, location)

    return jsonify([{
        "id": slot.id,
        "doctor_name": slot.doctor.name,
        "start_time": slot.start_time,
        "location": slot.location
    } for slot in slots]), 200

@app.route('/appointments', methods=['POST'])
def book_appointment():
    data = request.json or {}
    patient_id = data.get('patient_id')
    slot_id = data.get('slot_id')
    reason = data.get('reason', '')

    if not patient_id or not slot_id:
        return jsonify({"error": "Missing patient_id or slot_id"}), 400

    slot = AvailabilitySlot.query.get(slot_id)
    if not slot or slot.is_booked:
        return jsonify({"error": "Slot unavailable or does not exist"}), 400

    slot.is_booked = True
    appointment = Appointment(
        patient_id=patient_id,
        slot_id=slot_id,
        doctor_id=slot.doctor_id,
        reason=reason
    )

    db.session.add(appointment)
    db.session.commit()

    return jsonify({
        "appointment_id": appointment.id,
        "doctor_name": slot.doctor.name,
        "location": slot.location,
        "start_time": slot.start_time,
        "status": "confirmed"
    }), 201
