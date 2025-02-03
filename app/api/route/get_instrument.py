from fastapi import APIRouter, HTTPException
from app.api.schemas.instrument_schemas import InstrumentsResponse, ArtistSkillsRequest
from app.utils.ontology import get_genres_from_artists
from app.utils.fuzzy import evaluate_genres, evaluate_skills

router = APIRouter()

def get(request: ArtistSkillsRequest):
    """
    Получает список наиболее подходящих музыкальных инструментов с весами на основе списка артистов и навыков.
    
    :param request: Данные, включающие список артистов и (опционально) навыки пользователя.
    :return: Список наиболее подходящих инструментов с весами.
    """
    if not request.artists:
        raise HTTPException(status_code=400, detail="Список артистов не может быть пустым")
    
    # Получаем список артистов
    artist_list = [artist.strip() for artist in request.artists]
    instrument_weights = get_genres_from_artists(artist_list)
    # Обработка навыков пользователя
    if request.skills:
        skill_dict = {skill.instrument: skill.level for skill in request.skills}
        skills_evaluation = evaluate_skills(skill_dict)
    else:
        skills_evaluation = {}

    # Интеграция с оценкой навыков
    for instrument in instrument_weights:
        if instrument in skills_evaluation:
            instrument_weights[instrument] *= skills_evaluation[instrument]

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

    # Сортируем инструменты по нормализованным весам в порядке убывания
    sorted_instruments = sorted(
        ((name, weight) for name, weight in normalized_instruments.items() if weight > 0),
        key=lambda x: x[1], 
        reverse=True
    )
    
    return InstrumentsResponse(instruments=[{"name": name, "weight": round(weight, 2)} for name, weight in sorted_instruments[:3]])
