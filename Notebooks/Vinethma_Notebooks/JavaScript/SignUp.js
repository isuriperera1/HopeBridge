document.getElementById("signup-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const termsChecked = document.getElementById("terms").checked;
if (!termsChecked) {
    alert("You must agree to the Terms & Conditions.");
    return;
}


    const formData = {
        firstName: document.getElementById("first-name").value,
        lastName: document.getElementById("last-name").value,
        age: document.getElementById("age").value,
        gender: document.getElementById("gender").value,
        telephone: document.getElementById("telephone").value,
        dob: document.getElementById("dob").value,
        district: document.getElementById("district").value,
        email: document.getElementById("email").value,
        password: document.getElementById("password").value,
    };

    const confirmPassword = document.getElementById("confirm-password").value;

    if (formData.password !== confirmPassword) {
        alert("Passwords do not match!");
        return;
    }

    try {
        const response = await fetch("http://127.0.0.1:5000/signup", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(formData),
        });

        const result = await response.json();

        if (response.ok) {
            localStorage.setItem("user_id", formData.email); // Assuming email is used as user_id
            localStorage.setItem("district", formData.district);
            localStorage.setItem("username", formData.firstName);
            alert("User registered successfully!");
            window.location.href = "login.html"; // Redirect to login page
        } else {
            alert(result.error || "Signup failed");
        }
    } catch (error) {
        console.error("Error:", error);
        alert("Error connecting to server");
    }

});
