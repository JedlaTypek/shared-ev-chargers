from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import Base, engine
from app import models  # noqa: F401 - needed to register SQLAlchemy models
from app.routers import charger, user  # sem budeš přidávat další routery

# Inicializace DB (vytvoří tabulky, pokud nejsou)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    debug=settings.DEBUG,
)

# Povolené CORS (dočasně otevřené pro vývoj)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Připojení routerů
app.include_router(user.router, prefix="/users", tags=["Users"])
app.include_router(charger.router, prefix="/chargers", tags=["Chargers"])

@app.get("/")
def root():
    return {"message": f"{settings.PROJECT_NAME} is running"}
