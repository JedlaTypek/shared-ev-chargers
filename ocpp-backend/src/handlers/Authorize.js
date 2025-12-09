import { ocppResponse } from "../utils/ocppResponse.js";
import { config } from "../utils/config.js";

export default async function handleAuthorize({ client, payload }) {
  const { idTag } = payload;
  const ocppId = client.identity; // ID nabíječky z WebSocket spojení

  client.log.info({ idTag }, "🔒 Authorize request received");

  try {
    // Sestavení URL pro volání FastAPI backendu
    const url = `${config.apiUrl}/chargers/authorize/${ocppId}`;

    // Volání API
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        id_tag: idTag // FastAPI očekává snake_case "id_tag"
      }),
    });

    // Pokud API vrátí chybu (např. 404 - nabíječka neexistuje, nebo 500)
    if (!response.ok) {
      client.log.warn(
        { status: response.status, statusText: response.statusText },
        "⚠️ Authorization API failed"
      );
      // Fail-safe: Pokud API nefunguje, kartu raději odmítneme
      return ocppResponse.authorize("Invalid");
    }

    // Zpracování odpovědi
    // API vrací: { "idTagInfo": { "status": "Accepted", ... } }
    const data = await response.json();

    client.log.info(
      { status: data.idTagInfo.status },
      "🔒 Authorization processed"
    );

    // Vrátíme idTagInfo přesně tak, jak nám ho poslalo API
    return { idTagInfo: data.idTagInfo };

  } catch (error) {
    // Chyba sítě (API je nedostupné)
    client.log.error({ err: error }, "💥 Failed to contact API for authorization");
    
    // Z bezpečnostních důvodů při výpadku sítě kartu odmítneme
    return ocppResponse.authorize("Invalid");
  }
}