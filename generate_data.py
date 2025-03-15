import pandas as pd
import numpy as np
import os

# Create data directory if it doesn't exist
if not os.path.exists('data'):
    os.makedirs('data')

# Generate cars data
car_makes = ['Toyota', 'Honda', 'Ford', 'BMW', 'Mercedes', 'Audi', 'Volkswagen', 'Nissan', 'Hyundai', 'Kia']
car_models_list = ['Sedan', 'SUV', 'Hatchback', 'Coupe', 'Convertible', 'Wagon', 'Truck', 'Van']
car_types = ['Economy', 'Compact', 'Mid-size', 'Full-size', 'Luxury', 'Sport', 'SUV', 'Minivan']
fuel_types = ['Gasoline', 'Electric', 'Hybrid', 'Diesel']
transmission_types = ['Automatic', 'Manual', 'CVT']

# Create 100 cars
np.random.seed(42)
n_cars = 100
cars_data = []

for i in range(1, n_cars + 1):
    make = np.random.choice(car_makes)  # <-- Use a different variable name
    model = np.random.choice(car_models_list)
    car_type = np.random.choice(car_types)
    fuel_type = np.random.choice(fuel_types)
    transmission_type = np.random.choice(transmission_types)
    price_per_day = np.random.randint(50, 300)
    year = np.random.randint(2015, 2025)
    
    cars_data.append({
        'car_id': i,
        'car_make': make,  # <-- Corrected key name
        'car_models': model,
        'car_type': car_type,
        'fuel_type': fuel_type,
        'transmission_type': transmission_type,
        'price_per_day': price_per_day,
        'year': year
    })

cars_df = pd.DataFrame(cars_data)
cars_df.to_csv('data/cars.csv', index=False)

# Generate users data
n_users = 50
users_data = []

for i in range(1, n_users + 1):
    age = np.random.randint(18, 70)
    gender = np.random.choice(['Male', 'Female'])
    preferred_car_type = np.random.choice(car_types)
    preferred_fuel_type = np.random.choice(fuel_types)
    
    users_data.append({
        'user_id': i,
        'age': age,
        'gender': gender,
        'preferred_car_type': preferred_car_type,
        'preferred_fuel_type': preferred_fuel_type
    })

users_df = pd.DataFrame(users_data)
users_df.to_csv('data/users.csv', index=False)

# Generate ratings data
n_ratings = 500
ratings_data = []

for _ in range(n_ratings):
    user_id = np.random.randint(1, n_users + 1)
    car_id = np.random.randint(1, n_cars + 1)
    # Make sure we don't have duplicate user-car pairs
    while any((r['user_id'] == user_id and r['car_id'] == car_id) for r in ratings_data):
        user_id = np.random.randint(1, n_users + 1)
        car_id = np.random.randint(1, n_cars + 1)
    
    rating = np.random.randint(1, 6)  # Rating from 1 to 5
    
    ratings_data.append({
        'user_id': user_id,
        'car_id': car_id,
        'rating': rating
    })

ratings_df = pd.DataFrame(ratings_data)
ratings_df.to_csv('data/ratings.csv', index=False)

print("Data generation complete!")