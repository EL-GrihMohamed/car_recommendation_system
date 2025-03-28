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

            // Simulate API call (replace with actual fetch to your backend)
            setTimeout(() => {
                // Hide loading indicator
                loadingIndicator.style.display = 'none';

                // Example recommendation data (replace with actual data from backend)
                const recommendations = {
                    hybrid: [
                        { 
                            carMake: 'Toyota', 
                            carModel: 'Prius', 
                            carType: 'Hybrid', 
                            fuelType: 'Hybrid', 
                            transmissionType: 'Automatic',
                            pricePerDay: 75 
                        },
                        { 
                            carMake: 'Honda', 
                            carModel: 'Insight', 
                            carType: 'Hybrid', 
                            fuelType: 'Hybrid', 
                            transmissionType: 'Automatic',
                            pricePerDay: 70 
                        }
                    ],
                    contentBased: [
                        { 
                            carMake: 'Ford', 
                            carModel: 'Mustang', 
                            carType: 'Sports', 
                            fuelType: 'Petrol', 
                            transmissionType: 'Manual',
                            pricePerDay: 100 
                        }
                    ],
                    collaborativeBased: [
                        { 
                            carMake: 'BMW', 
                            carModel: '3 Series', 
                            carType: 'Sedan', 
                            fuelType: 'Diesel', 
                            transmissionType: 'Automatic',
                            pricePerDay: 90 
                        }
                    ]
                };

                // Display recommendations
                displayRecommendations(recommendations);
            }, 1500);
        });
    }

    function displayRecommendations(recommendations) {
        // Display Hybrid Recommendations
        const hybridContainer = document.getElementById('hybrid-cars');
        hybridContainer.innerHTML = recommendations.hybrid.map(car => createCarCard(car)).join('');

        // Display Content-Based Recommendations
        const contentContainer = document.getElementById('content-cars');
        contentContainer.innerHTML = recommendations.contentBased.map(car => createCarCard(car)).join('');

        // Display Collaborative Recommendations
        const collaborativeContainer = document.getElementById('collaborative-cars');
        collaborativeContainer.innerHTML = recommendations.collaborativeBased.map(car => createCarCard(car)).join('');
    }

    function createCarCard(car) {
        return `
            <div class="car-card">
                <h3>${car.carMake} ${car.carModel}</h3>
                <p>Type: ${car.carType}</p>
                <p>Fuel: ${car.fuelType}</p>
                <p>Transmission: ${car.transmissionType}</p>
                <p>Price per day: $${car.pricePerDay}</p>
                <button class="btn btn__primary">Rent Now</button>
            </div>
        `;
    }
});