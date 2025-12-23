import { ocppResponse } from "../utils/ocppResponse.js";
import { config } from "../utils/config.js";
import axios from "axios";

export default async function handleBootNotification({ client, payload }) {
  const { 
    chargePointVendor, 
    chargePointModel, 
    chargePointSerialNumber, 
    firmwareVersion 
  } = payload;

  const ocppId = client.identity;
  client.log.info({ payload }, "📦 BootNotification received");

  try {
    // Axios automaticky:
    // 1. Nastaví Content-Type: application/json
    // 2. Převede objekt na JSON string
    // 3. Vyhodí error, pokud API vrátí 4xx nebo 5xx
    const response = await axios.post(
      `${config.apiUrl}/chargers/boot-notification/${ocppId}`,
      {
        vendor: chargePointVendor,
        model: chargePointModel,
        serial_number: chargePointSerialNumber,
        firmware_version: firmwareVersion
      }
    );

    // Pokud jsme zde, odpověď je OK (200-299)
    const chargerData = response.data;
    
    client.log.info(
      { id: chargerData.id, model: chargerData.model }, 
      "✅ Charger authorized and updated"
    );

    return ocppResponse.bootNotification("Accepted", 300);

  } catch (error) {
    if (error.response) {
      // API odpovědělo chybou (např. 403 Forbidden)
      client.log.warn(
        { status: error.response.status, data: error.response.data }, 
        "⚠️ Charger rejected by API"
      );
      return ocppResponse.bootNotification("Rejected", 60);
    } else {
      // Chyba sítě (API nedostupné)
      client.log.error({ err: error.message }, "💥 Failed to contact API backend");
      return ocppResponse.bootNotification("Pending", 30);
    }
  }
}