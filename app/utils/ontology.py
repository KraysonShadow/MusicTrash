from owlready2 import get_ontology, sync_reasoner

# Загружаем онтологию
ontology = get_ontology("app/utils/music.owl").load()

def get_instruments(artists: list[str]) -> list[str]:
    """
    Получает список музыкальных инструментов по именам исполнителей.
    """
    with ontology:
        sync_reasoner()  # Запуск reasoner'а (можно заменить на sync_reasoner_hermit())

    instruments = set()  # Используем set, чтобы избежать дублирования

    for artist in ontology.Исполнитель.instances():  # Получаем всех исполнителей
        if artist.name in artists:  # Проверяем, есть ли имя в списке
            for genre in artist.Играет_в_жанре:  # Исправлена опечатка
                test = genre.Подходит_инструмент
                for instrument in genre.Подходит_инструмент:
                    instruments.add(instrument.name)  # Получаем название инструмента

    return list(instruments)  # Преобразуем в список перед возвратом
