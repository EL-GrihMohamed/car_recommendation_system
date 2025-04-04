from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
from surprise import Dataset, Reader, KNNBasic
from surprise.model_selection import train_test_split
import pickle
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

app = Flask(__name__)

# Load data
cars_df = pd.read_csv('data/cars.csv')
ratings_df = pd.read_csv('data/ratings.csv')
users_df = pd.read_csv('data/users.csv')

# Prepare data for Surprise
reader = Reader(rating_scale=(1, 5))
data = Dataset.load_from_df(ratings_df[['user_id', 'car_id', 'rating']], reader)
trainset = data.build_full_trainset()

# Train KNN model with cosine similarity
sim_options = {
    'name': 'cosine',
    'user_based': True  # User-based collaborative filtering
}
knn_user = KNNBasic(sim_options=sim_options, verbose=False)  # Suppress logs
knn_user.fit(trainset)

# Also train item-based model
sim_options_item = {
    'name': 'cosine',
    'user_based': False  # Item-based collaborative filtering
}
knn_item = KNNBasic(sim_options=sim_options_item, verbose=False)  # Suppress logs
knn_item.fit(trainset)

# Content-based filtering
# Create feature representation for cars
cars_df['features'] = cars_df['car_make'] + ' ' + cars_df['car_models'] + ' ' + cars_df['car_type'] + ' ' + cars_df['fuel_type'] + ' ' + cars_df['transmission_type']
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(cars_df['features'])
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# Route for home page (index.html)
@app.route('/')
@app.route('/index')
@app.route('/index.html')
def index():
    return render_template('index.html')

# Route for recommendation page
@app.route('/rent')
@app.route('/rent.html')
def rent_page():
    # Get unique values for dropdowns
    car_types = sorted(cars_df['car_type'].unique())
    fuel_types = sorted(cars_df['fuel_type'].unique())
    transmission_types = sorted(cars_df['transmission_type'].unique())
    user_ids = sorted(users_df['user_id'].unique())
    car_models = sorted(cars_df['car_models'].unique())
    car_makes = sorted(cars_df['car_make'].unique())
    return render_template('rent.html', 
                           car_types=car_types,
                           fuel_types=fuel_types,
                           transmission_types=transmission_types,
                           user_ids=user_ids,
                           car_models=car_models,
                           car_makes=car_makes)

# Route for services page
@app.route('/services')
@app.route('/services.html')
def services_page():
    return render_template('services.html')

# Route for contact page
@app.route('/contact')
@app.route('/contact.html')
def contact_page():
    return render_template('contact.html')

# Function to get content-based recommendations
def get_content_based_recommendations(preferences, top_n=5):
    # Filter cars based on user preferences
    filtered_cars = cars_df.copy()
    
    # Only apply filters for non-empty preferences
    if preferences.get('car_models') and preferences['car_models'] != "":
        filtered_cars = filtered_cars[filtered_cars['car_models'] == preferences['car_models']]
    
    if preferences.get('car_makes') and preferences['car_makes'] != "":
        filtered_cars = filtered_cars[filtered_cars['car_make'] == preferences['car_makes']]  # Note: column is 'car_make' not 'car_makes'

    if preferences.get('car_type') and preferences['car_type'] != "":
        filtered_cars = filtered_cars[filtered_cars['car_type'] == preferences['car_type']]
    
    if preferences.get('fuel_type') and preferences['fuel_type'] != "":
        filtered_cars = filtered_cars[filtered_cars['fuel_type'] == preferences['fuel_type']]
        
    if preferences.get('transmission_type') and preferences['transmission_type'] != "":
        filtered_cars = filtered_cars[filtered_cars['transmission_type'] == preferences['transmission_type']]
    
    # If no cars match the criteria or no filters were applied, return a sample of cars
    if filtered_cars.empty:
        return cars_df.sample(min(top_n, len(cars_df))).to_dict('records')
    
    # Return the filtered cars
    return filtered_cars.head(top_n).to_dict('records')

# Function to get collaborative filtering recommendations
def get_collaborative_recommendations(user_id, top_n=5):
    try:
        user_id = int(user_id)
        # Get all cars not rated by the user
        all_car_ids = cars_df['car_id'].unique()
        user_ratings = ratings_df[ratings_df['user_id'] == user_id]['car_id'].unique()
        unrated_cars = np.setdiff1d(all_car_ids, user_ratings)
        
        # Get predictions for user
        predictions = []
        for car_id in unrated_cars:
            predictions.append((car_id, knn_user.predict(user_id, car_id).est))
        
        # Sort by estimated rating
        predictions.sort(key=lambda x: x[1], reverse=True)
        
        # Get top N car IDs
        top_car_ids = [pred[0] for pred in predictions[:top_n]]
        
        # Return car details
        return cars_df[cars_df['car_id'].isin(top_car_ids)].to_dict('records')
    except Exception as e:
        print(f"Error in collaborative recommendations: {e}")
        # Return random cars if there's an error
        return cars_df.sample(min(top_n, len(cars_df))).to_dict('records')

# Function to get item-based recommendations
def get_item_based_recommendations(user_id, top_n=5):
    try:
        user_id = int(user_id)
        # Get cars rated by the user
        user_rated_cars = ratings_df[ratings_df['user_id'] == user_id]['car_id'].unique()
        
        if len(user_rated_cars) == 0:
            return cars_df.sample(min(top_n, len(cars_df))).to_dict('records')
        
        # Get all cars not rated by the user
        all_car_ids = cars_df['car_id'].unique()
        unrated_cars = np.setdiff1d(all_car_ids, user_rated_cars)
        
        # Get predictions for user based on item similarity
        predictions = []
        for car_id in unrated_cars:
            predictions.append((car_id, knn_item.predict(user_id, car_id).est))
        
        # Sort by estimated rating
        predictions.sort(key=lambda x: x[1], reverse=True)
        
        # Get top N car IDs
        top_car_ids = [pred[0] for pred in predictions[:top_n]]
        
        # Return car details
        return cars_df[cars_df['car_id'].isin(top_car_ids)].to_dict('records')
    except Exception as e:
        print(f"Error in item-based recommendations: {e}")
        # Return random cars if there's an error
        return cars_df.sample(min(top_n, len(cars_df))).to_dict('records')

# Function to get purchase-based recommendations
def get_purchase_based_recommendations(user_id, top_n=5):
    try:
        # Chargement du fichier CSV des achats
        purchase_data = pd.read_csv('data/purchases.csv')
        print(f"Loaded purchase data:\n{purchase_data.head()}")  # Log des données
    except FileNotFoundError:
        print("File not found, returning empty recommendations.")
        return []

    try:
        # Convertir user_id dans le CSV en entier pour éviter les problèmes de type
        purchase_data['user_id'] = purchase_data['user_id'].astype(int)
        
        # Convertir user_id de la requête en entier
        user_id = int(user_id)

        # Vérifier le type et la valeur de user_id avant de filtrer
        print(f"Checking purchases for user_id: {user_id} (type: {type(user_id)})")

        # Filtrer les achats de l'utilisateur
        user_purchases = purchase_data[purchase_data['user_id'] == user_id]
        print(f"User ID: {user_id} Purchases:\n{user_purchases}")  # Log des achats filtrés

        # Si l'utilisateur n'a effectué aucun achat, retourner une liste vide d'informations de voitures
        if user_purchases.empty:
            print(f"No purchases found for User ID: {user_id}")
            return cars_df.sample(min(top_n, len(cars_df))).to_dict('records')  # Retourner des voitures aléatoires

        # Obtenir les IDs des voitures achetées
        purchased_car_ids = user_purchases['car_id'].tolist()
        print(f"Purchased car IDs: {purchased_car_ids}")

        # Pour une recommandation simple, on retourne les détails des voitures achetées
        # Limité à top_n voitures
        recommended_cars = cars_df[cars_df['car_id'].isin(purchased_car_ids[:top_n])]
        
        # Convertir en dictionnaire pour cohérence avec les autres fonctions de recommandation
        return recommended_cars.to_dict('records')
    except Exception as e:
        print(f"Error in get_purchase_based_recommendations: {e}")
        # En cas d'erreur, retourner des voitures aléatoires
        return cars_df.sample(min(top_n, len(cars_df))).to_dict('records')

# Function to get hybrid recommendations
def get_hybrid_recommendations(user_id, preferences, top_n=5):
    # Get content-based and collaborative filtering recommendations
    content_recs = get_content_based_recommendations(preferences, top_n=top_n*2)
    collab_recs = get_collaborative_recommendations(user_id, top_n=top_n*2)
    item_recs = get_item_based_recommendations(user_id, top_n=top_n*2)
    history_recs = get_purchase_based_recommendations(user_id, top_n=top_n*2)
    
    # Combine and score recommendations
    all_recs = {}
    
    # Score content-based recommendations
    for i, car in enumerate(content_recs):
        car_id = car['car_id']
        if car_id not in all_recs:
            all_recs[car_id] = {'car': car, 'score': 0}
        all_recs[car_id]['score'] += (top_n*2 - i) / (top_n*2) * 0.3  # 30% weight for content-based
    
    # Score user-based collaborative recommendations
    for i, car in enumerate(collab_recs):
        car_id = car['car_id']
        if car_id not in all_recs:
            all_recs[car_id] = {'car': car, 'score': 0}
        all_recs[car_id]['score'] += (top_n*2 - i) / (top_n*2) * 0.25  # 25% weight for user-based collab
    
    # Score item-based collaborative recommendations
    for i, car in enumerate(item_recs):
        car_id = car['car_id']
        if car_id not in all_recs:
            all_recs[car_id] = {'car': car, 'score': 0}
        all_recs[car_id]['score'] += (top_n*2 - i) / (top_n*2) * 0.25  # 25% weight for item-based collab
    
    # Score history-based recommendations
    for i, car in enumerate(history_recs):
        car_id = car['car_id']
        if car_id not in all_recs:
            all_recs[car_id] = {'car': car, 'score': 0}
        all_recs[car_id]['score'] += (top_n*2 - i) / (top_n*2) * 0.2  # 20% weight for history-based
    
    # Sort by final score
    sorted_recs = sorted(all_recs.values(), key=lambda x: x['score'], reverse=True)
    
    # Return top N recommendations
    recommendations = [rec['car'] for rec in sorted_recs[:top_n]]
    
    # If no recommendations were found, return a sample of cars
    if not recommendations:
        return cars_df.sample(min(top_n, len(cars_df))).to_dict('records')
    
    return recommendations

# Route to get recommendations
@app.route('/recommend', methods=['POST'])
def recommend():
    # Get JSON data from the request
    data = request.json

    # Check if 'user_id' is present in the request
    user_id = data.get('user_id')
    if user_id is None:
        return jsonify({"error": "'user_id' is required"}), 400  # Return error if 'user_id' is missing
    
    # Get other preferences using .get() to avoid KeyError if keys are missing
    preferences = {
        'car_models': data.get('car_models'),
        'car_makes': data.get('car_makes'),
        'car_type': data.get('car_type'),
        'fuel_type': data.get('fuel_type'),
        'transmission_type': data.get('transmission_type')
    }

    # Display received data for debugging (optional)
    print(f"Received data: {data}")
    
    # Get recommendations for all types
    content_recs = get_content_based_recommendations(preferences)
    collab_recs = get_collaborative_recommendations(user_id)
    hybrid_recs = get_hybrid_recommendations(user_id, preferences)
    history_recs = get_purchase_based_recommendations(user_id)

    # Return recommendations as JSON
    return jsonify({
        'content_based': content_recs,
        'collaborative_filtering': collab_recs,
        'hybrid': hybrid_recs,
        'history_based': history_recs
    })

if __name__ == '__main__':
    app.run(debug=True)