# FAST API BACKEND
## Start serveru:
1. Buildnout kontejnery
`docker-compose up -d`
2. Provést migrace
`docker-compose exec api alembic upgrade head`

## Vytvoření migrace
1. Buildnout kontejnery
2. Vytvoření migrace
`alembic revision --autogenerate -m "Název migrace"`
3. Provést migrace
`docker-compose exec api alembic upgrade head`

## Kde co běží
- **API** - http://localhost:8000/api/v1/
- **Swagger dokumentace** - http://localhost:8000/docs
- **Redoc dokumentace** - http://localhost:8000/redoc
### Jak se připojit do PostgreSQL shellu
1. Buildnout kontejnery
`docker-compose up -d`
2. Připojení do shellu
`docker-compose exec db psql -U <uživatel> -d <databáze>`
#### List všech databází
1. Připojit se do PostgreSQL shellu (postup výše)
2. Přikaz pro list všech databází `\dt`

## Zdroje
- https://www.youtube.com/watch?v=Af6Zr0tNNdE&list=LL