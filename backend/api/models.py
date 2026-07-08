from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Patient(db.Model):
    __tablename__ = 'patients'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.String(20), nullable=False)  # Format: YYYY-MM-DD
    is_new_patient = db.Column(db.Boolean, default=True)

class Doctor(db.Model):
    __tablename__ = 'doctors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    accepts_new_patients = db.Column(db.Boolean, default=True)

class PhysicianProtocol(db.Model):
    __tablename__ = 'physician_protocols'
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    body_part = db.Column(db.String(50), nullable=False)      # e.g., 'Knee', 'Hip'
    issue_type = db.Column(db.String(50), nullable=False)     # e.g., 'Fracture', 'Sports Medicine', 'General'
    
    doctor = db.relationship('Doctor', backref=db.backref('protocols', lazy=True))

class AvailabilitySlot(db.Model):
    __tablename__ = 'availability_slots'
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(20), nullable=False)        # 'MAIN', 'NORTH', 'WEST'
    is_booked = db.Column(db.Boolean, default=False)

    doctor = db.relationship('Doctor', backref=db.backref('slots', lazy=True))

class Appointment(db.Model):
    __tablename__ = 'appointments'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    slot_id = db.Column(db.Integer, db.ForeignKey('availability_slots.id'), unique=True, nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    reason = db.Column(db.String(200), nullable=False)

class CallLog(db.Model):
    __tablename__ = 'call_logs'
    id = db.Column(db.Integer, primary_key=True)
    transcript = db.Column(db.Text, nullable=True)
    booking_status = db.Column(db.String(50), default='abandoned') # scheduled, abandoned, redirected, failed
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=True)
