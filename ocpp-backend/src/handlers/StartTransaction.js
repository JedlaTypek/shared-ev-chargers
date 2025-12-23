import { ocppResponse } from "../utils/ocppResponse.js";
import { config } from "../utils/config.js";
import axios from "axios";

export default async function handleStartTransaction({ client, payload }) {
  const { connectorId, idTag, meterStart, timestamp } = payload;
  const ocppId = client.identity;

  client.log.info({ connectorId, idTag }, "🔌 StartTransaction request");

  try {
    const response = await axios.post(`${config.apiUrl}/transactions/start`, {
      ocpp_id: ocppId,
      connector_id: connectorId,
      id_tag: idTag,
      meter_start: meterStart,
      timestamp: timestamp
    });

    const { transactionId } = response.data;

    client.log.info({ txId: transactionId }, "✅ Transaction started");

    return {
        transactionId: transactionId,
        idTagInfo: { status: "Accepted" }
    };

  } catch (error) {
    client.log.error({ err: error.message }, "💥 Failed to start transaction via API");
    return {
        transactionId: 0,
        idTagInfo: { status: "Invalid" } // Zde by šlo vrátit i "ConcurrentTx" apod.
    };
  }
}