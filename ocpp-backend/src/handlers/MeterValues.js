import { ocppResponse } from "../utils/ocppResponse.js";

export default async function handleMeterValues({ client, payload }) {
  // Zde zatím data jen logujeme.
  // V budoucnu je můžeš posílat na API a ukládat k transakci pro live graf.
  const { transactionId, meterValue } = payload;
  
  // Najdeme poslední hodnotu (často jich chodí víc v poli)
  const lastSample = meterValue[meterValue.length - 1];
  const energyImport = lastSample.sampledValue.find(
    (v) => v.measurand === "Energy.Active.Import.Register"
  );

  client.log.info(
    { 
      txId: transactionId, 
      energy: energyImport ? `${energyImport.value} ${energyImport.unit}` : "N/A" 
    }, 
    "📊 MeterValues received"
  );

  // Vždy musíme vrátit prázdnou odpověď, jinak si nabíječka myslí, že je chyba
  return {};
}