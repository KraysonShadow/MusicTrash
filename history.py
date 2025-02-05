import json
import os
import random
from owlready2 import get_ontology, sync_reasoner
from app.utils.fuzzy import evaluate_genres


# Функция для сохранения данных в JSON
def save_to_json(selected_artists, sorted_instruments, selected_instrument):
    data = {
        "selected_artists": [artist.name for artist in selected_artists],
        "recommended_instruments": [instrument[0] for instrument in sorted_instruments],
        "selected_instrument": selected_instrument
    }
    
    # Загружаем существующие данные, если файл существует
    existing_data = []
    if os.path.exists("user_selection.json"):
        with open("user_selection.json", "r", encoding="utf-8") as file:
            try:
                existing_data = json.load(file)
            except json.JSONDecodeError:
                existing_data = []
    
    # Добавляем новые данные
    existing_data.append(data)
    
    # Сохраняем обновленные данные обратно в файл
    with open("user_selection.json", "w", encoding="utf-8") as file:
        json.dump(existing_data, file, ensure_ascii=False, indent=4)

# Функция для загрузки данных из JSON
def load_data(json_file):
    try:
        with open(json_file, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Функция для выбора случайных исполнителей и инструмента
def generate_music_selection(ontology):
    artists = list(ontology.Исполнитель.instances())
    instruments = list(ontology.Инструмент.instances())
    
    # Выбираем от 1 до 6 случайных исполнителей
    selected_artists = random.sample(artists, random.randint(1, 6))
    
    # Первый выбранный исполнитель определяет жанр
    main_artist = selected_artists[0]
    possible_genres = list(main_artist.Играет_в_жанре)
    selected_genre = random.choice(possible_genres) if possible_genres else None
    
    # Оставшиеся исполнители с 90% вероятностью играют в том же жанре
    for i in range(1, len(selected_artists)):
        if random.random() > 0.9:
            other_genres = list(selected_artists[i].Играет_в_жанре)
            if other_genres:
                selected_genre = random.choice(other_genres)
    
    # Выбираем случайный инструмент
    selected_instrument = random.choice(instruments)
    
    # 90% вероятности, что инструмент подходит жанру
    if selected_genre and random.random() > 0.9:
        suitable_instruments = [instr for instr in instruments if selected_genre in instr.Подходит_жанру]
        if suitable_instruments:
            selected_instrument = random.choice(suitable_instruments)
    
    return {
        "selected_artists": selected_artists,
        "recommended_instruments": [(None, None)],
        "selected_instrument": selected_instrument.name
    }

def data_generator(ontology, n = 800, json_file="user_selection.json"):
    for i in range(n):
        data = generate_music_selection(ontology)
        save_to_json(data['selected_artists'], data['recommended_instruments'], data['selected_instrument'])

if __name__ == "__main__":
    # Загружаем онтологию
    ontology = get_ontology("app/utils/music.rdf").load()
    data_generator(ontology)
    