import { ocppResponse } from "../utils/ocppResponse.js";
import { config } from "../utils/config.js"; 
import axios from "axios";

export default async function handleMeterValues({ client, payload }) {
  const { transactionId, meterValue } = payload;
  
  // 1. Získání poslední (nejnovější) hodnoty z pole
  const lastSample = meterValue[meterValue.length - 1];
  
  // 2. Hledáme "Energy.Active.Import.Register" (celkový stav v Wh)
  // Někdy nabíječky posílají jen hodnotu bez 'measurand', default je Import.Register
  const energyImport = lastSample.sampledValue.find(
    (v) => v.measurand === "Energy.Active.Import.Register" || !v.measurand
  );

  client.log.info(
    { 
      txId: transactionId, 
      energy: energyImport ? `${energyImport.value} ${energyImport.unit || 'Wh'}` : "N/A" 
    }, 
    "📊 MeterValues received"
  );

  // 3. Pokud máme hodnotu a transakci, pošleme update do API
  if (energyImport && transactionId) {
    try {
      // Převedeme na celé číslo (int)
      const valueInt = parseInt(energyImport.value, 10);
      
      await axios.post(`${config.apiUrl}/transactions/meter-values`, {
        transaction_id: transactionId,
        meter_value: valueInt
      });

      // client.log.debug("💾 Meter value saved"); // Debug log, ať nespamujeme

    } catch (error) {
      // Chyba updatu nesmí shodit spojení s nabíječkou
      const msg = error.response ? error.response.status : error.message;
      client.log.warn({ err: msg }, "⚠️ Failed to save meter value to DB");
    }
  }

  // Odpověď pro nabíječku je vždy prázdná
  return {};
}