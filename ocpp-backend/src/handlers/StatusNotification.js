import { ocppResponse } from "../utils/ocppResponse.js";
import { config } from "../utils/config.js"; 

export default async function handleStatusNotification({ client, payload }) {
  const { connectorId, status, errorCode } = payload;
  const ocppId = client.identity;

  client.log.info({ connectorId, status }, "⚡ StatusNotification received");

  // Pokud je connectorId 0, jde o status celé stanice (např. Online/Offline),
  // ten do DB konektorů obvykle neukládáme, zajímají nás konektory 1, 2, ...
  if (connectorId > 0) {
    try {
      // Volání FastAPI backendu
      const response = await fetch(`${config.apiUrl}/connectors/ocpp-status`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          ocpp_id: ocppId,
          connector_number: connectorId,
          status: status,
          error_code: errorCode
        }),
      });

      if (!response.ok) {
        // Logujeme chybu, ale nepropálíme ji do nabíječky (ta jen oznamuje stav)
        client.log.error(
          { status: response.status, text: response.statusText }, 
          "❌ Failed to update connector status in API"
        );
      } else {
        const data = await response.json();
        client.log.debug({ apiResponse: data }, "✅ Connector status updated");
      }

    } catch (err) {
      client.log.error({ err }, "💥 Network error calling API backend");
    }
  }

  // Vždy vrátíme prázdnou úspěšnou odpověď
  return ocppResponse.statusNotification();
}