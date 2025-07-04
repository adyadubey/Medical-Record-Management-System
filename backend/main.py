from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from database import engine, SessionLocal, get_db
from models import Base, Patient, Appointment, Prescription, Doctor
from schemas import PatientCreate, PatientUpdate, PatientRead
from loaders import load_all_data
from sentence_transformers import SentenceTransformer
import openai
import logging
from dotenv import load_dotenv
import os
from embeddings import embed

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize app
app = FastAPI()

# Allow CORS (for frontend communication)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend domain in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging setup
logging.basicConfig(level=logging.INFO)

# Load sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Create tables & load data on startup
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    load_all_data(session)
    session.close()

@app.get("/")
def root():
    return {"message": "Vector DB initialized and all data loaded successfully."}

# ========== Patient Routes ==========

@app.get("/patients", response_model=List[PatientRead])
def get_patients(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Patient).offset(skip).limit(limit).all()

@app.get("/patient/{patient_id}", response_model=PatientRead)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@app.post("/patient", response_model=PatientRead)
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    db_patient = Patient(**patient.dict())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

@app.put("/patient/{patient_id}", response_model=PatientRead)
def update_patient(patient_id: int, updated: PatientUpdate, db: Session = Depends(get_db)):
    db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    for key, value in updated.dict(exclude_unset=True).items():
        setattr(db_patient, key, value)
    db.commit()
    db.refresh(db_patient)
    return db_patient

# ========== Appointment Info ==========

@app.get("/appointment_info/{patient_id}")
def get_appointment_info(patient_id: int, db: Session = Depends(get_db)):
    appointments = db.query(Appointment).filter_by(patient_id=patient_id).all()
    if not appointments:
        raise HTTPException(status_code=404, detail="No appointments found for this patient")

    results = []
    for appointment in appointments:
        doctor = db.query(Doctor).filter_by(doctor_id=appointment.doctor_id).first()
        doctor_name = doctor.doctor_name if doctor else "Unknown Doctor"

        prescription = db.query(Prescription).filter_by(
            patient_id=appointment.patient_id,
            doctor_id=appointment.doctor_id,
            date=appointment.appointment_date
        ).first()

        results.append({
            "doctor_name": doctor_name,
            "appointment_date": appointment.appointment_date,
            "diagnosis": prescription.diagnosis if prescription else "Not available",
            "medicine_prescribed": prescription.medicine_prescribed if prescription else "Not available"
        })

    return {
        "patient_id": patient_id,
        "appointments": results
    }

# ========== Semantic Search ==========

@app.post("/search")
def semantic_search(query: str, top_k: int = 5, db: Session = Depends(get_db)):
    try:
        embedding = embed(query)
        sql = text("""
            SELECT id, name, gender, height_cm, weight_kg, bmi, medical_history,
                   medical_history_embedding <=> (:embedding)::vector AS distance
            FROM patients
            ORDER BY distance
            LIMIT :top_k;
        """)

        results = db.execute(sql, {"embedding": embedding, "top_k": top_k}).fetchall()

        return [
            {
                "id": id_,
                "name": name,
                "gender": gender,
                "height_cm": height_cm,
                "weight_kg": weight_kg,
                "bmi": bmi,
                "medical_history": history,
                "similarity_score": round(1 - distance, 4)
            }
            for id_, name, gender, height_cm, weight_kg, bmi, history, distance in results
        ]

    except Exception:
        logging.error("Embedding search failed", exc_info=True)
        raise HTTPException(status_code=500, detail="Semantic search failed")
