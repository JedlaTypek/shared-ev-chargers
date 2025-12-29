import apiClient from "../utils/apiClient.js";
import { ocppResponse } from "../utils/ocppResponse.js";

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
    // 1. Volání API
    await apiClient.post(`/boot-notification/${ocppId}`, {
      vendor: chargePointVendor,
      model: chargePointModel,
      serial_number: chargePointSerialNumber,
      firmware_version: firmwareVersion
    });

    client.log.info("✅ Charger authorized and updated");

    // 2. Debug Konfigurace
    setTimeout(async () => {
      // TADY BYLA CHYBA: Vyhodil jsem tu kontrolu 'if (!client.connection...)'
      // Necháme to spadnout do catch bloku, pokud by spojení neexistovalo,
      // ale aspoň uvidíme log.
      
      client.log.info("⏰ Timeout passed. Attempting GetConfiguration...");

      try {
        // Zkusíme získat úplně všechno (prázdné pole klíčů)
        const response = await client.call('GetConfiguration', { 
            key: [] 
        });

        // Výpis do logu - zajímají nás hlavně unknownKeys a konkrétní hodnoty
        client.log.info({ 
            configurationKeys: response.configurationKey,
            unknownKeys: response.unknownKey 
        }, "📋 FULL CHARGER CONFIGURATION");

      } catch (err) {
        client.log.error({ err: err.message }, "❌ Failed to GetConfiguration");
      }

      try {
        client.log.info("⚙️ Attempting to enable Remote Start (AuthorizeRemoteTxRequests)...");

        // 1. Odeslání příkazu a čekání na odpověď
        const response = await client.call('ChangeConfiguration', {
            key: 'AuthorizeRemoteTxRequests',
            value: 'true'
        });

        // 2. Kontrola statusu odpovědi
        if (response.status === 'Accepted') {
            client.log.info("✅ Configuration SUCCESS: AuthorizeRemoteTxRequests is now TRUE");
        } 
        else if (response.status === 'RebootRequired') {
            client.log.warn("⚠️ Configuration ACCEPTED, but CHARGER REBOOT REQUIRED");
        }
        else if (response.status === 'Rejected') {
            // Toto se stane, pokud je klíč v nabíječce nastaven jako "readonly: true"
            client.log.error("❌ Configuration REJECTED: Key is likely ReadOnly");
        }
        else if (response.status === 'NotSupported') {
            client.log.error("❌ Configuration FAILED: Key is not supported by this charger");
        }
        else {
            // Jiný neznámý status
            client.log.warn({ status: response.status }, "❓ Unknown configuration status");
        }

      } catch (err) {
          // Chyba sítě nebo timeout
          client.log.error({ err: err.message }, "💥 Network error while changing configuration");
      }
      
    }, 2000);

    return ocppResponse.bootNotification("Accepted", 300);

  } catch (error) {
    const msg = error.response?.data?.detail || error.message;
    client.log.warn({ err: msg }, "⚠️ BootNotification failed");
    return ocppResponse.bootNotification("Rejected", 60);
  }
}