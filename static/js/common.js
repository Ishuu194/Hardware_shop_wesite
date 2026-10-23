/* =========================================
   ZAMBRE AGENCIES - COMMON JS
   NAVBAR + SEARCH
========================================= */

document.addEventListener("DOMContentLoaded", function () {

    // Navbar content
    const navbarContent = document.getElementById("userNavbarContent");

    // Highlight active navbar link
    const currentPath = window.location.pathname;

    document.querySelectorAll(".user-nav-link").forEach(function (link) {

        link.classList.remove("active");

        const linkPath = new URL(
            link.href,
            window.location.origin
        ).pathname;

        if (linkPath === currentPath) {
            link.classList.add("active");
        }
    });

    // Close mobile menu after clicking a link
    document.querySelectorAll(
        ".user-nav-link, .user-profile-menu .dropdown-item"
    ).forEach(function (link) {

        link.addEventListener("click", function () {

            if (
                navbarContent &&
                navbarContent.classList.contains("show") &&
                window.innerWidth < 1200 &&
                typeof bootstrap !== "undefined"
            ) {
                const collapse =
                    bootstrap.Collapse.getOrCreateInstance(navbarContent);

                collapse.hide();
            }
        });
    });

    // Search validation
    const searchForm = document.querySelector(".user-search-form");

    if (searchForm) {
        searchForm.addEventListener("submit", function (event) {

            const searchInput = searchForm.querySelector(
                'input[name="search"]'
            );

            if (!searchInput || searchInput.value.trim() === "") {
                event.preventDefault();

                if (searchInput) {
                    searchInput.focus();
                }
            }
        });
    }

});