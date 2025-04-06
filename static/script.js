document.addEventListener('DOMContentLoaded', () => {
    const recommendBtn = document.getElementById('recommend-btn');
    const loadingIndicator = document.getElementById('loading');
    const tabButtons = document.querySelectorAll('.tab-button');
    const menuBtn = document.getElementById("menu-btn");
    const navLinks = document.getElementById("nav-links");
    const menuBtnIcon = menuBtn ? menuBtn.querySelector("i") : null;

    // Define valid user IDs
    const VALID_USER_IDS = ["P100088", "L200079", "G300057", "P400044", "L500046"];

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
                alert("Veuillez entrer un ID utilisateur pour obtenir des recommandations personnalisées");
                return;
            }
            
            // Check if the user ID is in our list of valid IDs
            if (!VALID_USER_IDS.includes(userId)) {
                alert("ID utilisateur invalide. Veuillez utiliser l'un des IDs utilisateurs fournis (ex: P100088, L200079, etc.)");
                return;
            }

            const preferences = {
                user_id: userId,
                car_models: document.getElementById('car_models').value,
                car_makes: document.getElementById('car_makes').value,
                car_type: document.getElementById('car-type').value,
                fuel_type: document.getElementById('fuel-type').value,
                transmission_type: document.getElementById('transmission-type').value
            };

            console.log("Préférences envoyées:", preferences);
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
                        throw new Error(data.error || `Erreur HTTP: ${response.status}`);
                    });
                }
                return response.json();
            })
            .then(data => {
                console.log("Réponse complète de l'API:", data);
                loadingIndicator.style.display = 'none';

                if (data.collaborative_filtering) {
                    console.log("Données collaboratives reçues:", data.collaborative_filtering);
                    console.log("Nombre d'éléments:", data.collaborative_filtering.length);
                    if (data.collaborative_filtering.length > 0) {
                        console.log("Premier élément:", data.collaborative_filtering[0]);
                    }
                } else {
                    console.warn("Aucune donnée collaborative reçue");
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
                console.error('Erreur:', error);
                loadingIndicator.style.display = 'none';
                alert(error.message || 'Une erreur s\'est produite lors de la récupération des recommandations. Veuillez réessayer.');
                const errorMessage = `<p class="error-message">${error.message || 'Une erreur s\'est produite lors de la récupération des recommandations. Veuillez réessayer.'}</p>`;
                document.querySelectorAll('.cars-grid').forEach(container => {
                    container.innerHTML = errorMessage;
                });
            });
        });
    }

    // Function to display collaborative recommendations with detailed logs
    function displayCollaborativeRecommendations(cars, containerId) {
        console.log(`Début de l'affichage pour ${containerId} avec ${cars.length} voitures`);
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Le conteneur ${containerId} n'existe pas`);
            return;
        }

        container.innerHTML = '';

        if (!cars || !Array.isArray(cars) || cars.length === 0) {
            console.warn(`Pas de recommandations disponibles pour ${containerId}`);
            container.innerHTML = '<p>No recommendations available. This could be because there are not enough similar users with ratings.</p>';
            return;
        }

        cars.forEach((car, index) => {
            console.log(`Traitement de la voiture ${index}:`, car);
            try {
                const carCard = document.createElement('div');
                carCard.className = 'car-card';
                carCard.innerHTML = createCarCardHTML(car);
                container.appendChild(carCard);
            } catch (e) {
                console.error(`Erreur lors de l'affichage de la voiture ${index}:`, e);
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
            console.error("Objet voiture invalide:", car);
            return "<p>Erreur: données de voiture invalides</p>";
        }

        const carMake = car.car_make || car.make || 'Unknown Make';
        const carModel = car.car_models || car.model || 'Unknown Model';
        const carType = car.car_type || car.type || 'Unknown Type';
        const fuelType = car.fuel_type || 'Unknown Fuel';
        const transmissionType = car.transmission_type || 'Unknown Transmission';
        const price = car.price_per_day || 75;
        const year = car.year || 'N/A';

        return `
            <div class="car-card">
                <h3>${carMake} ${carModel}</h3>
                <p>Type: ${carType}</p>
                <p>Fuel: ${fuelType}</p>
                <p>Transmission: ${transmissionType}</p>
                <p>Price per day: $${price}</p>
                <p>Year: ${year}</p>
                <div class="button-container">
                   <button class="btn btn__primary">Rent Now</button>
                   <button class="cart_btn">Add to Cart</button>
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