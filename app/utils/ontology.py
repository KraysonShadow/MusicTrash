from owlready2 import get_ontology, sync_reasoner
from app.utils.fuzzy import evaluate_genres

# Загружаем онтологию
ontology = get_ontology("app/utils/music.owl").load()

with ontology:
    sync_reasoner()

def get_genres_from_artists(artists: list[str]) -> list[str]:
    """
    Получает список жанров на основе любимых артистов.
    
    :param artists: Список имен любимых артистов.
    :return: Список жанров с повторениями.
    """
    genres = []
    for artist in ontology.Исполнитель.instances():
        if artist.name in artists:
            genres.extend([genre.name for genre in artist.Играет_в_жанре])
    return get_instruments_with_weights(genres)

def get_instruments_with_weights(genres: list[str]) -> list[dict]:
    """
    Получает список музыкальных инструментов с их весами на основе жанров.
    
    :param artists: Список имен любимых артистов.
    :return: Список словарей с инструментами и их весами.
    """

    # Получаем соответствие жанров
    genre_relevance = evaluate_genres(genres)
    
    # Фильтруем жанры с любой степенью соответствия
    relevant_genres = {genre: relevance for genre, relevance in genre_relevance.items()}
    
    # Словарь для накопления весов инструментов
    instrument_weights = {}

    # Вычисляем вес для каждого инструмента
    for instrument in ontology.Инструмент.instances():
        weight = 0
        for genre in instrument.Подходит_жанру:
            genre_name = genre.name
            if genre_name in relevant_genres:
                if relevant_genres[genre_name] == 'Высокое соответствие':
                    weight += 3
                elif relevant_genres[genre_name] == 'Среднее соответствие':
                    weight += 2
                elif relevant_genres[genre_name] == 'Низкое соответствие':
                    weight += 1
        if weight > 0:
            instrument_weights[instrument.name] = weight
    return instrument_weights
