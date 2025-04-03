
// Login validation function
function loginUser() {
    const email = document.getElementById("Email").value;
    const password = document.getElementById("Password").value;
    const remember = document.getElementById("flexCheckChecked").checked;

    // Basic validation: check if email or password is empty
    if (!email || !password) {
        document.getElementById("error-message").removeAttribute("hidden");
        document.getElementById("error-message").innerText = "Please fill in both email and password.";
        return;
    }

    fetch("/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, remember })
    })
        .then(response => response.json()) // Expecting JSON response
        .then(data => {
            if (data.success) {
                window.location.href = "/home"; // Redirect on success
            } else {
                document.getElementById("error-message").removeAttribute("hidden");
                document.getElementById("error-message").innerText = data.error; // Show error
            }
        })
        .catch(error => {
            console.error("Error:", error);
        });
}

// Register validation function
function registerUser() {
    const email = document.getElementById("RegisterEmail").value;
    const password = document.getElementById("RegisterPassword").value;
    const confirmPassword = document.getElementById("confirmPassword").value;
    const name = document.getElementById("name").value;

    // Basic validation: check if any field is empty
    if (!email || !password || !confirmPassword || !name) {
        document.getElementById("error-message").removeAttribute("hidden");
        document.getElementById("error-message").innerText = "Please fill in all fields.";
        return;
    }

    // Check if passwords match
    if (password !== confirmPassword) {
        document.getElementById("error-message").removeAttribute("hidden");
        document.getElementById("error-message").innerText = "Passwords do not match.";
        return;
    }

    fetch("/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, confirmPassword, name })
    })
        .then(response => response.json()) // Expecting JSON response
        .then(data => {
            if (data.success) {
                window.location.href = "/home"; // Redirect on success
            } else {
                document.getElementById("error-message").removeAttribute("hidden");
                document.getElementById("error-message").innerText = data.error; // Show error
            }
        })
        .catch(error => {
            console.error("Error:", error);
        });
}

// Switch to Register form
function ShowRegisterForm() {
    document.getElementById("LoginForm").setAttribute("hidden", "");
    document.getElementById("RegisterForm").removeAttribute("hidden");
    document.getElementById("ResetPasswordForm").setAttribute("hidden", "");
    document.getElementById("error-message").setAttribute("hidden", "");
}

// Switch to Login form
function ShowLoginForm() {
    document.getElementById("LoginForm").removeAttribute("hidden");
    document.getElementById("RegisterForm").setAttribute("hidden", "");
    document.getElementById("ResetPasswordForm").setAttribute("hidden", "");
    document.getElementById("error-message").setAttribute("hidden", "");
}

// Switch to Reset Password form
function ShowRestPasswordForm() {
    document.getElementById("LoginForm").setAttribute("hidden", "");
    document.getElementById("ResetPasswordForm").removeAttribute("hidden");
    document.getElementById("error-message").setAttribute("hidden", "");
}
