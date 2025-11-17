# FAST API BACKEND
## Starting the server:
1. Buildnout kontejnery
`docker-compose up -d`
2. Provést migrace
`docker-compose exec api alembic upgrade head`

## Kde co běží
- **API** - http://localhost:8000/api/v1/
- **Swagger dokumentace** - http://localhost:8000/docs
- **Redoc dokumentace** - http://localhost:8000/redoc

## Zdroje
- https://www.youtube.com/watch?v=Af6Zr0tNNdE&list=LL