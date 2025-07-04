from pydantic import BaseModel
from typing import Optional, List
from datetime import date



class PatientBase(BaseModel):
    name: str
    gender: str
    height_cm: float
    weight_kg: float
    bmi: float
    medical_history: Optional[str] = None


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    name: Optional[str]
    gender: Optional[str]
    height_cm: Optional[float]
    weight_kg: Optional[float]
    bmi: Optional[float]
    medical_history: Optional[str]


class PatientRead(PatientBase):
    id: int

    class Config:
        orm_mode = True




class DoctorBase(BaseModel):
    doctor_name: str
    specialty: str


class DoctorCreate(DoctorBase):
    pass


class DoctorRead(DoctorBase):
    doctor_id: int

    class Config:
        orm_mode = True


class AppointmentBase(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_date: date


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentRead(AppointmentBase):
    class Config:
        orm_mode = True




class PrescriptionBase(BaseModel):
    patient_id: int
    doctor_id: int
    date: date
    diagnosis: Optional[str] = None
    medicine_prescribed: Optional[str] = None


class PrescriptionCreate(PrescriptionBase):
    pass


class PrescriptionRead(PrescriptionBase):
    class Config:
        orm_mode = True
