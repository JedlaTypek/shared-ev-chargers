from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import config
from app.api.v1 import user, charger, connector, rfid, transaction # Importujeme routery

app = FastAPI(
    title=config.project_name,
    version=config.project_version,
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
)

# Nastavení CORS (aby se na API dalo volat z frontendu/prohlížeče)
if config.backend_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in config.backend_cors_origins],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.get("/", include_in_schema=False)
def root():
    return {"message": "Welcome to Shared EV Chargers API"}

# ---------------------------------------------------------
# Registrace Routerů
# ---------------------------------------------------------

# 1. Users
app.include_router(user.router, prefix="/api/v1/users", tags=["Users"])

# 2. Chargers
app.include_router(charger.router, prefix="/api/v1/chargers", tags=["Chargers"])

# 3. Connectors 
# Necháváme samostatně pro přímý přístup (např. GET /connectors/{id} nebo webhooky)
app.include_router(connector.router, prefix="/api/v1/connectors", tags=["Connectors"])

# 4. RFID Cards
app.include_router(rfid.router, prefix="/api/v1/rfid-cards", tags=["RFID Cards"])

# 5. Transactions (OCPP Start/Stop)
app.include_router(transaction.router, prefix="/api/v1/transactions", tags=["Transactions"])