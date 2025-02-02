from fastapi import APIRouter
from app.api.route.get_instrument import get
from app.api.schemas.instrument_schemas import InstrumentsResponse

router = APIRouter(tags=["instrument"])

router.get("/", status_code=200, response_model=InstrumentsResponse)(get)