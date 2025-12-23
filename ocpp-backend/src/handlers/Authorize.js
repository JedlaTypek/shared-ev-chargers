import { ocppResponse } from "../utils/ocppResponse.js";
import { config } from "../utils/config.js";
import axios from "axios";

export default async function handleAuthorize({ client, payload }) {
  const { idTag } = payload;
  const ocppId = client.identity;

  client.log.info({ idTag }, "🔒 Authorize request received");

  try {
    const response = await axios.post(`${config.apiUrl}/chargers/authorize/${ocppId}`, {
      id_tag: idTag
    });

    const data = response.data;
    
    client.log.info(
      { status: data.idTagInfo.status },
      "🔒 Authorization processed"
    );

    return { idTagInfo: data.idTagInfo };

  } catch (error) {
    // Ať už je to 404 (karta neexistuje) nebo 500 (chyba serveru), odmítneme
    client.log.warn({ err: error.message }, "⚠️ Authorization failed");
    return ocppResponse.authorize("Invalid");
  }
}