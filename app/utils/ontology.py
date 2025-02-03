from owlready2 import get_ontology, sync_reasoner

# Загружаем онтологию
ontology = get_ontology("app/utils/music.owl").load()


with ontology:
    sync_reasoner()


def get_instruments(artists: list[str]) -> list[str]:
    """
    Получает список музыкальных инструментов по именам исполнителей.
    """
    instruments = set() 

    for artist in ontology.Исполнитель.instances():
        if artist.name in artists:
            for genre in artist.Играет_в_жанре:
                for instrument in ontology.Инструмент.instances():
                    if genre in instrument.Подходит_жанру:
                        instruments.add(instrument) 

    return list(instruments) 
