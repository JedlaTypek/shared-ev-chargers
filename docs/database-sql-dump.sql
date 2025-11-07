CREATE TABLE IF NOT EXISTS "users" (
	"id" SERIAL,
	"email" VARCHAR(255) NOT NULL UNIQUE,
	"password_hash" TEXT NOT NULL,
	"full_name" VARCHAR(255),
	"role" VARCHAR(20) DEFAULT 'user' CHECK("[object Object]" IN user AND owner AND admin),
	"balance" NUMERIC(10,2) DEFAULT 0,
	"created_at" TIMESTAMP DEFAULT NOW(),
	PRIMARY KEY("id")
);




CREATE TABLE IF NOT EXISTS "chargers" (
	"id" SERIAL,
	"owner_id" INTEGER NOT NULL,
	"name" VARCHAR(255) NOT NULL,
	"latitude" NUMERIC(9,6) NOT NULL,
	"longitude" NUMERIC(9,6) NOT NULL,
	"street" VARCHAR(255),
	"house_number" VARCHAR(20),
	"city" VARCHAR(100),
	"postal_code" VARCHAR(20),
	"region" VARCHAR(100),
	"ocpp_id" VARCHAR(255) UNIQUE,
	"is_active" BOOLEAN DEFAULT true,
	"created_at" TIMESTAMP DEFAULT NOW(),
	PRIMARY KEY("id")
);




CREATE TABLE IF NOT EXISTS "connector_types" (
	"id" SERIAL,
	"name" VARCHAR(50) NOT NULL UNIQUE,
	"current_type" VARCHAR(10) NOT NULL CHECK("[object Object]" IN AC AND DC),
	PRIMARY KEY("id")
);




CREATE TABLE IF NOT EXISTS "connectors" (
	"id" SERIAL,
	"charger_id" INTEGER NOT NULL,
	"connector_type_id" INTEGER NOT NULL,
	"connector_number" INTEGER NOT NULL,
	"max_power_kw" NUMERIC(5,2) NOT NULL,
	"price_per_kwh" NUMERIC(5,2) NOT NULL,
	"is_active" BOOLEAN DEFAULT true,
	PRIMARY KEY("id")
);




CREATE TABLE IF NOT EXISTS "rfid_cards" (
	"id" SERIAL,
	"user_id" INTEGER NOT NULL,
	"card_uid" VARCHAR(255) NOT NULL UNIQUE,
	"is_active" BOOLEAN DEFAULT true,
	"created_at" TIMESTAMP DEFAULT NOW(),
	PRIMARY KEY("id")
);




CREATE TABLE IF NOT EXISTS "charge_logs" (
	"id" SERIAL,
	"user_id" INTEGER,
	"charger_id" INTEGER,
	"connector_id" INTEGER,
	"rfid_card_id" INTEGER,
	"start_time" TIMESTAMP NOT NULL,
	"end_time" TIMESTAMP,
	"energy_kwh" NUMERIC(8,3),
	"price" NUMERIC(7,2),
	"status" VARCHAR(20) DEFAULT 'running' CHECK("[object Object]" IN running AND completed AND failed AND cancelled),
	PRIMARY KEY("id")
);




CREATE TABLE IF NOT EXISTS "reservations" (
	"id" SERIAL,
	"user_id" INTEGER NOT NULL,
	"charger_id" INTEGER NOT NULL,
	"connector_id" INTEGER,
	"start_time" TIMESTAMP NOT NULL,
	"end_time" TIMESTAMP NOT NULL,
	"status" VARCHAR(20) DEFAULT 'active' CHECK("[object Object]" IN active AND cancelled AND completed),
	PRIMARY KEY("id")
);



ALTER TABLE "chargers"
ADD FOREIGN KEY("owner_id") REFERENCES "users"("id")
ON UPDATE NO ACTION ON DELETE CASCADE;
ALTER TABLE "connectors"
ADD FOREIGN KEY("charger_id") REFERENCES "chargers"("id")
ON UPDATE NO ACTION ON DELETE CASCADE;
ALTER TABLE "connectors"
ADD FOREIGN KEY("connector_type_id") REFERENCES "connector_types"("id")
ON UPDATE NO ACTION ON DELETE RESTRICT;
ALTER TABLE "rfid_cards"
ADD FOREIGN KEY("user_id") REFERENCES "users"("id")
ON UPDATE NO ACTION ON DELETE CASCADE;
ALTER TABLE "charge_logs"
ADD FOREIGN KEY("user_id") REFERENCES "users"("id")
ON UPDATE NO ACTION ON DELETE SET NULL;
ALTER TABLE "charge_logs"
ADD FOREIGN KEY("charger_id") REFERENCES "chargers"("id")
ON UPDATE NO ACTION ON DELETE SET NULL;
ALTER TABLE "charge_logs"
ADD FOREIGN KEY("connector_id") REFERENCES "connectors"("id")
ON UPDATE NO ACTION ON DELETE SET NULL;
ALTER TABLE "charge_logs"
ADD FOREIGN KEY("rfid_card_id") REFERENCES "rfid_cards"("id")
ON UPDATE NO ACTION ON DELETE SET NULL;
ALTER TABLE "reservations"
ADD FOREIGN KEY("user_id") REFERENCES "users"("id")
ON UPDATE NO ACTION ON DELETE CASCADE;
ALTER TABLE "reservations"
ADD FOREIGN KEY("charger_id") REFERENCES "chargers"("id")
ON UPDATE NO ACTION ON DELETE CASCADE;
ALTER TABLE "reservations"
ADD FOREIGN KEY("connector_id") REFERENCES "connectors"("id")
ON UPDATE NO ACTION ON DELETE SET NULL;