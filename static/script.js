document.getElementById('recommend-btn').addEventListener('click', function () {
    const userId = document.getElementById('user-id').value;
    const carModels = document.getElementById('car_models').value;
    const carMakes = document.getElementById('car_makes').value;
    const carType = document.getElementById('car-type').value;
    const fuelType = document.getElementById('fuel-type').value;
    const transmissionType = document.getElementById('transmission-type').value;
    const recommendationType = document.getElementById('recommendation-type').value; // Get selected recommendation type

    const preferences = {
        user_id: userId,
        car_models: carModels,
        car_makes: carMakes,
        car_type: carType,
        fuel_type: fuelType,
        transmission_type: transmissionType
    };

    // Show loading spinner
    document.getElementById('loading').style.display = 'block';

    // Send request to the backend
    fetch('/recommend', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ...preferences, recommendation_type: recommendationType }), // Include recommendation type
    })
    .then(response => response.json())
    .then(data => {
        // Hide loading spinner
        document.getElementById('loading').style.display = 'none';

        // Display the recommendations based on the selected type
        if (recommendationType === 'hybrid') {
            displayCars(data.hybrid, 'hybrid-cars');
        } else if (recommendationType === 'content') {
            displayCars(data.content_based, 'content-cars');
        } else if (recommendationType === 'collaborative') {
            displayCars(data.collaborative_filtering, 'collaborative-cars');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('loading').style.display = 'none';
    });
});

function displayCars(cars, containerId) {
    const container = document.getElementById(containerId);
    container.innerHTML = ''; // Clear previous results

    if (cars.length === 0) {
        container.innerHTML = '<p>No recommendations found.</p>';
        return;
    }

    cars.forEach(car => {
        const carCard = document.createElement('div');
        carCard.className = 'car-card';
        carCard.innerHTML = `
            <h3>${car.car_make} ${car.car_models}</h3>
            <p>Type: ${car.car_type}</p>
            <p>Fuel: ${car.fuel_type}</p>
            <p>Transmission: ${car.transmission_type}</p>
            <p>Price per day: $${car.price_per_day}</p>
            <p>Year: ${car.year}</p>
        `;
        container.appendChild(carCard);
    });
}