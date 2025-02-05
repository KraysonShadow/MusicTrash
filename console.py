from app.utils.ontology import get_artists, get_genres_from_artists, get_all_instruments, get_types, search, check_type
import ml
from history import save_to_json

# Менюшка выбора любимых исполнителей
# Возвращает список любимых исполнителей
def select_artists():
    artists = get_artists()
    print("\nВыберите ваших любимых исполнителей, введя их номера через пробел:")
    for index, artist in enumerate(artists):
        print(f"{index + 1}. {artist.name}")

    selected_artists = []
    selected_indices = set(input("Ввод номеров: ").strip().split())

    try:
        selected_artists = [artists[int(i) - 1] for i in selected_indices]
        print("\nВы выбрали следующих исполнителей:")
        for artist in selected_artists:
            print(f"- {artist.name}")
    except (ValueError, IndexError):
        print("Ошибка ввода.")
    return selected_artists

def select_type(instruments):
    selected_types = []
    all_types = list(get_types())
    filtered_types = []
    for type in all_types:
        if any(check_type(search(iri=f"*{instrument}"), type) for instrument in instruments):
            filtered_types.append(type)
    if filtered_types == []:
        return []
    print("\nВыберите предпочитаемые типы инструментов, введя их номера через пробел, или введите 0, что пропустить этот шаг.")
    for index, type in enumerate(filtered_types):
        print(f"{index + 1}. {type.name}")

    selected_indices = set(input("Ввод номеров: ").strip().split())
    if "0" not in selected_indices:
        try:
            selected_types = [filtered_types[int(i) - 1] for i in selected_indices]
            print("\nВы выбрали следующие типы инструментов:")
            for type in selected_types:
                print(f"- {type.name}")
        except (ValueError, IndexError):
            print("Ошибка ввода.")
    else: print("\nВыбор типа инструмента пропущен.")
    return selected_types

def ml_menu():
    model, artist_to_index, instruments = ml.train_from_json()
    if model: selected_artists = select_artists()
    else: selected_artists = []
    if (selected_artists != []):
        recommendations = ml.recommend_instruments(model, artist_to_index, instruments, selected_artists)
        # Вывод инструментов пользователю
        while True:
            print("\nВам могут подойти следующие инструменты:")
            show_amount = 5
            for index, instrument in enumerate(recommendations[:show_amount], start=1):
                print(f"{index}. {instrument[0]} ({instrument[1]:.2f})")

            print("Введите номер инструмента, который вы выбрали, или 0, если предложенные варианты не подходят.")

            selected_index = input("Ввод номера: ").strip()
        
            if selected_index == "0":
                while True:
                    all_instruments = get_all_instruments()
                    print("\nВсе доступные инструменты:")
                    for index, instrument in enumerate(all_instruments, start=1):
                        print(f"{index}. {instrument.name}")
                    print("Помогите скорректировать систему, введя номер инструмента, который вам подходит. Если хотите выйти, введите 0.")
                    selected_index = input("Ввод номера: ").strip()
                    if selected_index == "0":
                        break
                    else:
                        try:
                            selected_index = int(selected_index)
                            if 1 <= selected_index <= len(all_instruments):
                                selected_instrument = all_instruments[selected_index - 1].name
                                print(f"Вы выбрали инструмент: {selected_instrument}")
                                save_to_json(selected_artists, recommendations, selected_instrument)
                                break
                            else:
                                print("Некорректный ввод. Попробуйте снова.")
                        except ValueError:
                            print("Некорректный ввод. Попробуйте снова.")
                break
            else:
                try:
                    selected_index = int(selected_index)
                    if 1 <= selected_index <= show_amount:
                        selected_instrument = recommendations[selected_index - 1][0]
                        print(f"Вы выбрали инструмент: {selected_instrument}")
                        save_to_json(selected_artists, recommendations, selected_instrument)
                        break
                    else:
                        print("Некорректный ввод. Попробуйте снова.")
                except ValueError:
                    print("Некорректный ввод. Попробуйте снова.")

# Вычисляет и выводит наиболее подходящие инструменты
def get_instruments(selected_artists):
    # Получение весов инструментов
    instrument_weights = get_genres_from_artists([artist.name for artist in selected_artists])
    min_weight = min(instrument_weights.values())
    max_weight = max(instrument_weights.values())
    # Нормализация весов
    if max_weight == min_weight:
        normalized_instruments = {name: 1.0 for name in instrument_weights}
    else:
        normalized_instruments = {
            name: (weight - min_weight) / (max_weight - min_weight)
            for name, weight in instrument_weights.items()
        }
    
    def adjust_instrument_weights(instrument_weights, selected_types):
        for instrument_name, weight in instrument_weights.items():
            # Найти объект класса в онтологии
            instrument_class = search(iri=f"*{instrument_name}")
            if instrument_class:
                # Проверить, является ли инструмент подклассом одного из выбранных типов
                if any(check_type(instrument_class, t) for t in selected_types):
                    instrument_weights[instrument_name] += 0.4  # Увеличиваем вес
                else:
                    instrument_weights[instrument_name] -= 0.4  # Уменьшаем вес
        # Нормализация весов
        min_weight = min(instrument_weights.values())
        max_weight = max(instrument_weights.values())
        if max_weight == min_weight:
            instrument_weights = {name: 1.0 for name in instrument_weights}
        else:
            instrument_weights = {
                name: (weight - min_weight) / (max_weight - min_weight)
                for name, weight in instrument_weights.items()
            }
        return instrument_weights
    
    selected_types = select_type(normalized_instruments)
    # Корректируем веса по типу инструмента
    if selected_types != []:
        normalized_instruments = adjust_instrument_weights(normalized_instruments, selected_types)

    # Сортируем инструменты по нормализованным весам в порядке убывания
    sorted_instruments = sorted(
        ((name, weight) for name, weight in normalized_instruments.items() if weight > 0),
        key=lambda x: x[1], 
        reverse=True
    )

    # Вывод инструментов пользователю
    while True:
        print("\nВам могут подойти следующие инструменты:")
        show_amount = 5
        for index, instrument in enumerate(sorted_instruments[:show_amount], start=1):
            print(f"{index}. {instrument[0]} ({instrument[1]:.2f})")

        print("Введите номер инструмента, который вы выбрали, или 0, если предложенные варианты не подходят.")

        selected_index = input("Ввод номера: ").strip()
    
        if selected_index == "0":
            while True:
                instruments = get_all_instruments()
                print("\nВсе доступные инструменты:")
                for index, instrument in enumerate(instruments, start=1):
                    print(f"{index}. {instrument.name}")
                print("Помогите скорректировать систему, введя номер инструмента, который вам подходит. Если хотите выйти, введите 0.")
                selected_index = input("Ввод номера: ").strip()
                if selected_index == "0":
                    break
                else:
                    try:
                        selected_index = int(selected_index)
                        if 1 <= selected_index <= len(instruments):
                            selected_instrument = instruments[selected_index - 1].name
                            print(f"Вы выбрали инструмент: {selected_instrument}")
                            save_to_json(selected_artists, sorted_instruments, selected_instrument)
                            break
                        else:
                            print("Некорректный ввод. Попробуйте снова.")
                    except ValueError:
                        print("Некорректный ввод. Попробуйте снова.")
            break
        else:
            try:
                selected_index = int(selected_index)
                if 1 <= selected_index <= show_amount:
                    selected_instrument = sorted_instruments[selected_index - 1][0]
                    print(f"Вы выбрали инструмент: {selected_instrument}")
                    save_to_json(selected_artists, sorted_instruments, selected_instrument)
                    break
                else:
                    print("Некорректный ввод. Попробуйте снова.")
            except ValueError:
                print("Некорректный ввод. Попробуйте снова.")
    
def menu():
    # Цикл меню
    while True:
        print("\nДобро пожаловать в экспертную систему подбора музыкального инструмента!")
        print("1. Запустить систему")
        print("2. Запустить GB")
        print("3. Выйти")
        
        choice = input("Выбор пункта меню: ").strip()
        # Запуск системы
        if choice == "1":
            # Выбор исполнителей
            selected_artists = select_artists()
            if (selected_artists != []):
                get_instruments(selected_artists)
            # Если исполнители не выбраны
            else:
                print("Возвращение в главное меню...")
        # Рекомендации с KNN
        elif choice == "2":
            ml_menu()
        # Выход из приложения
        elif choice == "3":
            print("Выход из системы. До свидания!")
            break
        # Неверный ввод
        else:
            print("Некорректный ввод. Попробуйте снова.")

if __name__ == "__main__":
    menu()
