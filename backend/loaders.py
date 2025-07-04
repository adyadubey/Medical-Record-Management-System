import pandas as pd
from sqlalchemy.orm import Session
from models import Patient, Doctor, Appointment, Prescription
from database import SessionLocal
from embeddings import embed  


def load_patients(session: Session):
    df = pd.read_excel("patients_with_random_names.xlsx")
    for _, row in df.iterrows():
        session.merge(Patient(
            id=row["ID"],
            name=row["Name"],
            gender=row["Gender"],
            height_cm=row["Height (cm)"],
            weight_kg=row["Weight (kg)"],
            bmi=row["BMI"],
            medical_history=row["Medical History"],
            medical_history_embedding=embed(str(row["Medical History"]))
        ))

def load_doctors(session: Session):
    df = pd.read_excel("doctors_with_random_names.xlsx")
    for _, row in df.iterrows():
        session.merge(Doctor(
            doctor_id=row["Doctor ID"],
            doctor_name=row["Doctor Name"],
            specialty=row["Specialty"],
            specialty_embedding=embed(str(row["Specialty"]))
        ))

def load_appointments(session: Session):
    df = pd.read_excel("appointments (4).xlsx")
    for _, row in df.iterrows():
        session.merge(Appointment(
            patient_id=row["Patient ID"],
            doctor_id=row["Doctor ID"],
            appointment_date=row["Appointment Date"]
        ))

def load_prescriptions(session: Session):
    df = pd.read_excel("prescriptions (1).xlsx")
    for _, row in df.iterrows():
        session.merge(Prescription(
            patient_id=row["Patient ID"],
            doctor_id=row["Doctor ID"],
            date=row["Date"],
            diagnosis=row["Diagnosis"],
            diagnosis_embedding=embed(str(row["Diagnosis"])),
            medicine_prescribed=row["Medicine Prescribed"]
        ))

def load_all_data(session: Session):
    load_patients(session)
    load_doctors(session)
    load_appointments(session)
    load_prescriptions(session)
