document.addEventListener('DOMContentLoaded', () => {
    const recommendBtn = document.getElementById('recommend-btn');
    const loadingIndicator = document.getElementById('loading');
    const tabButtons = document.querySelectorAll('.tab-button');
    const menuBtn = document.getElementById("menu-btn");
    const navLinks = document.getElementById("nav-links");
    const menuBtnIcon = menuBtn ? menuBtn.querySelector("i") : null;

    // Tab switching functionality
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove active class from all buttons and tab contents
            tabButtons.forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

            // Add active class to clicked button and corresponding tab content
            button.classList.add('active');
            const tabId = button.getAttribute('data-tab');
            document.getElementById(`${tabId}-recommendations`).classList.add('active');
        });
    });

    // Recommendation functionality
    if (recommendBtn) {
        recommendBtn.addEventListener('click', () => {
            // Collect preference values
            const preferences = {
                userId: document.getElementById('user-id').value,
                carModels: document.getElementById('car_models').value,
                carMakes: document.getElementById('car_makes').value,
                carType: document.getElementById('car-type').value,
                fuelType: document.getElementById('fuel-type').value,
                transmissionType: document.getElementById('transmission-type').value
            };

            // Show loading indicator
            loadingIndicator.style.display = 'block';

            // Send request to the backend
            fetch('/recommend', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(preferences),
            })
                .then(response => response.json())
                .then(data => {
                    // Hide loading indicator
                    loadingIndicator.style.display = 'none';

                    // Display recommendations
                    displayCars(data.hybrid, 'hybrid-cars');
                    displayCars(data.content_based, 'content-cars');
                    displayCars(data.collaborative_filtering, 'collaborative-cars');
                })
                .catch(error => {
                    console.error('Error:', error);
                    loadingIndicator.style.display = 'none';
                });
        });
    }

    function displayCars(cars, containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        container.innerHTML = '';

        if (!cars || cars.length === 0) {
            container.innerHTML = '<p>No recommendations available.</p>';
            return;
        }

        cars.forEach(car => {
            container.innerHTML += createCarCard(car);
        });
    }

    function createCarCard(car) {
        return `
            <div class="car-card">
                <h3>${car.car_make} ${car.car_models}</h3>
                <p>Type: ${car.car_type}</p>
                <p>Fuel: ${car.fuel_type}</p>
                <p>Transmission: ${car.transmission_type}</p>
                <p>Price per day: $${car.price_per_day || 75}</p>
                <button class="btn btn__primary">Rent Now</button>
            </div>
        `;
    }

    // Navigation Toggle Functionality
    if (menuBtn && navLinks) {
        const menuBtnIcon = menuBtn.querySelector("i");
        if (menuBtnIcon) { // Ensure the icon exists
            menuBtn.addEventListener("click", () => {
                navLinks.classList.toggle("open");
                const isOpen = navLinks.classList.contains("open");
                menuBtnIcon.setAttribute("class", isOpen ? "ri-close-line" : "ri-menu-line");
            });

            navLinks.addEventListener("click", () => {
                navLinks.classList.remove("open");
                menuBtnIcon.setAttribute("class", "ri-menu-line");
            });
        }
    }

    // ScrollReveal animations
    if (typeof ScrollReveal === 'function') {
        const scrollRevealOption = {
            origin: "bottom",
            distance: "50px",
            duration: 1000,
        };

        // Header animations
        ScrollReveal().reveal(".headerr__container h1", {
            ...scrollRevealOption,
        });
        ScrollReveal().reveal(".headerr__container form", {
            ...scrollRevealOption,
            delay: 500,
        });
        ScrollReveal().reveal(".headerr__container img", {
            ...scrollRevealOption,
            delay: 1000,
        });

        // Range animations
        ScrollReveal().reveal(".range__card", {
            duration: 1000,
            interval: 500,
        });

        // Location section animations (updated with your new code)
        ScrollReveal().reveal(".location__image img", {
            ...scrollRevealOption,
            origin: "right",
        });
        ScrollReveal().reveal(".location__content .section__header", {
            ...scrollRevealOption,
            delay: 500,
        });
        ScrollReveal().reveal(".location__content p", {
            ...scrollRevealOption,
            delay: 1000,
        });
        ScrollReveal().reveal(".location__content .location__btn", {
            ...scrollRevealOption,
            delay: 1500,
        });
        
        // Story animations
        ScrollReveal().reveal(".story__card", {
            ...scrollRevealOption,
            interval: 500,
        });
    }

    // Swiper initialization
    const selectCards = document.querySelectorAll(".select__card");
    if (selectCards.length > 0) {
        // Define the prices for each car
        const price = ["225", "455", "275", "625", "395"];
        
        // Get the price element
        const priceEl = document.getElementById("select-price");
        
        // Set the first card as active by default
        selectCards[0].classList.add("show__info");
        
        // Function to update the active card and price
        function updateSwiperImage(eventName, args) {
            if (eventName === "slideChangeTransitionStart" && priceEl) {
                const index = args && args[0] && args[0].realIndex !== undefined ? args[0].realIndex : 0;
                priceEl.innerText = price[index] || "";
                selectCards.forEach((item) => {
                    item.classList.remove("show__info");
                });
                if (selectCards[index]) {
                    selectCards[index].classList.add("show__info");
                }
            }
        }

        // Initialize Swiper
        const swiper = new Swiper(".swiper", {
            loop: true,
            effect: "coverflow",
            grabCursor: true,
            centeredSlides: true,
            slidesPerView: "auto",
            coverflowEffect: {
                rotate: 0,
                depth: 500,
                modifier: 1,
                scale: 0.75,
                slideShadows: false,
                stretch: -100,
            },
            
            onAny(event, ...args) {
                updateSwiperImage(event, args);
            },
        });
    }
});