import { ocppResponse } from "../utils/ocppResponse.js";
import { config } from "../utils/config.js";

export default async function handleStopTransaction({ client, payload }) {
  const { transactionId, meterStop, timestamp, idTag, reason } = payload;

  client.log.info({ transactionId, meterStop }, "🛑 StopTransaction request");

  try {
    // Voláme API jen pro info (uzavření logu).
    // I když API selže, nabíječka už přestala nabíjet, takže vracíme Accepted.
    await fetch(`${config.apiUrl}/transactions/stop`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        transaction_id: transactionId,
        meter_stop: meterStop,
        timestamp: timestamp,
        id_tag: idTag,
        reason: reason
      }),
    });

    client.log.info("✅ Transaction closed");

  } catch (err) {
    client.log.error({ err }, "⚠️ Failed to close transaction via API");
  }

  // Nabíječka očekává potvrzení
  return {
      idTagInfo: { status: "Accepted" }
  };
}