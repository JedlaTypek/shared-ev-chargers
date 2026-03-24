import apiClient from "../utils/apiClient.js";

export default async function handleMeterValues({ client, payload }) {
  const { transactionId, connectorId, meterValue } = payload;

  // Log pro debug
  client.log.debug({ transactionId }, "📊 MeterValues received");

  // Keep-alive: Update heartbeat in Redis because charging stations often don't send Heartbeats during transaction
  try {
    await apiClient.post(`/heartbeat/${client.identity}`);
  } catch (err) {
    client.log.warn({ err: err.message }, "⚠️ Failed to update heartbeat status from MeterValues");
  }

  // 1. Získání poslední (nejnovější) hodnoty z pole měření
  // OCPP může poslat více vzorků najednou, nás zajímá ten aktuální (poslední)
  const lastSample = meterValue[meterValue.length - 1];

  if (!lastSample) {
    return {}; // Prázdný payload, ignorujeme
  }

  // 2. Hledáme "Energy.Active.Import.Register" (stav elektroměru v Wh)
  // Pokud nabíječka neposílá 'measurand', specifikace říká, že default je Import Register.
  const energyImport = lastSample.sampledValue.find(
    (v) => v.measurand === "Energy.Active.Import.Register" || !v.measurand
  );

  // 3. Pokud jsme našli hodnotu energie a máme ID transakce, pošleme to na backend
  if (energyImport && transactionId) {
    try {
      // Převedeme string na číslo (int)
      const valueInt = parseInt(energyImport.value, 10);

      // Voláme API: POST /transactions/meter-values
      await apiClient.post("/transaction/meter-values", {
        transaction_id: transactionId,
        meter_value: valueInt
      });

      client.log.debug({ val: valueInt }, "💾 Meter value saved to DB");

    } catch (error) {
      // Chyba při ukládání (např. transakce už neexistuje)
      // Nesmíme shodit spojení, jen zalogujeme varování.
      client.log.warn({ err: error.message }, "⚠️ Failed to save meter value");
    }
  }

  // Odpověď pro nabíječku je vždy prázdná (podle OCPP specifikace)
  return {};
}