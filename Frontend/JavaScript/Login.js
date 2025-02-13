document.addEventListener("DOMContentLoaded", () => {
    document.querySelector("form").addEventListener("submit", async (event) => {
        event.preventDefault();

        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;

        if (!email || !password) {
            alert("Please fill in all fields.");
            return;
        }

        try {
            const response = await fetch("http://127.0.0.1:5000/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ email, password }),
            });

            const result = await response.json();

            if (response.ok) {
                alert("Login successful!");
                window.location.href = "Home.html"; // Redirect to the home page
            } else {
                alert(result.error || "Invalid email or password.");
            }
        } catch (error) {
            console.error("Error:", error);
            alert("Error connecting to server.");
        }
    });
});
