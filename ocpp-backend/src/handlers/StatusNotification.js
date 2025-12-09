import { ocppResponse } from "../utils/ocppResponse.js";
<<<<<<< HEAD
import { config } from "../utils/config.js"; // Nezapomeň, že jsme si udělali config
=======
import { config } from "../utils/config.js"; 
>>>>>>> 6fefceb4222a1a64705e382b46671648a9cf5ffe

export default async function handleStatusNotification({ client, payload }) {
  const { connectorId, status, errorCode } = payload;
  const ocppId = client.identity;

  client.log.info({ connectorId, status }, "⚡ StatusNotification received");

  // Pokud je connectorId 0, jde o status celé stanice (např. Online/Offline),
  // ten do DB konektorů obvykle neukládáme, zajímají nás konektory 1, 2, ...
  if (connectorId > 0) {
    try {
<<<<<<< HEAD
      // Volání FastAPI backendu na endpoint, který jsme připravili
      // URL: http://api:80/api/v1/connectors/ocpp-status
=======
      // Volání FastAPI backendu
>>>>>>> 6fefceb4222a1a64705e382b46671648a9cf5ffe
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
<<<<<<< HEAD
        // Logujeme chybu, ale nepropálíme ji do nabíječky. 
        // Nabíječku nezajímá, že nám spadla databáze, ona jen oznamuje stav.
=======
        // Logujeme chybu, ale nepropálíme ji do nabíječky (ta jen oznamuje stav)
>>>>>>> 6fefceb4222a1a64705e382b46671648a9cf5ffe
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

<<<<<<< HEAD
  // Vždy vrátíme prázdnou úspěšnou odpověď, aby nabíječka věděla, že jsme zprávu přijali.
=======
  // Vždy vrátíme prázdnou úspěšnou odpověď
>>>>>>> 6fefceb4222a1a64705e382b46671648a9cf5ffe
  return ocppResponse.statusNotification();
}