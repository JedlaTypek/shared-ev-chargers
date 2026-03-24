import apiClient from "../utils/apiClient.js";
import { ocppResponse } from "../utils/ocppResponse.js";
import { buildChargingProfile, kwToAmps } from "../utils/profileBuilder.js";

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

    // 2. Debug Konfigurace a Nastavení měření
    setTimeout(async () => {
      client.log.info("⏰ Timeout passed. Starting configuration sequence...");

      // --- KROK A: Získání aktuální konfigurace (pro kontrolu) ---
      try {
        const response = await client.call('GetConfiguration', {
          key: [] // Prázdné pole = dej mi všechno
        });

        client.log.info({
          configurationKeys: response.configurationKey,
          unknownKeys: response.unknownKey
        }, "📋 FULL CHARGER CONFIGURATION");

      } catch (err) {
        client.log.error({ err: err.message }, "❌ Failed to GetConfiguration");
      }

      // --- KROK B: Povolení Remote Start (pro APP mode) ---
      try {
        client.log.info("⚙️ Attempting to enable Remote Start (AuthorizeRemoteTxRequests)...");

        const response = await client.call('ChangeConfiguration', {
          key: 'AuthorizeRemoteTxRequests',
          value: 'true'
        });

        if (response.status === 'Accepted') {
          client.log.info("✅ Configuration SUCCESS: AuthorizeRemoteTxRequests is now TRUE");
        }
        else if (response.status === 'RebootRequired') {
          client.log.warn("⚠️ Configuration ACCEPTED, but CHARGER REBOOT REQUIRED");
        }
        else {
          client.log.warn({ status: response.status }, "❌ Failed to set AuthorizeRemoteTxRequests");
        }

      } catch (err) {
        client.log.error({ err: err.message }, "💥 Network error (AuthorizeRemoteTxRequests)");
      }

      // --- KROK C: Nastavení detailního měření (L1, L2, L3) ---
      // TOTO JE TA NOVÁ ČÁST PRO DIAGNOSTIKU FÁZÍ
      try {
        client.log.info("🛠️ Attempting to configure detailed MeterValues (L1, L2, L3)...");

        const response = await client.call('ChangeConfiguration', {
          key: 'MeterValuesSampledData',
          // Žádáme: Celkový proud, Proudy po fázích, Celkové napětí, Napětí po fázích, Výkon, Energie
          value: 'Current.Import,Current.Import.L1,Current.Import.L2,Current.Import.L3,Voltage,Voltage.L1,Voltage.L2,Voltage.L3,Power.Active.Import,Energy.Active.Import.Register'
        });

        if (response.status === 'Accepted') {
          client.log.info("✅ MeterValues Configuration SUCCESS: Detailed phases enabled!");
        }
        else if (response.status === 'RebootRequired') {
          client.log.warn("⚠️ MeterValues Configuration ACCEPTED, but REBOOT REQUIRED");
        }
        else if (response.status === 'Rejected') {
          // Varování: V předchozím logu byl tento klíč označen jako 'readonly: true'.
          // Je možné, že to Solax nedovolí změnit.
          client.log.error("❌ MeterValues Configuration REJECTED (Key might be ReadOnly)");
        }
        else {
          client.log.warn({ status: response.status }, "❌ MeterValues Configuration FAILED");
        }

      } catch (err) {
        client.log.error({ err: err.message }, "💥 Network error (MeterValuesSampledData)");
      }

      // --- KROK D: Nastavení max. profilu (Ampery) ---
      try {
        const limitAmps = kwToAmps(11); // Naimplementováno "natvrdo" dle zadání 11kW->16A
        client.log.info({ limitAmps }, "🔌 Attempting to set ChargePointMaxProfile (Amperes)...");

        const profilePayload = buildChargingProfile(0, limitAmps, "ChargePointMaxProfile");

        const response = await client.call('SetChargingProfile', profilePayload);

        if (response.status === 'Accepted') {
          client.log.info("✅ MaxProfile Configuration SUCCESS: Limit set to " + limitAmps + "A");
        } else {
          client.log.warn({ status: response.status }, "⚠️ MaxProfile Configuration REJECTED");
        }
      } catch (err) {
        client.log.error({ err: err.message }, "💥 Network error (SetChargingProfile)");
      }

    }, 2000);

    return ocppResponse.bootNotification("Accepted", 300);

  } catch (error) {
    const msg = error.response?.data?.detail || error.message;
    client.log.warn({ err: msg }, "⚠️ BootNotification failed");
    return ocppResponse.bootNotification("Rejected", 60);
  }
}