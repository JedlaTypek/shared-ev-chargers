import { ocppResponse } from "../utils/ocppResponse.js";
import { config } from "../utils/config.js"; // Načítáme konfiguraci z utils

export default async function handleBootNotification({ client, payload }) {
  // Rozbalení dat z payloadu zprávy BootNotification
  const { 
    chargePointVendor, 
    chargePointModel, 
    chargePointSerialNumber, 
    firmwareVersion 
  } = payload;

  // Identita nabíječky (např. "CHG-001") z WebSocket spojení
  const ocppId = client.identity;

  // Logování příchozího požadavku
  client.log.info({ payload }, "📦 BootNotification received");

  try {
    // Sestavení URL pro volání FastAPI backendu
    const url = `${config.apiUrl}/chargers/boot-notification/${ocppId}`;

    // 1. Volání API pro autorizaci a uložení metadat
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        vendor: chargePointVendor,
        model: chargePointModel,
        serial_number: chargePointSerialNumber,
        firmware_version: firmwareVersion
      }),
    });

    // 2. Kontrola odpovědi z API
    if (!response.ok) {
      // Pokud API vrátí chybu (např. 404 - nabíječka neexistuje, nebo 500)
      client.log.warn(
        { status: response.status, statusText: response.statusText }, 
        "⚠️ Charger unauthorized or API error"
      );
      
      // Odmítneme nabíječku. Interval 60s říká "zkus to znovu za minutu".
      return ocppResponse.bootNotification("Rejected", 60);
    }

    // 3. Zpracování úspěšné odpovědi
    const chargerData = await response.json();
    
    client.log.info(
      { id: chargerData.id, model: chargerData.model }, 
      "✅ Charger authorized and updated"
    );

    // Přijmeme nabíječku. 
    // Interval 300s = očekáváme Heartbeat každých 5 minut.
    return ocppResponse.bootNotification("Accepted", 300);

  } catch (error) {
    // Pokud selže síťové spojení s API kontejnerem (např. API neběží)
    client.log.error({ err: error }, "💥 Failed to contact API backend");
    
    // Vrátíme Pending, aby to nabíječka zkusila za chvíli znovu (30s)
    return ocppResponse.bootNotification("Pending", 30);
  }
}