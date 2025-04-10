window.addEventListener("DOMContentLoaded", () => {
    const today = new Date().toISOString().split("T")[0];
    document.getElementById("date").setAttribute("min", today);
});

const Error_Message = document.getElementById("error-message");

const success_alert = document.getElementById("success-alert");
const success_message_main = document.getElementById("success-message-main");


document.getElementById("consultationForm").addEventListener("submit", function (event) {
    event.preventDefault();

    const date = document.getElementById("date").value;
    const time = document.getElementById("time").value;
    const topic = document.getElementById("topic").value;

    // Prevent submitting with a past date
    const selectedDate = new Date(date);
    const today = new Date();
    today.setHours(0, 0, 0, 0); // Normalize today's date

    if (selectedDate < today) {
        Error_Message.textContent = "Please choose a valid future date for your consultation.";
        Error_Message.removeAttribute("hidden");
        return;
    }

    fetch("/consultationsAPI", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            date: date,
            time: time,
            topic: topic
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById("consultationForm").reset();

                success_message_main.textContent = "Consultation scheduled successfully!";
                success_alert.removeAttribute("hidden");
            } else {
                Error_Message.textContent = "Failed to schedule consultation.";
                Error_Message.removeAttribute("hidden");
            }
        })
        .catch(error => {
            console.error("Error:", error);
            Error_Message.textContent = "An error occurred while scheduling the consultation, Please try again.";
            Error_Message.removeAttribute("hidden");
        });
});