from sklearn.ensemble import GradientBoostingClassifier
import numpy as np
from history import load_data
from app.utils.ontology import get_all_instruments

def train_from_json(json_file="user_selection.json"):
    data = load_data(json_file)
    if not data:
        print("Недостаточно данных для обучения модели.")
        return None, None, None
    
    artists_sets = []
    instruments = []
    
    for entry in data:
        artists_sets.append(entry["selected_artists"])
        instruments.append(entry["selected_instrument"])
    
    unique_artists = list(set(artist for artists in artists_sets for artist in artists))
    #unique_instruments = list([instrument.name for instrument in get_all_instruments()])
    unique_instruments = list(set(instruments))
    artist_to_index = {artist: i for i, artist in enumerate(unique_artists)}
    instrument_to_index = {instrument: i for i, instrument in enumerate(unique_instruments)}
    
    feature_matrix = np.zeros((len(artists_sets), len(unique_artists)))
    target_vector = np.array([instrument_to_index[instr] for instr in instruments])
    
    for i, artists in enumerate(artists_sets):
        for artist in artists:
            feature_matrix[i, artist_to_index[artist]] = 1
    
    gb = GradientBoostingClassifier(n_estimators=50, learning_rate=0.05, max_depth=2)
    gb.fit(feature_matrix, target_vector)
    
    return gb, artist_to_index, unique_instruments

def recommend_instruments(gb, artist_to_index, instruments, selected_artists):
    if gb is None or not selected_artists:
        print("Ошибка: модель не обучена или список исполнителей пуст.")
        return []
    
    input_vector = np.zeros(len(artist_to_index))
    for artist in selected_artists:
        if artist.name in artist_to_index:
            input_vector[artist_to_index[artist.name]] = 1
    probabilities = gb.predict_proba([input_vector])[0]
    top_indices = np.argsort(probabilities)[-5:][::-1]
    recommendations = [(instruments[idx], probabilities[idx]) for idx in top_indices]
    # Нормализация весов рекомендаций
    min_weight = min(probabilities)
    max_weight = max(probabilities)
    if max_weight == min_weight:
        normalized_recommendations = [(name, 1.0) for name, _ in recommendations]
    else:
        normalized_recommendations = [
            (name, (weight - min_weight) / (max_weight - min_weight))
            for name, weight in recommendations
        ]
    return normalized_recommendations
