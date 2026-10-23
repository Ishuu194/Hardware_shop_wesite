
document.addEventListener("DOMContentLoaded", function () {

    // 1. Delete confirmation
    document.querySelectorAll(".delete-btn").forEach(function (button) {
        button.addEventListener("click", function (event) {
            if (!confirm("Are you sure you want to delete this product?")) {
                event.preventDefault();
            }
        });
    });

    // 2. Add Product form validation
    const productForm = document.querySelector("#product-form");

    if (productForm) {
        productForm.addEventListener("submit", function (event) {
            const name = productForm.querySelector('[name="name"]');
            const price = productForm.querySelector('[name="price"]');
            const stock = productForm.querySelector('[name="stock"]');

            if (name && !name.value.trim()) {
                event.preventDefault();
                alert("Please enter the product name.");
                name.focus();
                return;
            }

            if (price && (
                price.value.trim() === "" ||
                !Number.isFinite(Number(price.value)) ||
                Number(price.value) < 0
            )) {
                event.preventDefault();
                alert("Please enter a valid product price.");
                price.focus();
                return;
            }

            if (stock && (
                stock.value.trim() === "" ||
                !Number.isInteger(Number(stock.value)) ||
                Number(stock.value) < 0
            )) {
                event.preventDefault();
                alert("Please enter a valid stock quantity.");
                stock.focus();
            }
        });
    }

    // 3. Search products
    const searchInput = document.querySelector("#product-search");
    const productRows = document.querySelectorAll(
        "#products-table tbody tr"
    );

    if (searchInput) {
        searchInput.addEventListener("input", function () {
            const searchText = searchInput.value.toLowerCase().trim();

            productRows.forEach(function (row) {
                row.style.display = row.textContent
                    .toLowerCase()
                    .includes(searchText) ? "" : "none";
            });
        });
    }

    // 4. Mobile sidebar
    const menuButton = document.querySelector("#sidebar-toggle");
    const sidebar = document.querySelector(".sidebar");

    if (menuButton && sidebar) {

        function closeSidebar() {
            sidebar.classList.remove("sidebar-open");
            menuButton.setAttribute("aria-expanded", "false");
        }

        menuButton.addEventListener("click", function () {
            const isOpen = sidebar.classList.toggle("sidebar-open");
            menuButton.setAttribute("aria-expanded", String(isOpen));
        });

        // Close menu after selecting a link on mobile
        sidebar.querySelectorAll(".menu-link").forEach(function (link) {
            link.addEventListener("click", function () {
                if (window.innerWidth <= 600) {
                    closeSidebar();
                }
            });
        });

        // Close menu with Escape key
        document.addEventListener("keydown", function (event) {
            if (event.key === "Escape") {
                closeSidebar();
            }
        });

        // Reset menu when returning to desktop width
        window.addEventListener("resize", function () {
            if (window.innerWidth > 600) {
                closeSidebar();
            }
        });
    }

});

document.addEventListener("DOMContentLoaded", function () {

    const searchInput = document.getElementById("product-search");
    const productsTable = document.getElementById("products-table");
    const noResults = document.getElementById("no-results");

    if (!searchInput || !productsTable || !noResults) {
        return;
    }

    searchInput.addEventListener("input", function () {

        const searchText = searchInput.value.toLowerCase().trim();
        const rows = productsTable.querySelectorAll("tbody tr");

        let visibleCount = 0;
        let productRowCount = 0;

        rows.forEach(function (row) {

            // Do not count the empty-products message as a product
            if (row.querySelector(".empty-message")) {
                return;
            }

            productRowCount++;

            const rowText = row.textContent.toLowerCase();
            const matches = rowText.includes(searchText);

            row.style.display = matches ? "" : "none";

            if (matches) {
                visibleCount++;
            }
        });

        noResults.hidden =
            !(productRowCount > 0 && visibleCount === 0);
    });

});

// Category Products Search
document.addEventListener("DOMContentLoaded", function () {

    const searchInput = document.getElementById(
        "category-product-search"
    );

    const table = document.getElementById(
        "category-products-table"
    );

    const noResults = document.getElementById(
        "category-no-results"
    );

    if (!searchInput || !table || !noResults) {
        return;
    }

    searchInput.addEventListener("input", function () {

        const searchText = this.value.toLowerCase().trim();
        const rows = table.querySelectorAll("tbody tr");

        let visibleCount = 0;
        let productCount = 0;

        rows.forEach(function (row) {

            if (row.querySelector(".empty-message")) {
                return;
            }

            productCount++;

            const rowText = row.textContent.toLowerCase();
            const matches = rowText.includes(searchText);

            row.style.display = matches ? "" : "none";

            if (matches) {
                visibleCount++;
            }
        });

        noResults.hidden =
            productCount === 0 || visibleCount > 0;

    });

});


/* =========================================
   ORDERS PAGE - SEARCH
========================================= */

document.addEventListener("DOMContentLoaded", function () {

    const searchInput = document.getElementById("orders-search");
    const ordersTable = document.getElementById("orders-table");
    const noResults = document.getElementById("orders-no-results");

    // Run only on the Orders page
    if (!searchInput || !ordersTable || !noResults) {
        return;
    }

    searchInput.addEventListener("input", function () {

        const searchText = this.value.toLowerCase().trim();
        const rows = ordersTable.querySelectorAll("tbody tr");

        let visibleCount = 0;
        let orderCount = 0;

        rows.forEach(function (row) {

            // Skip the "No Orders Found" row
            if (row.querySelector(".empty-message")) {
                return;
            }

            orderCount++;

            const rowText = row.textContent.toLowerCase();
            const matches = rowText.includes(searchText);

            row.style.display = matches ? "" : "none";

            if (matches) {
                visibleCount++;
            }
        });

        // Show message when no orders match the search
        noResults.hidden = !(
            orderCount > 0 && visibleCount === 0
        );

    });

});

/* =========================================
   STOCK MANAGEMENT PAGE - SEARCH
========================================= */

document.addEventListener("DOMContentLoaded", function () {

    const searchInput = document.getElementById("stock-search");
    const stockTable = document.getElementById("stock-table");
    const noResults = document.getElementById("stock-no-results");

    // Run only on Stock Management page
    if (!searchInput || !stockTable || !noResults) {
        return;
    }

    searchInput.addEventListener("input", function () {

        const searchText = this.value.toLowerCase().trim();
        const rows = stockTable.querySelectorAll("tbody tr");

        let visibleCount = 0;
        let productCount = 0;

        rows.forEach(function (row) {

            // Skip the empty-products message
            if (row.querySelector(".empty-message")) {
                return;
            }

            productCount++;

            const rowText = row.textContent.toLowerCase();
            const matches = rowText.includes(searchText);

            row.style.display = matches ? "" : "none";

            if (matches) {
                visibleCount++;
            }
        });

        // Show message when no product matches
        noResults.hidden = !(
            productCount > 0 && visibleCount === 0
        );

    });

});
/* =========================================
   ZAMBRE AGENCIES - ADMIN PROFILE JS
========================================= */

document.addEventListener("DOMContentLoaded", function () {

    const logoutButton = document.getElementById("adminLogoutBtn");

    if (!logoutButton) {
        return;
    }

    logoutButton.addEventListener("click", function (event) {

        const confirmLogout = confirm(
            "Are you sure you want to logout from your admin account?"
        );

        if (!confirmLogout) {
            event.preventDefault();
        }

    });

});