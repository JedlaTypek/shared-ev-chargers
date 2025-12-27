import apiClient from "../utils/apiClient.js";

export default async function handleStopTransaction({ client, payload }) {
  // StopTransaction v OCPP 1.6 nemá connectorId v hlavním těle,
  // ale transactionId je unikátní.
  const { transactionId, meterStop, timestamp, idTag, reason } = payload;

  client.log.info({ transactionId, meterStop, reason }, "🛑 StopTransaction request");

  try {
    // Voláme API: POST /transaction/stop
    await apiClient.post("/transaction/stop", {
      transaction_id: transactionId,
      meter_stop: meterStop,
      timestamp: timestamp,
      id_tag: idTag, 
      reason: reason
    });

    client.log.info("✅ Transaction stopped in DB");

    return {
      idTagInfo: {
        status: "Accepted",
      },
    };

  } catch (error) {
    client.log.error({ err: error.message }, "⚠️ StopTransaction API failed");
    // I když API selže, nabíječce řekneme OK, jinak by zprávu posílala pořád dokola.
    return {
      idTagInfo: {
        status: "Accepted",
      },
    };
  }
}