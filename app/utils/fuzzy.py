import numpy as np
import skfuzzy as fuzz
from skfuzzy.control import Antecedent, Consequent, Rule, ControlSystem, ControlSystemSimulation
from collections import Counter

# Универсум дискурса: частота жанра (0 - 10)
frequency = Antecedent(np.arange(0, 12, 1), 'frequency')

# Определяем нечёткие множества
frequency['low'] = fuzz.trapmf(frequency.universe, [0, 0, 3, 5])
frequency['medium'] = fuzz.trimf(frequency.universe, [3, 5, 7])
frequency['high'] = fuzz.trapmf(frequency.universe, [5, 7, 9, 11])

# Выходная переменная: степень соответствия жанра
relevance = Consequent(np.arange(0, 12, 1), 'relevance')

# Определяем нечёткие множества для соответствия
relevance['poor'] = fuzz.trapmf(relevance.universe, [0, 0, 3, 5])
relevance['average'] = fuzz.trimf(relevance.universe, [3, 5, 7])
relevance['excellent'] = fuzz.trapmf(relevance.universe, [5, 7, 9, 11])

# Если жанр встречается редко, то соответствие низкое
rule1 = Rule(frequency['low'], relevance['poor'])

# Если жанр встречается со средней частотой, то соответствие среднее
rule2 = Rule(frequency['medium'], relevance['average'])

# Если жанр встречается часто, то соответствие высокое
rule3 = Rule(frequency['high'], relevance['excellent'])

# Создаём систему правил
genre_system = ControlSystem([rule1, rule2, rule3])
genre_sim = ControlSystemSimulation(genre_system)


def evaluate_genres(genres: list[str]) -> dict[str, str]:
    """
    Оценивает жанры на основе списка любимых артистов.
    
    :param genres: Список жанров.
    :return: Словарь с жанрами и их степенью соответствия.
    """
    
    # Подсчитываем частоту жанров
    genre_counts = Counter(genres)
    min_count = min(genre_counts.values(), default=0)
    max_count = max(genre_counts.values(), default=1)  # Чтобы избежать деления на 0

    results = {}
    for genre, count in genre_counts.items():
        # Правильная нормализация в диапазоне [0, 10]
        if max_count == min_count:
            normalized_frequency = 10  # Если все значения одинаковы, устанавливаем максимум
        else:
            normalized_frequency = ((count - min_count) / (max_count - min_count)) * 10
        
        # Устанавливаем значение частоты в симуляции
        genre_sim.input['frequency'] = normalized_frequency
        
        try:
            # Запускаем симуляцию
            genre_sim.compute()
        except Exception as e:
            raise RuntimeError(f"Ошибка в симуляции для жанра '{genre}': {e}")
        
        # Получаем степень соответствия
        if 'relevance' not in genre_sim.output:
            raise KeyError(f"Выходная переменная 'relevance' не найдена для жанра '{genre}'")
        
        score = genre_sim.output['relevance']
        
        # Интерпретируем результат
        if score < 3:
            results[genre] = 'Низкое соответствие'
        elif score < 7:
            results[genre] = 'Среднее соответствие'
        else:
            results[genre] = 'Высокое соответствие'
    
    return results


# Универсум дискурса: уровень мастерства (0 - 10)
skill_level = Antecedent(np.arange(0, 11, 1), 'skill_level')

# Определяем нечёткие множества
skill_level['novice'] = fuzz.trapmf(skill_level.universe, [0, 0, 2, 4])
skill_level['intermediate'] = fuzz.trimf(skill_level.universe, [3, 5, 7])
skill_level['expert'] = fuzz.trapmf(skill_level.universe, [6, 8, 10, 10])

# Выходная переменная: коэффициент усиления веса
skill_factor = Consequent(np.arange(0, 11, 1), 'skill_factor')

# Определяем нечёткие множества для коэффициента
skill_factor['low'] = fuzz.trapmf(skill_factor.universe, [0, 0, 2, 4])
skill_factor['medium'] = fuzz.trimf(skill_factor.universe, [3, 5, 7])
skill_factor['high'] = fuzz.trapmf(skill_factor.universe, [6, 8, 10, 10])

# Правила для уровня мастерства
rule4 = Rule(skill_level['novice'], skill_factor['low'])
rule5 = Rule(skill_level['intermediate'], skill_factor['medium'])
rule6 = Rule(skill_level['expert'], skill_factor['high'])

# Создаём систему правил
skill_system = ControlSystem([rule4, rule5, rule6])
skill_sim = ControlSystemSimulation(skill_system)

def evaluate_skills(skills: dict[str, int]) -> dict[str, float]:
    """
    Оценивает уровень мастерства пользователя по инструментам.
    
    :param skills: Словарь с инструментами и их уровнями мастерства.
    :return: Словарь с коэффициентами усиления для инструментов.
    """
    results = {}
    min_count = min(skills.values(), default=0)
    max_count = max(skills.values(), default=1)  # Чтобы избежать деления на 0
    
    for instrument, skill in skills.items():

        if max_count == min_count:
            normalized_frequency = 10  # Если все значения одинаковы, устанавливаем максимум
        else:
            normalized_frequency = ((skill - min_count) / (max_count - min_count)) * 10

        # Устанавливаем уровень мастерства в симуляции
        skill_sim.input['skill_level'] = normalized_frequency
        
        try:
            # Запускаем симуляцию
            skill_sim.compute()
        except Exception as e:
            raise RuntimeError(f"Ошибка в симуляции для инструмента '{instrument}': {e}")
        
        # Получаем коэффициент усиления
        if 'skill_factor' not in skill_sim.output:
            raise KeyError(f"Выходная переменная 'skill_factor' не найдена для инструмента '{instrument}'")
        
        skill_factor_value = skill_sim.output['skill_factor']
        results[instrument] = skill_factor_value
    
    return results