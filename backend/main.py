# US-1.4: Appointment Booking Flow
# US-1.6: Appointment Cancellation Flow



from fastapi import FastAPI, HTTPException
from models import Appointment, BookingRequest, RescheduleRequest
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

# Default slots: 10:00 AM to 12:00 PM (3 slots, 1 hour each)
DEFAULT_SLOTS = ["10:00", "11:00", "12:00"]

available_slots = {
    "2026-01-20": ["10:00", "11:00", "12:00"],
    "2026-01-21": ["10:00", "11:00", "12:00"]
}

# -------- US-1.4 --------
@app.get("/slots")
def get_slots(date: str):
    return {
        "date": date,
        "available_slots": available_slots.get(date, DEFAULT_SLOTS.copy())
    }

@app.post("/book")
def book_appointment(data: BookingRequest):
    date = data.date
    time = data.time

    if date not in available_slots:
        available_slots[date] = DEFAULT_SLOTS.copy()

    if time not in available_slots.get(date, DEFAULT_SLOTS.copy()):
        raise HTTPException(status_code=409, detail="Slot not available")

    appointment = Appointment(
        id=len(appointments) + 1,
        patient_name=data.patient_name,
        doctor_name=data.doctor_name,
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

@app.get("/doctor-dashboard")
def get_doctor_dashboard(doctor_name: str = None):
    """Get appointments for a specific doctor or all appointments"""
    if doctor_name:
        doctor_appointments = [
            {
                "id": appt.id,
                "patient_name": appt.patient_name,
                "doctor_name": appt.doctor_name,
                "date": appt.date,
                "time": appt.time,
                "status": appt.status,
                "created_at": appt.created_at.isoformat()
            }
            for appt in appointments
            if appt.doctor_name == doctor_name
        ]
        return {
            "doctor_name": doctor_name,
            "appointments": doctor_appointments,
            "total": len(doctor_appointments)
        }
    else:
        all_appointments = [
            {
                "id": appt.id,
                "patient_name": appt.patient_name,
                "doctor_name": appt.doctor_name,
                "date": appt.date,
                "time": appt.time,
                "status": appt.status,
                "created_at": appt.created_at.isoformat()
            }
            for appt in appointments
        ]
        return {
            "appointments": all_appointments,
            "total": len(all_appointments)
        }




# -------- US-1.6 --------
@app.get("/appointment/{appointment_id}")
def get_appointment(appointment_id: int):
    """Get appointment details by ID"""
    for appt in appointments:
        if appt.id == appointment_id:
            return {
                "id": appt.id,
                "patient_name": appt.patient_name,
                "doctor_name": appt.doctor_name,
                "date": appt.date,
                "time": appt.time,
                "status": appt.status,
                "created_at": appt.created_at.isoformat()
            }
    
    raise HTTPException(status_code=404, detail="Appointment not found")

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

# -------- US-1.7: Appointment Rescheduling --------
@app.put("/reschedule/{appointment_id}")
def reschedule_appointment(appointment_id: int, data: RescheduleRequest):
    """Reschedule an appointment to a new date and time"""
    new_date = data.new_date
    new_time = data.new_time
    
    # Find the appointment
    appointment = None
    for appt in appointments:
        if appt.id == appointment_id:
            appointment = appt
            break
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    if appointment.status != "Booked":
        raise HTTPException(status_code=400, detail="Only booked appointments can be rescheduled")
    
    # Check if new slot is available
    if new_date not in available_slots:
        available_slots[new_date] = DEFAULT_SLOTS.copy()
    
    if new_time not in available_slots.get(new_date, []):
        raise HTTPException(status_code=409, detail="New time slot is not available")
    
    # Release the old time slot
    old_date = appointment.date
    old_time = appointment.time
    available_slots.setdefault(old_date, []).append(old_time)
    
    # Remove the new time slot from availability
    available_slots[new_date].remove(new_time)
    
    # Update the appointment
    appointment.date = new_date
    appointment.time = new_time
    
    # Notifications (simulated)
    print(f"EMAIL → Rescheduling confirmation sent to {appointment.patient_name}")
    print(f"NOTIFY → Doctor {appointment.doctor_name} notified of rescheduling")
    print(f"   Old: {old_date} at {old_time}")
    print(f"   New: {new_date} at {new_time}")
    
    return {
        "message": "Appointment rescheduled successfully",
        "appointment_id": appointment.id,
        "old_date": old_date,
        "old_time": old_time,
        "new_date": new_date,
        "new_time": new_time
    }
