import apiClient from "../utils/apiClient.js";
import { kwToAmps } from "../utils/profileBuilder.js";

// Pomocná funkce pro čekání
const sleep = (ms) => new Promise(r => setTimeout(r, ms));

export default async function handleStartTransaction({ client, payload }) {
  const ocppId = client.identity;
  const { connectorId, idTag, meterStart, timestamp } = payload;

  client.log.info({ connectorId, idTag }, "🔌 StartTransaction request received");

  try {
    const response = await apiClient.post("/transaction/start", {
      ocpp_id: ocppId,
      connector_id: connectorId,
      id_tag: idTag,
      meter_start: meterStart,
      timestamp: timestamp,
    });

    const { transactionId, max_power } = response.data;

    if (!transactionId) {
      return { transactionId: 0, idTagInfo: { status: "Invalid" } };
    }

    client.log.info({ txId: transactionId, maxKw: max_power }, "✅ Transaction created in DB");

    // Asynchronní konfigurace - POUZE ChargePointMaxProfile
    (async () => {
      // Počkáme 2 sekundy (5s už asi není třeba, když nepoužíváme TxProfile s IDčkem)
      await sleep(2000);

      const limitAmps = kwToAmps(max_power || 11);

      const profilePayload = {
        connectorId: 0, // Celá nabíječka
        csChargingProfiles: {
          chargingProfileId: 999,
          stackLevel: 2, // Vysoká priorita
          chargingProfilePurpose: "ChargePointMaxProfile",
          chargingProfileKind: "Relative",
          chargingSchedule: {
            chargingRateUnit: "A",
            chargingSchedulePeriod: [{ startPeriod: 0, limit: limitAmps, numberPhases: 3 }]
          }
        }
      };

      try {
        // Upravené logování pro zobrazení celé zprávy
        client.log.info({ profilePayload }, `📤 Sending ChargePointMaxProfile (${limitAmps}A)...`);
        const profileResponse = await client.call("SetChargingProfile", profilePayload);

        if (profileResponse.status === 'Accepted') {
          client.log.info("✅ MaxProfile ACCEPTED - Waiting for contactor...");
        } else {
          client.log.warn({ status: profileResponse.status }, "⚠️ MaxProfile REJECTED");
        }
      } catch (err) {
        client.log.error({ err: err.message }, "💥 Error sending MaxProfile");
      }

      // ❌ ZDE JSME SMAZALI RemoteStartTransaction ❌
      // Už ho neposíláme, protože způsoboval smyčku restartů.

    })();

    return {
      transactionId: transactionId,
      idTagInfo: { status: "Accepted" },
    };

  } catch (error) {
    client.log.error({ err: error.message }, "💥 StartTransaction FAILED");
    return { transactionId: 0, idTagInfo: { status: "Invalid" } };
  }
}