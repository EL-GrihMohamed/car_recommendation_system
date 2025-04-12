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

# Define valid user IDs
VALID_USER_IDS = ["P100088", "L200079", "G300057", "P400044", "L500046"]

# Prepare data for Surprise
reader = Reader(rating_scale=(1, 5))
data = Dataset.load_from_df(ratings_df[['user_id', 'car_id', 'rating']], reader)
trainset = data.build_full_trainset()


sim_options = {
    'name': 'cosine', # Mesure de similarité
    'user_based': True # Mode de filtrage basé sur les utilisateurs
}
knn_user = KNNBasic(sim_options=sim_options, verbose=False)  
knn_user.fit(trainset)

# Also train item-based model
sim_options_item = {
    'name': 'cosine',
    'user_based': False  # Filtrage collaboratif basé sur les items
}
knn_item = KNNBasic(sim_options=sim_options_item, verbose=False)  
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
def rent():
    # Define your data
    alpha_user_ids = {
        1: "P100088", 
        2: "L200079", 
        3: "G300057", 
        4: "P400044", 
        5: "L500046"
    }
    car_makes = ['Toyota', 'Honda', 'Ford', 'BMW', 'Mercedes', 'Audi', 'Volkswagen', 'Nissan', 'Hyundai', 'Kia']
    car_models = ['Sedan', 'SUV', 'Hatchback', 'Coupe', 'Convertible', 'Wagon', 'Truck', 'Van']
    car_types = ['Economy', 'Compact', 'Mid-size', 'Full-size', 'Luxury', 'Sport', 'SUV', 'Minivan']
    fuel_types = ['Gasoline', 'Electric', 'Hybrid', 'Diesel']
    transmission_types = ['Automatic', 'Manual', 'CVT']
    
    # Pass all variables to the template
    return render_template('rent.html', 
                          alpha_user_ids=alpha_user_ids,
                          car_makes=car_makes, 
                          car_models=car_models,
                          car_types=car_types,
                          fuel_types=fuel_types,
                          transmission_types=transmission_types)

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
    # Filtrer les voitures selon les préférences utilisateur
    filtered_cars = cars_df.copy()
    
    # Appliquer uniquement les filtres pour les préférences non vides
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
    
    # Si aucune voiture ne correspond aux critères ou aucun filtre n'a été appliqué, retourner un échantillon
    if filtered_cars.empty:
        return cars_df.sample(min(top_n, len(cars_df))).to_dict('records')
    # Retourner les voitures filtrées
    return filtered_cars.head(top_n).to_dict('records')

def get_collaborative_recommendations(user_id, top_n=5):
    try:
        # Obtenir toutes les voitures non évaluées par l'utilisateur
        all_car_ids = cars_df['car_id'].unique()
        user_ratings = ratings_df[ratings_df['user_id'] == user_id]['car_id'].unique()
        unrated_cars = np.setdiff1d(all_car_ids, user_ratings)
        
        # Générer des prédictions pour l'utilisateur
        predictions = []
        for car_id in unrated_cars:
            predictions.append((car_id, knn_user.predict(user_id, car_id).est))
        
        # Trier par évaluation estimée
        predictions.sort(key=lambda x: x[1], reverse=True)
        
        # Obtenir les IDs des N meilleures voitures
        top_car_ids = [pred[0] for pred in predictions[:top_n]]
        
        # Retourner les détails des voitures
        return cars_df[cars_df['car_id'].isin(top_car_ids)].to_dict('records')
    except Exception as e:
        print(f"Error in collaborative recommendations: {e}")
        # Return random cars if there's an error
        return cars_df.sample(min(top_n, len(cars_df))).to_dict('records')

# Function to get item-based recommendations
def get_item_based_recommendations(user_id, top_n=5):
    try:
        # Obtenir les voitures évaluées par l'utilisateur
        user_rated_cars = ratings_df[ratings_df['user_id'] == user_id]['car_id'].unique()
        
        if len(user_rated_cars) == 0:
            return cars_df.sample(min(top_n, len(cars_df))).to_dict('records')
        
        # Obtenir les voitures non évaluées
        all_car_ids = cars_df['car_id'].unique()
        unrated_cars = np.setdiff1d(all_car_ids, user_rated_cars)
        
        # Générer des prédictions basées sur la similarité entre items
        predictions = []
        for car_id in unrated_cars:
            predictions.append((car_id, knn_item.predict(user_id, car_id).est))
        
        # Trier par évaluation estimée
        predictions.sort(key=lambda x: x[1], reverse=True)
        
        # Obtenir les IDs des N meilleures voitures
        top_car_ids = [pred[0] for pred in predictions[:top_n]]
        
        # Retourner les détails des voitures
        return cars_df[cars_df['car_id'].isin(top_car_ids)].to_dict('records')
    except Exception as e:
        print(f"Error in item-based recommendations: {e}")
        # Retourner des voitures aléatoires en cas d'erreur
        return cars_df.sample(min(top_n, len(cars_df))).to_dict('records')

# Fonction pour obtenir des recommandations basées sur les achats
def get_purchase_based_recommendations(user_id, top_n=5):
    try:
        # Chargement des données d'achat depuis le fichier CSV
        purchase_data = pd.read_csv('data/purchases.csv')
        print(f"Données d'achat chargées :\n{purchase_data.head()}")  # Journalisation des données
    except FileNotFoundError:
        print("Fichier introuvable, retour de recommandations vides.")
        return []

    try:
        # Filtrage des achats pour l'utilisateur spécifié
        print(f"Vérification des achats pour user_id : {user_id} (type : {type(user_id)})")

        # Filtrer les achats de l'utilisateur
        user_purchases = purchase_data[purchase_data['user_id'] == user_id]
        print(f"Achats pour l'utilisateur {user_id} :\n{user_purchases}")  # Journalisation des achats filtrés

        # Si l'utilisateur n'a pas d'historique d'achat, retourner des voitures aléatoires
        if user_purchases.empty:
            print(f"Aucun achat trouvé pour l'utilisateur {user_id}")
            return cars_df.sample(min(top_n, len(cars_df))).to_dict('records')  # Retour de voitures aléatoires

        # Obtenir les IDs des voitures achetées
        purchased_car_ids = user_purchases['car_id'].tolist()
        print(f"IDs des voitures achetées : {purchased_car_ids}")

        # Pour une recommandation simple, retourner les détails des voitures achetées
        # Limité aux top_n voitures
        recommended_cars = cars_df[cars_df['car_id'].isin(purchased_car_ids[:top_n])]
        
        # Conversion en dictionnaire pour rester cohérent avec les autres fonctions de recommandation
        return recommended_cars.to_dict('records')
    except Exception as e:
        print(f"Erreur dans get_purchase_based_recommendations : {e}")
        # En cas d'erreur, retourner des voitures aléatoires
        return cars_df.sample(min(top_n, len(cars_df))).to_dict('records')

# Fonction pour obtenir des recommandations hybrides
def get_hybrid_recommendations(user_id, preferences, top_n=5):
    # Obtenir les recommandations basées sur le contenu et sur le filtrage collaboratif
    content_recs = get_content_based_recommendations(preferences, top_n=top_n*2)
    collab_recs = get_collaborative_recommendations(user_id, top_n=top_n*2)
    item_recs = get_item_based_recommendations(user_id, top_n=top_n*2)
    history_recs = get_purchase_based_recommendations(user_id, top_n=top_n*2)
    
    # Combiner et attribuer un score aux recommandations
    all_recs = {}
    
    # Attribuer un score aux recommandations basées sur le contenu
    for i, car in enumerate(content_recs):
        car_id = car['car_id']
        if car_id not in all_recs:
            all_recs[car_id] = {'car': car, 'score': 0}
        all_recs[car_id]['score'] += (top_n*2 - i) / (top_n*2) * 0.3  # Pondération de 30% pour le contenu

    # Attribuer un score aux recommandations collaboratives basées sur les utilisateurs
    for i, car in enumerate(collab_recs):
        car_id = car['car_id']
        if car_id not in all_recs:
            all_recs[car_id] = {'car': car, 'score': 0}
        all_recs[car_id]['score'] += (top_n*2 - i) / (top_n*2) * 0.25  # Pondération de 25% pour les utilisateurs similaires

    # Attribuer un score aux recommandations collaboratives basées sur les items
    for i, car in enumerate(item_recs):
        car_id = car['car_id']
        if car_id not in all_recs:
            all_recs[car_id] = {'car': car, 'score': 0}
        all_recs[car_id]['score'] += (top_n*2 - i) / (top_n*2) * 0.25  # Pondération de 25% pour les items similaires

    # Attribuer un score aux recommandations basées sur l'historique d'achat
    for i, car in enumerate(history_recs):
        car_id = car['car_id']
        if car_id not in all_recs:
            all_recs[car_id] = {'car': car, 'score': 0}
        all_recs[car_id]['score'] += (top_n*2 - i) / (top_n*2) * 0.2  # Pondération de 20% pour l'historique

    # Trier par score final
    sorted_recs = sorted(all_recs.values(), key=lambda x: x['score'], reverse=True)
    
    # Retourner les top N recommandations
    recommendations = [rec['car'] for rec in sorted_recs[:top_n]]
    
    # Si aucune recommandation trouvée, retourner un échantillon de voitures
    if not recommendations:
        return cars_df.sample(min(top_n, len(cars_df))).to_dict('records')
    
    return recommendations

# Route pour obtenir des recommandations
@app.route('/recommend', methods=['POST'])
def recommend():
    # Récupérer les données JSON de la requête
    data = request.json

    # Vérifier si 'user_id' est présent dans la requête
    user_id = data.get('user_id')
    if user_id is None:
        return jsonify({"error": "'user_id' est requis"}), 400  # Retourner une erreur si 'user_id' est manquant
    
    # Vérifier si l'identifiant de l'utilisateur est valide
    if user_id not in VALID_USER_IDS:
        return jsonify({"error": "ID utilisateur invalide. Veuillez utiliser l’un des IDs fournis."}), 400
    
    # Récupérer les autres préférences en utilisant .get() pour éviter les erreurs de type KeyError
    preferences = {
        'car_models': data.get('car_models'),
        'car_makes': data.get('car_makes'),
        'car_type': data.get('car_type'),
        'fuel_type': data.get('fuel_type'),
        'transmission_type': data.get('transmission_type')
    }

    # Afficher les données reçues pour le débogage (optionnel)
    print(f"Données reçues : {data}")
    
    # Obtenir les recommandations pour chaque type
    content_recs = get_content_based_recommendations(preferences)  # Basées sur le contenu
    collab_recs = get_collaborative_recommendations(user_id)       # Filtrage collaboratif
    hybrid_recs = get_hybrid_recommendations(user_id, preferences) # Méthode hybride
    history_recs = get_purchase_based_recommendations(user_id)     # Basées sur l'historique d'achats

    # Retourner les recommandations au format JSON
    return jsonify({
        'content_based': content_recs,
        'collaborative_filtering': collab_recs,
        'hybrid': hybrid_recs,
        'history_based': history_recs
    })

if __name__ == '__main__':
    app.run(debug=True)
