/* =========================================
   ZAMBRE AGENCIES - USER PANEL JS
   REGISTER FORM
========================================= */

document.addEventListener("DOMContentLoaded", function () {

    const registerForm = document.querySelector(
        'form[action*="registersave"]'
    );

    if (!registerForm) {
        return;
    }

    const fullname = registerForm.querySelector('[name="fullname"]');
    const email = registerForm.querySelector('[name="email"]');
    const password = registerForm.querySelector('[name="password"]');
    const contact = registerForm.querySelector('[name="contact"]');
    const city = registerForm.querySelector('[name="city"]');

    // Validate form before submitting
    registerForm.addEventListener("submit", function (event) {

        // Clear old custom messages
        [fullname, email, password, contact, city].forEach(function (field) {
            if (field) {
                field.setCustomValidity("");
            }
        });

        if (fullname && fullname.value.trim() === "") {
            fullname.setCustomValidity("Please enter your full name.");
        } else if (email && email.value.trim() === "") {
            email.setCustomValidity("Please enter your email address.");
        } else if (password && password.value.length < 8) {
            password.setCustomValidity(
                "Password must contain at least 8 characters."
            );
        } else if (
            contact &&
            !/^[0-9]{10}$/.test(contact.value.trim())
        ) {
            contact.setCustomValidity(
                "Please enter a valid 10-digit mobile number."
            );
        } else if (city && city.value.trim() === "") {
            city.setCustomValidity("Please enter your city.");
        }

        if (!registerForm.checkValidity()) {
            event.preventDefault();
            registerForm.reportValidity();
        }
    });

    // Clear custom validation messages while typing
    registerForm.querySelectorAll("input").forEach(function (input) {
        input.addEventListener("input", function () {
            input.setCustomValidity("");
        });
    });

});
/* =========================================
   ZAMBRE AGENCIES - LOGIN JS
========================================= */

document.addEventListener("DOMContentLoaded", function () {

    // Login form
    const loginForm = document.querySelector(
        'form[action*="logincheck"]'
    );

    if (!loginForm) {
        return;
    }

    const email = loginForm.querySelector('[name="email"]');
    const password = loginForm.querySelector('[name="password"]');

    // Validate login form
    loginForm.addEventListener("submit", function (event) {

        // Clear previous validation messages
        email.setCustomValidity("");
        password.setCustomValidity("");

        // Email validation
        if (email.value.trim() === "") {
            email.setCustomValidity("Please enter your email address.");
        }

        // Password validation
        else if (password.value.trim() === "") {
            password.setCustomValidity("Please enter your password.");
        }

        // Display validation message
        if (!loginForm.checkValidity()) {
            event.preventDefault();
            loginForm.reportValidity();
        }
    });

    // Clear validation messages while typing
    email.addEventListener("input", function () {
        email.setCustomValidity("");
    });

    password.addEventListener("input", function () {
        password.setCustomValidity("");
    });

});
/* =========================================
   ZAMBRE AGENCIES - USER DASHBOARD JS
========================================= */

document.addEventListener("DOMContentLoaded", function () {

    const sidebar = document.getElementById("userSidebar");
    const toggleButton = document.getElementById("sidebarToggle");
    const overlay = document.getElementById("sidebarOverlay");
    const logoutButton = document.getElementById("userLogoutBtn");

    function openSidebar() {
        if (!sidebar || !toggleButton || !overlay) return;

        sidebar.classList.add("sidebar-open");
        overlay.classList.add("overlay-visible");
        toggleButton.setAttribute("aria-expanded", "true");
    }

    function closeSidebar() {
        if (!sidebar || !toggleButton || !overlay) return;

        sidebar.classList.remove("sidebar-open");
        overlay.classList.remove("overlay-visible");
        toggleButton.setAttribute("aria-expanded", "false");
    }

    if (toggleButton) {
        toggleButton.addEventListener("click", function () {
            if (sidebar.classList.contains("sidebar-open")) {
                closeSidebar();
            } else {
                openSidebar();
            }
        });
    }

    if (overlay) {
        overlay.addEventListener("click", closeSidebar);
    }

    document.querySelectorAll(".dashboard-menu-link").forEach(function (link) {
        link.addEventListener("click", function () {
            if (window.innerWidth <= 1050) {
                closeSidebar();
            }
        });
    });

    if (logoutButton) {
        logoutButton.addEventListener("click", function (event) {
            const confirmed = confirm(
                "Are you sure you want to logout?"
            );

            if (!confirmed) {
                event.preventDefault();
            }
        });
    }

});
/* =========================================
   ZAMBRE AGENCIES - PRODUCTS JAVASCRIPT
========================================= */

document.addEventListener("DOMContentLoaded", function () {

    // Add to Cart form submission
    const cartForms = document.querySelectorAll(".product-cart-form");

    cartForms.forEach(function (form) {

        form.addEventListener("submit", function () {

            const button = form.querySelector(".add-to-cart-btn");

            if (!button || button.disabled) {
                return;
            }

            // Prevent repeated clicks
            button.disabled = true;

            // Show loading text
            button.textContent = "Adding to Cart...";

        });

    });

    // Smooth horizontal category navigation
    const categoryRow = document.querySelector(
        ".product-categories-strip"
    );

    if (categoryRow) {
        categoryRow.style.scrollBehavior = "smooth";
    }

});
/* =========================================
   ZAMBRE AGENCIES - CART JAVASCRIPT
========================================= */

document.addEventListener("DOMContentLoaded", function () {

    // Confirm before removing a product
    const removeForms = document.querySelectorAll(
        'form[action*="/remove_from_cart/"]'
    );

    removeForms.forEach(function (form) {

        form.addEventListener("submit", function (event) {

            const confirmed = window.confirm(
                "Are you sure you want to remove this product from your cart?"
            );

            if (!confirmed) {
                event.preventDefault();
            }

        });

    });

    // Prevent repeated checkout clicks if checkout is enabled later
    const checkoutButton = document.querySelector(".checkout-btn");

    if (checkoutButton) {

        checkoutButton.addEventListener("click", function () {

            if (checkoutButton.disabled) {
                return;
            }

            // checkoutButton.disabled = true;
            // checkoutButton.textContent = "Processing...";

        });

    }

});
// =====================================
// MY ORDERS - SIDEBAR + DASHBOARD CARD
// =====================================

document.addEventListener("DOMContentLoaded", function () {

    const ordersUrl = "/my_orders";

    // Find My Orders link in the sidebar
    const sidebarLinks = document.querySelectorAll(
        ".dashboard-menu-link"
    );

    sidebarLinks.forEach(function (link) {

        const linkText = link.textContent
            .replace(/\s+/g, " ")
            .trim()
            .toLowerCase();

        if (linkText.includes("my orders")) {

            if (link.tagName.toLowerCase() === "a") {
                link.setAttribute("href", ordersUrl);
            }

            link.addEventListener("click", function (event) {
                event.preventDefault();
                window.location.assign(ordersUrl);
            });

        }
    });


    // Find My Orders card on the dashboard
    const dashboardCards = document.querySelectorAll(
        ".dashboard-card"
    );

    dashboardCards.forEach(function (card) {

        const heading = card.querySelector("h3");

        if (
            heading &&
            heading.textContent.trim().toLowerCase() === "my orders"
        ) {

            if (card.tagName.toLowerCase() === "a") {
                card.setAttribute("href", ordersUrl);
            }

            card.addEventListener("click", function (event) {

                // Allow navigation only when this card is selected
                event.preventDefault();
                window.location.assign(ordersUrl);

            });

            // Keyboard accessibility
            if (card.tagName.toLowerCase() !== "a") {

                card.setAttribute("role", "link");
                card.setAttribute("tabindex", "0");

                card.addEventListener("keydown", function (event) {

                    if (event.key === "Enter" || event.key === " ") {
                        event.preventDefault();
                        window.location.assign(ordersUrl);
                    }

                });

            }

        }
    });

});