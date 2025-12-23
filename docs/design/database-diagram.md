# Database diagram documentation
## Summary

- [Introduction](#introduction)
- [Database Type](#database-type)
- [Table Structure](#table-structure)
	- [users](#users)
	- [chargers](#chargers)
	- [connector_types](#connector_types)
	- [connectors](#connectors)
	- [rfid_cards](#rfid_cards)
	- [charge_logs](#charge_logs)
	- [reservations](#reservations)
- [Relationships](#relationships)
- [Database Diagram](#database-diagram)

## Introduction

## Database type

- **Database system:** PostgreSQL
## Table structure

### users

| Name        | Type          | Settings                      | References                    | Note                           |
|-------------|---------------|-------------------------------|-------------------------------|--------------------------------|
| **id** | SERIAL | 🔑 PK, null |  | |
| **email** | VARCHAR(255) | not null, unique |  | |
| **password_hash** | TEXT | not null |  | |
| **full_name** | VARCHAR(255) | null |  | |
| **role** | VARCHAR(20) | null, default: user |  | |
| **balance** | NUMERIC(10,2) | null, default: 0 |  | |
| **created_at** | TIMESTAMP | null, default: NOW() |  | | 


### chargers

| Name        | Type          | Settings                      | References                    | Note                           |
|-------------|---------------|-------------------------------|-------------------------------|--------------------------------|
| **id** | SERIAL | 🔑 PK, null |  | |
| **owner_id** | INTEGER | not null | fk_chargers_owner_id_users | |
| **name** | VARCHAR(255) | not null |  | |
| **latitude** | NUMERIC(9,6) | not null |  | |
| **longitude** | NUMERIC(9,6) | not null |  | |
| **street** | VARCHAR(255) | null |  | |
| **house_number** | VARCHAR(20) | null |  | |
| **city** | VARCHAR(100) | null |  | |
| **postal_code** | VARCHAR(20) | null |  | |
| **region** | VARCHAR(100) | null |  | |
| **ocpp_id** | VARCHAR(255) | null, unique |  | |
| **is_active** | BOOLEAN | null, default: true |  | |
| **created_at** | TIMESTAMP | null, default: NOW() |  | | 


### connector_types

| Name        | Type          | Settings                      | References                    | Note                           |
|-------------|---------------|-------------------------------|-------------------------------|--------------------------------|
| **id** | SERIAL | 🔑 PK, null |  | |
| **name** | VARCHAR(50) | not null, unique |  | |
| **current_type** | VARCHAR(10) | not null |  | | 


### connectors

| Name        | Type          | Settings                      | References                    | Note                           |
|-------------|---------------|-------------------------------|-------------------------------|--------------------------------|
| **id** | SERIAL | 🔑 PK, null |  | |
| **charger_id** | INTEGER | not null | fk_connectors_charger_id_chargers | |
| **connector_type_id** | INTEGER | not null | fk_connectors_connector_type_id_connector_types | |
| **connector_number** | INTEGER | not null |  | |
| **max_power_kw** | NUMERIC(5,2) | not null |  | |
| **price_per_kwh** | NUMERIC(5,2) | not null |  | |
| **is_active** | BOOLEAN | null, default: true |  | | 


### rfid_cards

| Name        | Type          | Settings                      | References                    | Note                           |
|-------------|---------------|-------------------------------|-------------------------------|--------------------------------|
| **id** | SERIAL | 🔑 PK, null |  | |
| **user_id** | INTEGER | not null | fk_rfid_cards_user_id_users | |
| **card_uid** | VARCHAR(255) | not null, unique |  | |
| **is_active** | BOOLEAN | null, default: true |  | |
| **created_at** | TIMESTAMP | null, default: NOW() |  | | 


### charge_logs

| Name        | Type          | Settings                      | References                    | Note                           |
|-------------|---------------|-------------------------------|-------------------------------|--------------------------------|
| **id** | SERIAL | 🔑 PK, null |  | |
| **user_id** | INTEGER | null | fk_charge_logs_user_id_users | |
| **charger_id** | INTEGER | null | fk_charge_logs_charger_id_chargers | |
| **connector_id** | INTEGER | null | fk_charge_logs_connector_id_connectors | |
| **rfid_card_id** | INTEGER | null | fk_charge_logs_rfid_card_id_rfid_cards | |
| **start_time** | TIMESTAMP | not null |  | |
| **end_time** | TIMESTAMP | null |  | |
| **energy_kwh** | NUMERIC(8,3) | null |  | |
| **price** | NUMERIC(7,2) | null |  | |
| **status** | VARCHAR(20) | null, default: running |  | | 


### reservations

| Name        | Type          | Settings                      | References                    | Note                           |
|-------------|---------------|-------------------------------|-------------------------------|--------------------------------|
| **id** | SERIAL | 🔑 PK, null |  | |
| **user_id** | INTEGER | not null | fk_reservations_user_id_users | |
| **charger_id** | INTEGER | not null | fk_reservations_charger_id_chargers | |
| **connector_id** | INTEGER | null | fk_reservations_connector_id_connectors | |
| **start_time** | TIMESTAMP | not null |  | |
| **end_time** | TIMESTAMP | not null |  | |
| **status** | VARCHAR(20) | null, default: active |  | | 


## Relationships

- **chargers to users**: many_to_one
- **connectors to chargers**: many_to_one
- **connectors to connector_types**: many_to_one
- **rfid_cards to users**: many_to_one
- **charge_logs to users**: many_to_one
- **charge_logs to chargers**: many_to_one
- **charge_logs to connectors**: many_to_one
- **charge_logs to rfid_cards**: many_to_one
- **reservations to users**: many_to_one
- **reservations to chargers**: many_to_one
- **reservations to connectors**: many_to_one

## Database Diagram

```mermaid
erDiagram
	chargers }o--|| users : references
	connectors }o--|| chargers : references
	connectors }o--|| connector_types : references
	rfid_cards }o--|| users : references
	charge_logs }o--|| users : references
	charge_logs }o--|| chargers : references
	charge_logs }o--|| connectors : references
	charge_logs }o--|| rfid_cards : references
	reservations }o--|| users : references
	reservations }o--|| chargers : references
	reservations }o--|| connectors : references

	users {
		SERIAL id
		VARCHAR(255) email
		TEXT password_hash
		VARCHAR(255) full_name
		VARCHAR(20) role
		NUMERIC(10,2) balance
		TIMESTAMP created_at
	}

	chargers {
		SERIAL id
		INTEGER owner_id
		VARCHAR(255) name
		NUMERIC(9,6) latitude
		NUMERIC(9,6) longitude
		VARCHAR(255) street
		VARCHAR(20) house_number
		VARCHAR(100) city
		VARCHAR(20) postal_code
		VARCHAR(100) region
		VARCHAR(255) ocpp_id
		BOOLEAN is_active
		TIMESTAMP created_at
	}

	connector_types {
		SERIAL id
		VARCHAR(50) name
		VARCHAR(10) current_type
	}

	connectors {
		SERIAL id
		INTEGER charger_id
		INTEGER connector_type_id
		INTEGER connector_number
		NUMERIC(5,2) max_power_kw
		NUMERIC(5,2) price_per_kwh
		BOOLEAN is_active
	}

	rfid_cards {
		SERIAL id
		INTEGER user_id
		VARCHAR(255) card_uid
		BOOLEAN is_active
		TIMESTAMP created_at
	}

	charge_logs {
		SERIAL id
		INTEGER user_id
		INTEGER charger_id
		INTEGER connector_id
		INTEGER rfid_card_id
		TIMESTAMP start_time
		TIMESTAMP end_time
		NUMERIC(8,3) energy_kwh
		NUMERIC(7,2) price
		VARCHAR(20) status
	}

	reservations {
		SERIAL id
		INTEGER user_id
		INTEGER charger_id
		INTEGER connector_id
		TIMESTAMP start_time
		TIMESTAMP end_time
		VARCHAR(20) status
	}
```