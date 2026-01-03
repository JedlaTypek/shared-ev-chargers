# FAST API BACKEND
## Zdroje
- https://www.youtube.com/watch?v=Af6Zr0tNNdE&list=LL

## 🛠 Technické specifikace
- **Runtime**: Python 3.12+
- **Framework**: FastAPI
- **ORM**: SQLAlchemy (Async)
- **Migrace**: Alembic
- **Validace**: Pydantic v2

## 📁 Struktura projektu
- `app/api/`: Endpointy rozdělené podle verzí a modulů.
- `app/core/`: Globální konfigurace a nastavení bezpečnosti.
- `app/db/`: Definice databázových modelů (schema.py) a inicializace session.
- `app/models/`: Pydantic schémata pro validaci vstupů a výstupů.
- `app/services/`: Business logika oddělená od endpointů.
- `alembic/`: Skripty pro správu verzování databázového schématu.

## 🔧 Vývojářské instrukce

### Práce s databází
Pro interakci s PostgreSQL uvnitř Dockeru použijte následující příkazy:

- **Vstup do PostgreSQL shellu:**
  ```bash
  docker compose exec db psql -U ${POSTGRES_USER} -d ${POSTGRES_DB}
  ```
- **Výpis tabulek v shellu:** `\dt`

## Správa migrací (Alembic)

Při změně modelů v app/db/schema.py je nutné generovat migrační skript:

Generování: `docker compose exec api alembic revision --autogenerate -m "popis změn"`

Aplikace: `docker compose exec api alembic upgrade head`