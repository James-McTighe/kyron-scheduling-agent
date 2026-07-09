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

