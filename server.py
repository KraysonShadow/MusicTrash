from fastapi import FastAPI
from app.api.route import router
from app.utils.ontology import ontology

app = FastAPI()

app.include_router(router, prefix="/api")

for cls in ontology.classes():
    print(cls)