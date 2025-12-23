import { ocppResponse } from "../utils/ocppResponse.js";
import { config } from "../utils/config.js"; 
import axios from "axios";

export default async function handleStatusNotification({ client, payload }) {
  const { connectorId, status, errorCode } = payload;
  const ocppId = client.identity;

  client.log.info({ connectorId, status }, "⚡ StatusNotification received");

  if (connectorId > 0) {
    try {
      const response = await axios.post(`${config.apiUrl}/connectors/ocpp-status`, {
        ocpp_id: ocppId,
        connector_number: connectorId,
        status: status,
        error_code: errorCode
      });

      client.log.debug({ apiResponse: response.data }, "✅ Connector status updated");

    } catch (error) {
      // Stačí jeden catch pro síťové chyby i chyby API (404/500)
      const errorDetail = error.response ? error.response.data : error.message;
      client.log.error({ err: errorDetail }, "❌ Failed to update connector status");
    }
  }

  return ocppResponse.statusNotification();
}