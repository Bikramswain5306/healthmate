function book() {
    const patient = document.getElementById("patient").value;
    const doctor = document.getElementById("doctor").value;
    const date = document.getElementById("date").value;
    const time = document.getElementById("time").value;

    fetch("http://127.0.0.1:8000/book", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            patient_name: patient,
            doctor_name: doctor,
            date: date,
            time: time
        })
    })
        .then(async res => {
            const data = await res.json();

            if (!res.ok) {
                alert(data.detail);   // e.g. "Slot not available"
                return null;          // IMPORTANT
            }

            return data;            // <<< THIS WAS MISSING
        })
        .then(data => {
            if (!data) return;
            alert("Booked with ID: " + data.appointment_id);
        })
        .catch(err => {
            console.error(err);
            alert("Server error");
        });
}
