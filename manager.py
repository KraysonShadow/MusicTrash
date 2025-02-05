import sys
from owlready2 import sync_reasoner
from app.utils.ontology import ontology

ontology_path = "app/utils/music.rdf"

def add_instrument():
    name = input("Введите название нового инструмента: ").strip()
    
    instrument_class = ontology.search_one(iri="*Инструмент")
    categories = list(instrument_class.subclasses())
    
    if not categories:
        print("Ошибка: В онтологии нет доступных категорий инструментов.")
        return
    
    print("Доступные категории инструментов:")
    for i, category in enumerate(categories, 1):
        print(f"{i}. {category.name}")
    
    choice = input("Выберите номер категории: ").strip()
    try:
        category_class = categories[int(choice) - 1]
    except (IndexError, ValueError):
        print("Ошибка: Неверный выбор.")
        return
    
    with ontology:
        new_instrument = category_class(name)
        ontology.save(ontology_path)
        sync_reasoner()
    
    print(f"Инструмент '{name}' добавлен в онтологию под категорию '{category_class.name}'.")

def delete_instrument():
    instruments = list(ontology.search(type=ontology.search_one(iri="*Инструмент")))
    
    if not instruments:
        print("В онтологии нет инструментов.")
        return
    
    print("\nСписок инструментов:")
    for idx, instrument in enumerate(instruments, 1):
        print(f"{idx}. {instrument.name}")
    
    choice = input("Выберите номер инструмента для удаления (или 0 для выхода): ").strip()
    if choice == "0":
        return
    
    try:
        selected_instrument = instruments[int(choice) - 1]
    except (IndexError, ValueError):
        print("Ошибка: Неверный выбор.")
        return
    
    with ontology:
        ontology.destroy_entity(selected_instrument)
        ontology.save(ontology_path)
        sync_reasoner()
    
    print(f"Инструмент '{selected_instrument.name}' удалён из онтологии.")

def adjust_weights():
    genres = list(ontology.search(type=ontology.Жанр))
    instruments = list(ontology.search(type=ontology.search_one(iri="*Инструмент")))
    
    if not instruments:
        print("В онтологии нет инструментов.")
        return
    
    print("\nСписок инструментов и их соответствие жанрам:")
    for idx, instrument in enumerate(instruments, 1):
        weights = []
        for genre in genres:
            genre_weight_prop = f"Вес_жанра_{genre.name}"
            weight = getattr(instrument, genre_weight_prop, None)
            if weight and isinstance(weight, list) and weight:
                weights.append(f"{genre.name}: {weight[0]}")
        weights_str = ", ".join(weights) if weights else "Нет данных"
        print(f"{idx}. {instrument.name} - {weights_str}")
    
    choice = input("Выберите номер инструмента для настройки веса (или 0 для выхода): ").strip()
    if choice == "0":
        return
    
    try:
        selected_instrument = instruments[int(choice) - 1]
    except (IndexError, ValueError):
        print("Ошибка: Неверный выбор.")
        return
    
    print(f"Вы выбрали инструмент: {selected_instrument.name}")
    weights = []
    for genre in genres:
        genre_weight_prop = f"Вес_жанра_{genre.name}"
        weight = getattr(selected_instrument, genre_weight_prop, None)
        if weight and isinstance(weight, list) and weight:
            weights.append(f"{genre.name}: {weight[0]}")
    weights_str = ", ".join(weights) if weights else "Нет данных"
    print(f"Текущие веса: {weights_str}")
    
    print("Доступные жанры:")
    for i, genre in enumerate(genres, 1):
        print(f"{i}. {genre.name}")
    
    genre_choice = input("Выберите номер жанра для настройки: ").strip()
    try:
        selected_genre = genres[int(genre_choice) - 1]
    except (IndexError, ValueError):
        print("Ошибка: Неверный выбор.")
        return
    
    weight = input("Введите вес соответствия (0.0 - 1.0): ").strip()
    try:
        weight = float(weight)
        if weight < 0.0 or weight > 1.0:
            raise ValueError
    except ValueError:
        print("Ошибка: Некорректный ввод веса.")
        return
    
    genre_weight_prop = f"Вес_жанра_{selected_genre.name}"
    
    with ontology:
        if weight == 0.0:
            if hasattr(selected_instrument, "Подходит_жанру") and selected_genre in getattr(selected_instrument, "Подходит_жанру", []):
                getattr(selected_instrument, "Подходит_жанру").remove(selected_genre)
            if hasattr(selected_instrument, genre_weight_prop):
                setattr(selected_instrument, genre_weight_prop, [])
        else:
            setattr(selected_instrument, genre_weight_prop, [weight])
            if selected_genre not in getattr(selected_instrument, "Подходит_жанру", []):
                getattr(selected_instrument, "Подходит_жанру").append(selected_genre)
        
        ontology.save(ontology_path)
        sync_reasoner()
    
    print(f"Вес для инструмента '{selected_instrument.name}' и жанра '{selected_genre.name}' обновлён до {weight}.")

def main():
    while True:
        print("\nМеню:")
        print("1. Добавить инструмент")
        print("2. Удалить инструмент")
        print("3. Настроить веса")
        print("4. Выход")
        choice = input("Выберите действие: ").strip()
        
        if choice == "1":
            add_instrument()
        elif choice == "2":
            delete_instrument()
        elif choice == "3":
            adjust_weights()
        elif choice == "4":
            print("Выход из программы.")
            sys.exit()
        else:
            print("Ошибка: Неверный ввод. Попробуйте снова.")

if __name__ == "__main__":
    main()