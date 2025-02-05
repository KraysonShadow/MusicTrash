from owlready2 import get_ontology, sync_reasoner
from app.utils.fuzzy import evaluate_genres

# Загружаем онтологию
ontology = get_ontology("app/utils/music.rdf").load()

with ontology:
    sync_reasoner()

# Получить список исполнителей
# Использую для вывода в меню
def get_artists():
    artists = ontology.Исполнитель.instances()
    return artists

# Получить список инструментов
def get_all_instruments():
    instruments = ontology.Инструмент.instances()
    return instruments

# Получить список типов инструментов
def get_types():
    types = ontology.Инструмент.subclasses()
    return types

# Поиск объекта по имени
def search(iri):
    return ontology.search_one(iri=iri)

# Проверка наличия типа у объекта
def check_type(object, type):
    result = type in object.is_a
    return result

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
            # Получаем коэффициент жанра для инструмента
            genre_coeff_prop = f"Вес_жанра_{genre_name}"
            genre_coeff = getattr(instrument, genre_coeff_prop, None)
            if genre_coeff: 
                genre_coeff = genre_coeff[0]
            else: 
                genre_coeff = 0.0
            if genre_name in relevant_genres:
                if relevant_genres[genre_name] == 'Высокое соответствие':
                    weight += 3 * genre_coeff
                elif relevant_genres[genre_name] == 'Среднее соответствие':
                    weight += 2 * genre_coeff
                elif relevant_genres[genre_name] == 'Низкое соответствие':
                    weight += 1 * genre_coeff
        if weight > 0:
            instrument_weights[instrument.name] = weight
    return instrument_weights