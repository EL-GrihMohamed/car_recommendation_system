import pandas as pd
import numpy as np
import os
import random

# Create data directory if it doesn't exist
if not os.path.exists('data'):
    os.makedirs('data')

# Define alphanumeric user IDs for the 5 existing users
alpha_user_ids = {
    1: "P100088",
    2: "L200079",
    3: "G300057",
    4: "P400044",
    5: "L500046"
}

# Load existing data (optional)
try:
    existing_cars = pd.read_csv('data/cars.csv')
    existing_users = pd.read_csv('data/users.csv')
    existing_ratings = pd.read_csv('data/ratings.csv')
    print("Loaded existing data files")
    
    # Use existing data as base
    cars_df = existing_cars
    
    # Create new users DataFrame with alphanumeric IDs
    users_data = []
    for _, user in existing_users.iterrows():
        # Extract numeric user_id if it's alphanumeric
        if isinstance(user['user_id'], str) and any(user['user_id'].startswith(prefix) for prefix in ['P', 'L', 'G']):
            alpha_id = user['user_id']
            user_id = int(''.join(filter(str.isdigit, alpha_id[:7])))
        else:
            user_id = int(user['user_id'])
            # If user_id is in our mapping, use the alphanumeric version, otherwise generate one
            if user_id in alpha_user_ids:
                alpha_id = alpha_user_ids[user_id]
            else:
                prefix = random.choice(['P', 'L', 'G'])
                alpha_id = f"{prefix}{user_id:06d}"
        
        users_data.append({
            'user_id': alpha_id,
            'age': user['age'],
            'gender': user['gender'],
            'preferred_car_type': user['preferred_car_type'],
            'preferred_fuel_type': user['preferred_fuel_type']
        })
    
    users_df = pd.DataFrame(users_data)
    
    # Create new ratings DataFrame with alphanumeric user IDs
    ratings_data = []
    for _, rating in existing_ratings.iterrows():
        # Extract numeric user_id if it's alphanumeric
        if isinstance(rating['user_id'], str) and any(rating['user_id'].startswith(prefix) for prefix in ['P', 'L', 'G']):
            alpha_id = rating['user_id']
            user_id = int(''.join(filter(str.isdigit, alpha_id[:7])))
        else:
            user_id = int(rating['user_id'])
            # Map to alphanumeric ID
            if user_id in alpha_user_ids:
                alpha_id = alpha_user_ids[user_id]
            else:
                prefix = random.choice(['P', 'L', 'G'])
                alpha_id = f"{prefix}{user_id:06d}"
        
        ratings_data.append({
            'user_id': alpha_id,
            'car_id': rating['car_id'],
            'rating': rating['rating']
        })
    
    ratings_df = pd.DataFrame(ratings_data)
    
except FileNotFoundError:
    print("Existing data files not found. Generating new data...")
    
    # Generate cars data
    car_makes = ['Toyota', 'Honda', 'Ford', 'BMW', 'Mercedes', 'Audi', 'Volkswagen', 'Nissan', 'Hyundai', 'Kia']
    car_models_list = ['Sedan', 'SUV', 'Hatchback', 'Coupe', 'Convertible', 'Wagon', 'Truck', 'Van']
    car_types = ['Economy', 'Compact', 'Mid-size', 'Full-size', 'Luxury', 'Sport', 'SUV', 'Minivan']
    fuel_types = ['Gasoline', 'Electric', 'Hybrid', 'Diesel']
    transmission_types = ['Automatic', 'Manual', 'CVT']

    # Create cars
    np.random.seed(42)
    n_cars = 100
    cars_data = []

    for i in range(1, n_cars + 1):
        make = np.random.choice(car_makes)
        model = np.random.choice(car_models_list)
        car_type = np.random.choice(car_types)
        fuel_type = np.random.choice(fuel_types)
        transmission_type = np.random.choice(transmission_types)
        price_per_day = np.random.randint(50, 300)
        year = np.random.randint(2015, 2025)
        
        cars_data.append({
            'car_id': i,
            'car_make': make,
            'car_models': model,
            'car_type': car_type,
            'fuel_type': fuel_type,
            'transmission_type': transmission_type,
            'price_per_day': price_per_day,
            'year': year
        })

    cars_df = pd.DataFrame(cars_data)
    
    # Generate users with alphanumeric IDs
    n_users = 5  # Since you mentioned you only have 5 users
    users_data = []
    
    for i in range(1, n_users + 1):
        # Use our predefined alphanumeric IDs
        alpha_id = alpha_user_ids[i]
        
        age = np.random.randint(18, 70)
        gender = np.random.choice(['Male', 'Female'])
        preferred_car_type = np.random.choice(car_types)
        preferred_fuel_type = np.random.choice(fuel_types)
        
        users_data.append({
            'user_id': alpha_id,
            'age': age,
            'gender': gender,
            'preferred_car_type': preferred_car_type,
            'preferred_fuel_type': preferred_fuel_type
        })

    users_df = pd.DataFrame(users_data)
    
    # Generate ratings data with alphanumeric user IDs
    n_ratings = 10  # Just 10 ratings (2 for each of the 5 users)
    ratings_data = []
    
    # For each user, create 2 ratings
    for i in range(1, n_users + 1):
        alpha_id = alpha_user_ids[i]
        
        # First rating
        car_id1 = np.random.randint(1, n_cars + 1)
        rating1 = np.random.randint(1, 6)  # Rating from 1 to 5
        
        # Second rating
        car_id2 = np.random.randint(1, n_cars + 1)
        while car_id2 == car_id1:  # Ensure different cars
            car_id2 = np.random.randint(1, n_cars + 1)
        rating2 = np.random.randint(1, 6)  # Rating from 1 to 5
        
        ratings_data.append({
            'user_id': alpha_id,
            'car_id': car_id1,
            'rating': rating1
        })
        
        ratings_data.append({
            'user_id': alpha_id,
            'car_id': car_id2,
            'rating': rating2
        })
    
    ratings_df = pd.DataFrame(ratings_data)

# Create purchase data if it doesn't exist
if not os.path.exists('data/purchases.csv'):
    # Create a purchases DataFrame with alphanumeric user IDs
    purchases_data = []
    
    # For the 5 users with predefined IDs
    for i in range(1, 6):
        alpha_id = alpha_user_ids[i]
        car_id = np.random.randint(1, len(cars_df) + 1)
        
        # Check if the car exists before accessing its properties
        car_row = cars_df[cars_df['car_id'] == car_id]
        if not car_row.empty:
            purchases_data.append({
                'user_id': alpha_id,
                'car_id': car_id,
                'car_make': car_row['car_make'].values[0],
                'car_model': car_row['car_models'].values[0],
                'car_type': car_row['car_type'].values[0],
                'fuel_type': car_row['fuel_type'].values[0],
                'transmission_type': car_row['transmission_type'].values[0],
                'price_per_day': car_row['price_per_day'].values[0],
                'year': car_row['year'].values[0]
            })
    
    purchases_df = pd.DataFrame(purchases_data)
    purchases_df.to_csv('data/purchases.csv', index=False)
    print("Created purchases.csv with alphanumeric user IDs")

# Create backup of original files
if os.path.exists('data/users_original.csv'):
    print("Backup files already exist, skipping backup creation")
else:
    # Create backups of original files
    try:
        original_users = pd.read_csv('data/users.csv')
        original_ratings = pd.read_csv('data/ratings.csv')
        
        original_users.to_csv('data/users_original.csv', index=False)
        original_ratings.to_csv('data/ratings_original.csv', index=False)
        print("Created backups of original files")
    except FileNotFoundError:
        print("Could not create backups, possibly files don't exist yet")

# Save the new dataframes with alphanumeric IDs
cars_df.to_csv('data/cars.csv', index=False)
users_df.to_csv('data/users.csv', index=False)
ratings_df.to_csv('data/ratings.csv', index=False)

print("Data generation with alphanumeric IDs complete!")