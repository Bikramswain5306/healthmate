from fastapi import FastAPI, HTTPException
from models import Appointment
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

appointments = []
appointment_history = []

available_slots = {
    "2026-01-20": ["10:00", "11:00", "12:00"],
    "2026-01-21": ["09:00", "10:30", "14:00"]
}

# -------- US-1.4 --------
@app.get("/slots")
def get_slots(date: str):
    return {
        "date": date,
        "available_slots": available_slots.get(date, [])
    }

@app.post("/book")
def book_appointment(data: dict):
    date = data["date"]
    time = data["time"]

    if date not in available_slots:
        available_slots[date] = ["09:00", "10:00", "11:00", "12:00"]

    if time not in available_slots.get(date, []):
        raise HTTPException(status_code=409, detail="Slot not available")

    appointment = Appointment(
        id=len(appointments) + 1,
        patient_name=data["patient_name"],
        doctor_name=data["doctor_name"],
        date=date,
        time=time,
        status="Booked",
        created_at=datetime.now()
    )

    available_slots[date].remove(time)
    appointments.append(appointment)

    print(f"EMAIL → Booking confirmation sent to {appointment.patient_name}")

    return {
        "message": "Appointment booked successfully",
        "appointment_id": appointment.id
    }




# -------- US-1.6 --------
@app.delete("/cancel/{appointment_id}")
def cancel_appointment(appointment_id: int):
    for appt in appointments:
        if appt.id == appointment_id:
            appointments.remove(appt)

            # Update history
            appointment_history.append({
                "id": appt.id,
                "patient_name": appt.patient_name,
                "doctor_name": appt.doctor_name,
                "date": appt.date,
                "time": appt.time,
                "status": "Cancelled",
                "cancelled_at": datetime.now()
            })

            # Release slot
            available_slots.setdefault(appt.date, []).append(appt.time)

            # Notifications (simulated)
            print(f"NOTIFY → Doctor {appt.doctor_name} notified of cancellation")
            print(f"EMAIL → Cancellation confirmation sent to {appt.patient_name}")

            return {
                "message": "Appointment cancelled successfully",
                "appointment_id": appt.id
            }

    raise HTTPException(status_code=404, detail="Appointment not found")

