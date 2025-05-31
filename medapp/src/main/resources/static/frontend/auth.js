document.addEventListener("DOMContentLoaded", () => {
    const loginBtn = document.getElementById("login-btn");
    const registerBtn = document.getElementById("register-btn");
    const loginForm = document.getElementById("login-form");
    const registerForm = document.getElementById("register-form");
    const authOptions = document.getElementById("auth-options");
    const errorBlock = document.getElementById("auth-error");

    const submitLogin = document.getElementById("submit-login");
    const submitRegister = document.getElementById("submit-register");

    loginBtn.addEventListener("click", () => {
        loginForm.classList.remove("hidden");
        authOptions.classList.add("hidden");
        errorBlock.classList.add("hidden");
    });

    registerBtn.addEventListener("click", () => {
        registerForm.classList.remove("hidden");
        authOptions.classList.add("hidden");
        errorBlock.classList.add("hidden");
    });

    document.getElementById("back-from-login").addEventListener("click", () => {
        loginForm.classList.add("hidden");
        authOptions.classList.remove("hidden");
        errorBlock.classList.add("hidden");
    });

    document.getElementById("back-from-register").addEventListener("click", () => {
        registerForm.classList.add("hidden");
        authOptions.classList.remove("hidden");
        errorBlock.classList.add("hidden");
    });

    const checkLoginFields = () => {
        const identifier = document.getElementById("login-identifier").value.trim();
        const password = document.getElementById("login-password").value.trim();
        submitLogin.disabled = !(identifier && password);
        submitLogin.className = submitLogin.disabled ? "bg-gray-400 text-white px-4 py-2 rounded cursor-not-allowed" :
            "bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded";
    };

    const checkRegisterFields = () => {
        const fields = ["reg-fullname", "reg-email", "reg-password", "reg-confirm", "reg-code"];
        const filled = fields.every(id => document.getElementById(id).value.trim());
        submitRegister.disabled = !filled;
        submitRegister.className = submitRegister.disabled ? "bg-gray-400 text-white px-4 py-2 rounded cursor-not-allowed" :
            "bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded";
    };

    document.querySelectorAll("#login-form input").forEach(el => el.addEventListener("input", checkLoginFields));
    document.querySelectorAll("#register-form input").forEach(el => el.addEventListener("input", checkRegisterFields));

    submitLogin.addEventListener("click", async (e) => {
        e.preventDefault();
        errorBlock.classList.add("hidden");

        const payload = {
            emailOrName: document.getElementById("login-identifier").value,
            password: document.getElementById("login-password").value
        };

        const res = await fetch("/auth/login", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(payload)
        });

        if (res.ok) {
            window.location.href = "/frontend/index.html";
        } else {
            errorBlock.textContent = "Ошибка входа: неверные данные.";
            errorBlock.classList.remove("hidden");
        }
    });

    submitRegister.addEventListener("click", async (e) => {
        e.preventDefault();
        errorBlock.classList.add("hidden");

        const payload = {
            fullName: document.getElementById("reg-fullname").value,
            email: document.getElementById("reg-email").value,
            password: document.getElementById("reg-password").value,
            confirmPassword: document.getElementById("reg-confirm").value,
            secretCode: document.getElementById("reg-code").value
        };

        const res = await fetch("/auth/register", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(payload)
        });

        if (res.ok) {
            window.location.href = "/frontend/index.html";
        } else {
            const text = await res.text();
            errorBlock.textContent = "Ошибка регистрации: " + text;
            errorBlock.classList.remove("hidden");
        }
    });
});
