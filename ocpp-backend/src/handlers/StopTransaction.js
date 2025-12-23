import { ocppResponse } from "../utils/ocppResponse.js";
import { config } from "../utils/config.js";
import axios from "axios";

export default async function handleStopTransaction({ client, payload }) {
  const { transactionId, meterStop, timestamp, idTag, reason } = payload;

  client.log.info({ transactionId, meterStop }, "🛑 StopTransaction request");

  try {
    await axios.post(`${config.apiUrl}/transactions/stop`, {
      transaction_id: transactionId,
      meter_stop: meterStop,
      timestamp: timestamp,
      id_tag: idTag,
      reason: reason
    });

    client.log.info("✅ Transaction closed");

  } catch (error) {
    client.log.error({ err: error.message }, "⚠️ Failed to close transaction via API");
  }

  return {
      idTagInfo: { status: "Accepted" }
  };
}