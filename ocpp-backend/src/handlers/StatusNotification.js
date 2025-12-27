import apiClient from "../utils/apiClient.js";
import { ocppResponse } from "../utils/ocppResponse.js";

export default async function handleStatusNotification({ client, payload }) {
  const ocppId = client.identity;
  const { connectorId, status, errorCode, info, timestamp } = payload;

  client.log.info({ connectorId, status }, "ℹ️ StatusNotification");

  // Konektor 0 je celá nabíječka, zajímají nás hlavně konektory 1+
  if (connectorId > 0) {
    try {
        await apiClient.post("/connector-status", {
            ocpp_id: ocppId,
            connector_number: connectorId,
            status: status,
            error_code: errorCode,
            info: info,
            timestamp: timestamp || new Date().toISOString()
        });
    } catch (error) {
        client.log.error({ err: error.message }, "⚠️ Failed to update status");
    }
  }

  // Odpověď je prázdná
  return {};
}