document.addEventListener('DOMContentLoaded', () => {
    const recommendBtn = document.getElementById('recommend-btn');
    const loadingIndicator = document.getElementById('loading');
    const tabButtons = document.querySelectorAll('.tab-button');

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
});