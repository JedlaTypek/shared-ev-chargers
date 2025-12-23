import { ocppResponse } from "../utils/ocppResponse.js";
import { config } from "../utils/config.js";

export default async function handleStartTransaction({ client, payload }) {
  const { connectorId, idTag, meterStart, timestamp } = payload;
  const ocppId = client.identity;

  client.log.info({ connectorId, idTag }, "🔌 StartTransaction request");

  try {
    const response = await fetch(`${config.apiUrl}/transactions/start`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ocpp_id: ocppId,
        connector_id: connectorId,
        id_tag: idTag,
        meter_start: meterStart,
        timestamp: timestamp
      }),
    });

    if (!response.ok) {
        throw new Error(`API Error: ${response.statusText}`);
    }

    const data = await response.json();
    const txId = data.transactionId;

    client.log.info({ txId }, "✅ Transaction started");

    // Odpověď pro nabíječku: Musí obsahovat transactionId!
    return {
        transactionId: txId,
        idTagInfo: { status: "Accepted" }
    };

  } catch (err) {
    client.log.error({ err }, "💥 Failed to start transaction via API");
    // Pokud selže API, musíme nabíjení odmítnout, jinak by jelo zadarmo
    return {
        transactionId: 0,
        idTagInfo: { status: "Invalid" }
    };
  }
}