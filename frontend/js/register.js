const API = "http://127.0.0.1:8000";

const form = document.getElementById("registerForm");
const roleInput = document.getElementById("role");
const message = document.getElementById("message");


/* =========================================================
   ROLE SELECTION
   ========================================================= */

document.querySelectorAll(".role").forEach(btn => {

    btn.addEventListener("click", () => {

        document.querySelectorAll(".role").forEach(b => {
            b.classList.remove("active");
        });

        btn.classList.add("active");

        roleInput.value = btn.dataset.role;

    });

});


/* =========================================================
   REGISTER
   ========================================================= */

form.addEventListener("submit", async (e) => {

    e.preventDefault();


    message.className = "message";
    message.textContent = "";


    const username =
        document.getElementById("username")
            .value
            .trim();


    const email =
        document.getElementById("email")
            .value
            .trim();


    const password =
        document.getElementById("password")
            .value;


    const confirmPassword =
        document.getElementById("confirmPassword")
            .value;


    const role =
        roleInput.value;


    /* =====================================================
       VALIDATION
       ===================================================== */

    if (!username) {

        showError("Please enter username.");

        return;
    }


    if (!email) {

        showError("Please enter email.");

        return;
    }


    if (!password) {

        showError("Please enter password.");

        return;
    }


    if (password !== confirmPassword) {

        showError(
            "Passwords do not match."
        );

        return;
    }


    if (
        role !== "user" &&
        role !== "admin"
    ) {

        showError(
            "Please select a role."
        );

        return;
    }


    /* =====================================================
       BUTTON
       ===================================================== */

    const button =
        form.querySelector(
            ".submit-btn"
        );


    button.disabled = true;

    button.textContent =
        "Creating...";


    try {

        /* =================================================
           API REQUEST
           ================================================= */

        const response =
            await fetch(
                `${API}/api/auth/register`,
                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body:
                        JSON.stringify({

                            username:
                                username,

                            email:
                                email,

                            password:
                                password,

                            confirm_password:
                                confirmPassword,

                            role:
                                role

                        })

                }
            );


        /* =================================================
           RESPONSE
           ================================================= */

        const data =
            await response.json();


        console.log(
            "Register response:",
            data
        );


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Registration failed."
            );

        }


        /* =================================================
           CHECK USER DATA
           ================================================= */

        if (
            !data.user ||
            !data.user.username ||
            !data.user.email ||
            !data.user.role
        ) {

            throw new Error(
                "Server did not return valid user session data."
            );

        }


        /* =================================================
           SAVE LOGIN SESSION
           ================================================= */

        const sessionUser = {

            username:
                data.user.username,

            email:
                data.user.email,

            role:
                data.user.role

        };


        localStorage.setItem(
            "ai_cp_user",
            JSON.stringify(
                sessionUser
            )
        );


        console.log(
            "Saved session:",
            sessionUser
        );


        /* =================================================
           SUCCESS
           ================================================= */

        message.className =
            "message success";


        message.textContent =
            data.message ||
            "Registration successful.";


        /* =================================================
           REDIRECT
           ================================================= */

        setTimeout(() => {

            if (
                sessionUser.role ===
                "admin"
            ) {

                window.location.href =
                    "admin_dashboard.html";

            }

            else {

                window.location.href =
                    "user_dashboard.html";

            }

        }, 500);


    }

    catch (error) {

        console.error(
            "Registration error:",
            error
        );


        showError(
            error.message
        );

    }

    finally {

        button.disabled =
            false;

        button.textContent =
            "Create Account";

    }

});


/* =========================================================
   ERROR FUNCTION
   ========================================================= */

function showError(text) {

    message.className =
        "message error";

    message.textContent =
        text;

}