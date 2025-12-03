from fastapi import FastAPI

# Musíte importovat všechny moduly s routami
from app.api.v1 import user, charger, connector, rfid
from app.core.config import config
from app.core.logging import setup_logging
# from app.db.schema import Base, engine # Pokud nepoužíváte alembic, odkomentujte pro auto-create tabulek

setup_logging()

app = FastAPI(title=config.app_name)

# --- REGISTRACE ROUT ---

# 1. Users
# V user.py máte definované cesty jako "/users", takže prefix stačí "/api/v1"
# Výsledek: /api/v1/users
app.include_router(user.router, prefix="/api/v1")

# 2. Chargers
# V charger.py jsem definoval cesty jako "" (prázdné), takže prefix musí obsahovat název zdroje
# Výsledek: /api/v1/chargers
app.include_router(charger.router, prefix="/api/v1/chargers", tags=["Chargers"])

# 3. Connectors
# Výsledek: /api/v1/connectors
app.include_router(connector.router, prefix="/api/v1/connectors", tags=["Connectors"])

# 4. RFID Cards
# Výsledek: /api/v1/rfid-cards
app.include_router(rfid.router, prefix="/api/v1/rfid-cards", tags=["RFID Cards"])