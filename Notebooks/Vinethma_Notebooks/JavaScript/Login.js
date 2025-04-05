// document.addEventListener("DOMContentLoaded", () => {
//     document.querySelector("form").addEventListener("submit", async (event) => {
//         event.preventDefault();
//
//         const email = document.getElementById("email").value;
//         const password = document.getElementById("password").value;
//
//         if (!email || !password) {
//             alert("Please fill in all fields.");
//             return;
//         }
//
//         try {
//             const response = await fetch("http://127.0.0.1:5000/login", {
//                 method: "POST",
//                 headers: {
//                     "Content-Type": "application/json",
//                 },
//                 body: JSON.stringify({ email, password }),
//             });
//
//             const result = await response.json();
//
//             if (response.ok) {
//                 alert("Login successful!");
//                 window.location.href = "Home.html"; // Redirect to the home page
//             } else {
//                 alert(result.error || "Invalid email or password.");
//             }
//         } catch (error) {
//             console.error("Error:", error);
//             alert("Error connecting to server.");
//         }
//     });
// });


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

                
 // Redirect to the home page

                // Store username in localStorage
                localStorage.setItem("username", result.username);

                window.location.href = "file:///C:/Users/sanje/OneDrive/Pictures/IIT%20FIRST%20YEAR/2%20year%20-2024/2603/HopeBridge/Notebooks/Isuri_Notebooks/Home.html"; // Redirect to home page

            } else {
                alert(result.error || "Invalid email or password.");
            }
        } catch (error) {
            console.error("Error:", error);
            alert("Error connecting to server.");
        }
    });
});