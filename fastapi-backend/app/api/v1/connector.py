from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db
from app.models.connector import ConnectorCreate, ConnectorRead
from app.services.connector_service import ConnectorService

router = APIRouter()

def get_connector_service(db: Session = Depends(get_db)) -> ConnectorService:
    return ConnectorService(session=db)

# Zde to dělám jako samostatný resource /connectors, 
# ale charger_id je uvnitř těla requestu.

@router.post("", response_model=ConnectorRead, status_code=status.HTTP_201_CREATED)
def create_connector(
    connector_data: ConnectorCreate,
    service: ConnectorService = Depends(get_connector_service)
):
    try:
        return service.create_connector(connector_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{connector_id}", response_model=ConnectorRead)
def get_connector(
    connector_id: int,
    service: ConnectorService = Depends(get_connector_service)
):
    connector = service.get_connector(connector_id)
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")
    return connector

@router.delete("/{connector_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_connector(
    connector_id: int,
    service: ConnectorService = Depends(get_connector_service)
):
    success = service.delete_connector(connector_id)
    if not success:
        raise HTTPException(status_code=404, detail="Connector not found")
    return