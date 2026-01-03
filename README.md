# ⚡ Voltuj - OCPP Backend System

Tento projekt představuje robustní backendové řešení pro správu a sdílení soukromých nabíjecích stanic elektromobilů. Systém je postaven na mezinárodním standardu **OCPP 1.6J** a umožňuje majitelům wallboxů integrovat svou infrastrukturu do modelu sdílené ekonomiky.

## 🏗️ Architektura systému
Projekt využívá moderní architekturu mikroslužeb založenou na principu **API-first**. Celý ekosystém je plně kontejnerizován a sestává z následujících komponent:

- **OCPP Backend (Node.js)**: Stavová služba zajišťující perzistentní WebSocket spojení s nabíjecími stanicemi. Provádí validaci zpráv pomocí JSON schémat a řídí logiku nabíjecích procesů.
- **API Backend (FastAPI)**: Aplikační jádro implementované v Pythonu. Zajišťuje business logiku, správu uživatelských účtů, autorizaci (JWT), databázové migrace a evidenci transakcí.
- **PostgreSQL**: Relační databáze pro bezpečné ukládání uživatelských dat, konfigurací nabíječek a detailních provozních logů.
- **Redis**: In-memory datové úložiště pro real-time sledování stavu konektorů (Available, Preparing, Charging atd.).

## 🚀 Rychlý start (Vývojové prostředí)
Díky plné kontejnerizaci není pro lokální spuštění vyžadována instalace Pythonu ani Node.js. Postačí nainstalované prostředí Docker a nástroj Docker Compose.

### 1. Příprava prostředí
Zkopírujte šablonu `.env-example` do nového souboru `.env` a doplňte požadované konfigurační parametry (zejména přístupové údaje k databázi a bezpečnostní klíče).

### 2. Spuštění vývojového režimu
Tento režim využívá funkci **Hot-Reloading**, kdy se veškeré změny v kódu okamžitě promítají do běžících kontejnerů bez nutnosti restartu.

```bash
docker-compose -f docker-compose.dev.yaml up --build

```

### 3. Správa databázových migrací (Alembic)

V rámci vývojového cyklu je nutné provádět migrace manuálně pro zajištění plné kontroly nad změnami schématu. Příkazy se spouštějí v kontextu běžícího kontejneru `api`:

* **Aktualizace databáze na nejnovější verzi:**
```bash
docker compose exec api alembic upgrade head

```


* **Generování nové migrace (při změně modelů v `schema.py`):**
```bash
docker compose exec api alembic revision --autogenerate -m "popis změn"

```

## 🔒 Produkční nasazení

Produkční sestavení využívá optimalizované multi-stage buildy, mechanismy automatického restartu a automatické aktualizace databáze podle poslední migrace.

```bash
docker-compose up -d

```

### Produkční schéma WSS komunikace:
1. **Nabíjecí stanice** inicializuje šifrované spojení **WSS** na portu `9000` domény `jedlickaf.cz`.
2. **Apache** (Reverse Proxy) provádí dešifrování provozu pomocí SSL certifikátu Let's Encrypt.
3. Provoz je interně směrován jako **WS** na port `9001` do příslušného Docker kontejneru.

## 🛠️ Použité technologie

* **Python (FastAPI)** – Jádro systému a REST API
* **Node.js** – Implementace OCPP WebSocket serveru
* **PostgreSQL** – Perzistentní úložiště dat
* **Redis** – Real-time stavový management
* **Docker** – Kontejnerizace a orchestrace služeb
* **Apache** – Reverse Proxy a správa SSL certifikace