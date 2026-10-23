// /* =========================================
//    ZAMBRE AGENCIES - HOME PAGE SLIDER
//    Automatic Slider + Navigation + Dots
// ========================================= */

// document.addEventListener("DOMContentLoaded", function () {

//     const slider = document.querySelector(".home-slider");

//     // Stop if the slider does not exist
//     if (!slider) {
//         return;
//     }

//     const slides = Array.from(
//         slider.querySelectorAll(".home-slide")
//     );

//     const prevButton = slider.querySelector(".home-prev");
//     const nextButton = slider.querySelector(".home-next");

//     const dots = Array.from(
//         slider.querySelectorAll(".home-slider-dot")
//     );

//     // No products available
//     if (slides.length === 0) {
//         return;
//     }

//     let currentIndex = slides.findIndex(function (slide) {
//         return slide.classList.contains("active");
//     });

//     if (currentIndex < 0) {
//         currentIndex = 0;
//     }

//     let autoSlideTimer = null;

//     // Time between automatic slides
//     const slideInterval = 4000;


//     /* =====================================
//        SHOW SELECTED SLIDE
//     ====================================== */

//     function showSlide(index) {

//         // Move back to the last slide
//         if (index < 0) {
//             index = slides.length - 1;
//         }

//         // Move to the first slide
//         if (index >= slides.length) {
//             index = 0;
//         }

//         currentIndex = index;

//         // Activate selected slide
//         slides.forEach(function (slide, slideIndex) {

//             const isActive = slideIndex === currentIndex;

//             slide.classList.toggle("active", isActive);

//             slide.setAttribute(
//                 "aria-hidden",
//                 isActive ? "false" : "true"
//             );
//         });

//         // Activate the corresponding dot
//         dots.forEach(function (dot, dotIndex) {

//             const isActive = dotIndex === currentIndex;

//             dot.classList.toggle("active", isActive);

//             dot.setAttribute(
//                 "aria-current",
//                 isActive ? "true" : "false"
//             );
//         });
//     }


//     /* =====================================
//        NEXT AND PREVIOUS SLIDES
//     ====================================== */

//     function nextSlide() {
//         showSlide(currentIndex + 1);
//     }

//     function previousSlide() {
//         showSlide(currentIndex - 1);
//     }


//     /* =====================================
//        AUTOMATIC SLIDER
//     ====================================== */

//     function stopAutoSlide() {

//         if (autoSlideTimer !== null) {
//             clearInterval(autoSlideTimer);
//             autoSlideTimer = null;
//         }
//     }

//     function startAutoSlide() {

//         stopAutoSlide();

//         // No need to rotate if there is only one product
//         if (slides.length <= 1) {
//             return;
//         }

//         autoSlideTimer = setInterval(function () {
//             nextSlide();
//         }, slideInterval);
//     }


//     /* =====================================
//        ARROW BUTTONS
//     ====================================== */

//     if (nextButton) {

//         nextButton.addEventListener("click", function () {

//             nextSlide();

//             // Restart the timer after manual navigation
//             startAutoSlide();
//         });
//     }

//     if (prevButton) {

//         prevButton.addEventListener("click", function () {

//             previousSlide();

//             // Restart the timer after manual navigation
//             startAutoSlide();
//         });
//     }


//     /* =====================================
//        DOT BUTTONS
//     ====================================== */

//     dots.forEach(function (dot, index) {

//         dot.addEventListener("click", function () {

//             showSlide(index);

//             // Restart the timer after choosing a dot
//             startAutoSlide();
//         });
//     });


//     /* =====================================
//        PAUSE WHEN MOUSE IS OVER SLIDER
//     ====================================== */

//     slider.addEventListener("mouseenter", function () {
//         stopAutoSlide();
//     });

//     slider.addEventListener("mouseleave", function () {
//         startAutoSlide();
//     });


//     /* =====================================
//        PAUSE WHEN TAB IS HIDDEN
//     ====================================== */

//     document.addEventListener("visibilitychange", function () {

//         if (document.hidden) {
//             stopAutoSlide();
//         } else {
//             startAutoSlide();
//         }
//     });


//     /* =====================================
//        INITIALIZE SLIDER
//     ====================================== */

//     showSlide(currentIndex);
//     startAutoSlide();

// });

/* =========================================
   HOME PAGE - AUTO PRODUCT SLIDER
========================================= */

document.addEventListener("DOMContentLoaded", function () {

    const slider = document.querySelector(".home-slider");

    if (!slider) {
        return;
    }

    const slides = slider.querySelectorAll(".home-slide");
    const dots = slider.querySelectorAll(".home-slider-dot");
    const prevButton = slider.querySelector(".home-prev");
    const nextButton = slider.querySelector(".home-next");

    // At least two products are required to move
    if (slides.length < 2) {
        console.log("Slider needs at least 2 featured products.");
        return;
    }

    let currentIndex = 0;
    let slideTimer;

    function showSlide(index) {

        currentIndex = (index + slides.length) % slides.length;

        slides.forEach(function (slide, i) {
            slide.classList.toggle("active", i === currentIndex);
        });

        dots.forEach(function (dot, i) {
            dot.classList.toggle("active", i === currentIndex);
        });
    }

    function nextSlide() {
        showSlide(currentIndex + 1);
    }

    function previousSlide() {
        showSlide(currentIndex - 1);
    }

    function startAutoSlide() {
        clearInterval(slideTimer);

        slideTimer = setInterval(function () {
            nextSlide();
        }, 3000);
    }

    if (nextButton) {
        nextButton.addEventListener("click", function () {
            nextSlide();
            startAutoSlide();
        });
    }

    if (prevButton) {
        prevButton.addEventListener("click", function () {
            previousSlide();
            startAutoSlide();
        });
    }

    dots.forEach(function (dot, index) {
        dot.addEventListener("click", function () {
            showSlide(index);
            startAutoSlide();
        });
    });

    // Start slider
    showSlide(0);
    startAutoSlide();

});