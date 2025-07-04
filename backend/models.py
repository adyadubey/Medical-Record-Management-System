from sqlalchemy import Column, Integer, String, Float, Date, Text, ForeignKey
from sqlalchemy.orm import declarative_base
from pgvector.sqlalchemy import Vector

Base = declarative_base()

class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    gender = Column(String(10))
    height_cm = Column(Float)
    weight_kg = Column(Float)
    bmi = Column(Float)
    medical_history = Column(Text)
    medical_history_embedding = Column(Vector(384))

class Doctor(Base):
    __tablename__ = "doctors"
    doctor_id = Column(Integer, primary_key=True)
    doctor_name = Column(String(100))
    specialty = Column(String(100))
    specialty_embedding = Column(Vector(384))

class Appointment(Base):
    __tablename__ = "appointments"
    patient_id = Column(Integer, ForeignKey("patients.id"), primary_key=True)
    doctor_id = Column(Integer, ForeignKey("doctors.doctor_id"), primary_key=True)
    appointment_date = Column(Date, primary_key=True)

class Prescription(Base):
    __tablename__ = "prescriptions"
    patient_id = Column(Integer, ForeignKey("patients.id"), primary_key=True)
    doctor_id = Column(Integer, ForeignKey("doctors.doctor_id"), primary_key=True)
    date = Column(Date, primary_key=True)
    diagnosis = Column(Text)
    diagnosis_embedding = Column(Vector(384))
    medicine_prescribed = Column(Text)
