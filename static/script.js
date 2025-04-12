document.addEventListener('DOMContentLoaded', () => {
    const recommendBtn = document.getElementById('recommend-btn');
    const loadingIndicator = document.getElementById('loading');
    const tabButtons = document.querySelectorAll('.tab-button');
    const menuBtn = document.getElementById("menu-btn");
    const navLinks = document.getElementById("nav-links");
    const menuBtnIcon = menuBtn ? menuBtn.querySelector("i") : null;

    // Define valid user IDs
    const VALID_USER_IDS = ["P100088", "L200079", "G300057", "P400044", "L500046"];

    // Define car options from your data
    const car_makes = ['Toyota', 'Honda', 'Ford', 'BMW', 'Mercedes', 'Audi', 'Volkswagen', 'Nissan', 'Hyundai', 'Kia'];
    const car_models_list = ['Sedan', 'SUV', 'Hatchback', 'Coupe', 'Convertible'];
    const car_types = ['Economy', 'Compact', 'Mid-size', 'Full-size', 'Luxury', 'Sport', 'SUV', 'Minivan'];
    const fuel_types = ['Gasoline', 'Electric', 'Hybrid', 'Diesel'];
    const transmission_types = ['Automatic', 'Manual', 'CVT'];

    // Initialiser les boutons de sélection
    const initSelectionButtons = (container, options, field) => {
        const containerElement = document.getElementById(container);
        if (!containerElement) return;

        containerElement.innerHTML = '';

        options.forEach(option => {
            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'option-btn';
            button.textContent = option;
            button.dataset.value = option;
            button.addEventListener('click', () => {
                // Basculer l’état du bouton (actif/inactif)
                if (button.classList.contains('active')) {
                    button.classList.remove('active');
                } else {
                    // Supprimer la classe 'active' de tous les boutons de ce conteneur
                    containerElement.querySelectorAll('.option-btn').forEach(btn => {
                        btn.classList.remove('active');
                    });
                    button.classList.add('active');
                }
            });
            containerElement.appendChild(button);
        });
    };

    // Initialize all selection buttons
    initSelectionButtons('car-make-selection', car_makes, 'car_makes');
    initSelectionButtons('car-model-selection', car_models_list, 'car_models');
    initSelectionButtons('car-type-selection', car_types, 'car_type');
    initSelectionButtons('fuel-type-selection', fuel_types, 'fuel_type');
    initSelectionButtons('transmission-type-selection', transmission_types, 'transmission_type');

    // Tab switching functionality
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            tabButtons.forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            button.classList.add('active');
            const tabId = button.getAttribute('data-tab');
            document.getElementById(`${tabId}-recommendations`).classList.add('active');
        });
    });

    // Recommendation functionality
    if (recommendBtn) {
        recommendBtn.addEventListener('click', () => {
            const userId = document.getElementById('user-id').value.trim();

            // Check if user ID is provided
            if (!userId) {
                alert("Please enter a user ID to get personalized recommendations");
                return;
            }

            // Check if the user ID is in our list of valid IDs
            if (!VALID_USER_IDS.includes(userId)) {
                alert("Invalid user ID. Please use one of the provided user IDs (e.g., P100088, L200079, etc.)");
                return;
            }

            // Get selected values from buttons
            const getSelectedValue = (containerId) => {
                const activeButton = document.querySelector(`#${containerId} .option-btn.active`);
                return activeButton ? activeButton.dataset.value : '';
            };

            const preferences = {
                user_id: userId,
                car_models: getSelectedValue('car-model-selection'),
                car_makes: getSelectedValue('car-make-selection'),
                car_type: getSelectedValue('car-type-selection'),
                fuel_type: getSelectedValue('fuel-type-selection'),
                transmission_type: getSelectedValue('transmission-type-selection')
            };

            console.log("Preferences sent:", preferences);
            loadingIndicator.style.display = 'block';

            // Clear containers
            document.querySelectorAll('.cars-grid').forEach(container => {
                container.innerHTML = '';
            });

            fetch('/recommend', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(preferences),
            })
                .then(response => {
                    if (!response.ok) {
                        return response.json().then(data => {
                            throw new Error(data.error || `HTTP Error: ${response.status}`);
                        });
                    }
                    return response.json();
                })
                .then(data => {
                    console.log("Complete API response:", data);
                    loadingIndicator.style.display = 'none';

                    if (data.collaborative_filtering) {
                        console.log("Collaborative data received:", data.collaborative_filtering);
                        console.log("Number of items:", data.collaborative_filtering.length);
                        if (data.collaborative_filtering.length > 0) {
                            console.log("First item:", data.collaborative_filtering[0]);
                        }
                    } else {
                        console.warn("No collaborative data received");
                    }

                    // Display recommendations
                    const historyContainer = document.getElementById('history-cars');
                    if (historyContainer) {
                        displayCars(data.history_based || [], 'history-cars');
                    }
                    displayCars(data.hybrid || [], 'hybrid-cars');
                    displayCars(data.content_based || [], 'content-cars');
                    displayCollaborativeRecommendations(data.collaborative_filtering || [], 'collaborative-cars');
                })
                .catch(error => {
                    console.error('Error:', error);
                    loadingIndicator.style.display = 'none';
                    alert(error.message || 'An error occurred when retrieving recommendations. Please try again.');
                    const errorMessage = `<p class="error-message">${error.message || 'An error occurred when retrieving recommendations. Please try again.'}</p>`;
                    document.querySelectorAll('.cars-grid').forEach(container => {
                        container.innerHTML = errorMessage;
                    });
                });
        });
    }

    // Function to display collaborative recommendations with detailed logs
    function displayCollaborativeRecommendations(cars, containerId) {
        console.log(`Starting display for ${containerId} with ${cars.length} cars`);
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Container ${containerId} does not exist`);
            return;
        }

        container.innerHTML = '';

        if (!cars || !Array.isArray(cars) || cars.length === 0) {
            console.warn(`No recommendations available for ${containerId}`);
            container.innerHTML = '<p>No recommendations available. This could be because there are not enough similar users with ratings.</p>';
            return;
        }

        cars.forEach((car, index) => {
            console.log(`Processing car ${index}:`, car);
            try {
                const carCard = document.createElement('div');
                carCard.className = 'car-card';
                carCard.innerHTML = createCarCardHTML(car);
                container.appendChild(carCard);
            } catch (e) {
                console.error(`Error displaying car ${index}:`, e);
            }
        });
    }

    // Function to display other types of recommendations
    function displayCars(cars, containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        container.innerHTML = '';

        if (!cars || !Array.isArray(cars) || cars.length === 0) {
            container.innerHTML = '<p>No recommendations available.</p>';
            return;
        }

        cars.forEach(car => {
            const carCard = document.createElement('div');
            carCard.className = 'car-card';
            carCard.innerHTML = createCarCardHTML(car);
            container.appendChild(carCard);
        });
    }

    // Function to create the HTML for a car card
    function createCarCardHTML(car) {
        if (!car) {
            console.error("Invalid car object:", car);
            return "<p>Error: invalid car data</p>";
        }

        const carMake = car.car_make || car.make || 'Unknown Make';
        const carModel = car.car_models || car.model || 'Unknown Model';
        const carType = car.car_type || car.type || 'Unknown Type';
        const fuelType = car.fuel_type || 'Unknown Fuel';
        const transmissionType = car.transmission_type || 'Unknown Transmission';
        const price = car.price_per_day || 75;
        const year = car.year || 'N/A';

        return `
            <div>
                <h3>${carMake} ${carModel}</h3>
                <p>Type: ${carType}</p>
                <p>Fuel: ${fuelType}</p>
                <p>Transmission: ${transmissionType}</p>
                <p>Price per day: $${price}</p>
                <p>Year: ${year}</p>
                <div >
                   <button class="btn btn__primary">Rent Now</button>
                </div>
            </div>
        `;
    }

    // Navigation Toggle Functionality
    if (menuBtn && navLinks && menuBtnIcon) {
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

    // ScrollReveal animations
    if (typeof ScrollReveal === 'function') {
        const scrollRevealOption = {
            origin: "bottom",
            distance: "50px",
            duration: 1000,
        };

        ScrollReveal().reveal(".headerr__container h1", scrollRevealOption);
        ScrollReveal().reveal(".headerr__container form", { ...scrollRevealOption, delay: 500 });
        ScrollReveal().reveal(".headerr__container img", { ...scrollRevealOption, delay: 1000 });
        ScrollReveal().reveal(".range__card", { duration: 1000, interval: 500 });
        ScrollReveal().reveal(".location__image img", { ...scrollRevealOption, origin: "right" });
        ScrollReveal().reveal(".location__content .section__header", { ...scrollRevealOption, delay: 500 });
        ScrollReveal().reveal(".location__content p", { ...scrollRevealOption, delay: 1000 });
        ScrollReveal().reveal(".location__content .location__btn", { ...scrollRevealOption, delay: 1500 });
        ScrollReveal().reveal(".story__card", { ...scrollRevealOption, interval: 500 });

        // This section uses ScrollReveal for animation
        ScrollReveal().reveal(".range__card", {
            duration: 1000,
            interval: 500,
        });
    }

    // Swiper initialization
    const selectCards = document.querySelectorAll(".select__card");
    if (selectCards.length > 0) {
        const price = ["225", "455", "275", "625", "395"];
        const priceEl = document.getElementById("select-price");
        selectCards[0].classList.add("show__info");

        function updateSwiperImage(eventName, args) {
            if (eventName === "slideChangeTransitionStart" && priceEl) {
                const index = args && args[0] && args[0].realIndex !== undefined ? args[0].realIndex : 0;
                priceEl.innerText = price[index] || "";
                selectCards.forEach((item) => item.classList.remove("show__info"));
                if (selectCards[index]) selectCards[index].classList.add("show__info");
            }
        }

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