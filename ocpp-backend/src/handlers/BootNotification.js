import apiClient from "../utils/apiClient.js";
import { ocppResponse } from "../utils/ocppResponse.js";

export default async function handleBootNotification({ client, payload }) {
  // Rozbalení dat
  const { 
    chargePointVendor, 
    chargePointModel, 
    chargePointSerialNumber, 
    firmwareVersion 
  } = payload;

  const ocppId = client.identity;

  client.log.info({ payload }, "📦 BootNotification received");

  try {
    // 1. Volání API přes apiClient
    // apiClient už má nastavený BaseURL (např. http://api:8000/api/v1/internal)
    // Takže píšeme jen koncovou část cesty.
    await apiClient.post(`/boot-notification/${ocppId}`, {
      vendor: chargePointVendor,
      model: chargePointModel,
      serial_number: chargePointSerialNumber,
      firmware_version: firmwareVersion
    });

    // 2. Pokud API neodpoví chybou (axios by hodil error), pokračujeme
    client.log.info("✅ Charger authorized and updated");

    // 3. Vracíme Accepted
    return ocppResponse.bootNotification("Accepted", 300);

  } catch (error) {
    // Pokud API vrátí chybu (4xx, 5xx) nebo je nedostupné
    
    // Zjistíme, jestli jde o odmítnutí API (např. 404/403) nebo chybu sítě
    const status = error.response ? error.response.status : "NetworkError";
    const msg = error.response?.data?.detail || error.message;

    client.log.warn({ status, err: msg }, "⚠️ BootNotification rejected or failed");

    // Vracíme Rejected (nebo Pending, pokud je to jen výpadek sítě - volitelné)
    // Tady pro jistotu dáváme Rejected s kratším intervalem, ať to zkusí znovu.
    return ocppResponse.bootNotification("Rejected", 60);
  }
}