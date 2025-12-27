import apiClient from "../utils/apiClient.js";

export default async function handleStartTransaction({ client, payload }) {
  const ocppId = client.identity;
  
  // Destrukturalizace z PAYLOAD (ne params)
  const { connectorId, idTag, meterStart, timestamp } = payload;

  client.log.info({ connectorId, idTag }, "🔌 StartTransaction request");

  try {
    // Voláme API: POST /transaction/start
    const response = await apiClient.post("/transaction/start", {
      ocpp_id: ocppId,
      connector_id: connectorId,
      id_tag: idTag,
      meter_start: meterStart,
      timestamp: timestamp,
    });

    const { transactionId } = response.data;
    client.log.info({ txId: transactionId }, "✅ Transaction started");

    return {
      transactionId: transactionId, 
      idTagInfo: {
        status: "Accepted",
      },
    };

  } catch (error) {
    client.log.error({ err: error.message }, "💥 StartTransaction failed");
    // Pokud API selže, musíme transakci odmítnout (vrátit 0)
    return {
      transactionId: 0, 
      idTagInfo: {
        status: "Invalid",
      },
    };
  }
}