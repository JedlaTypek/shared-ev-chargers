import apiClient from "../utils/apiClient.js";

export default async function handleAuthorize({ client, payload }) {
  const ocppId = client.identity;
  const { idTag } = payload; // V payloadu je idTag

  client.log.info({ idTag }, "🔒 Authorize request");

  try {
    // Voláme API: POST /chargers/authorize/{ocppId}
    // (Předpokládám, že charger router je na prefixu /chargers)
    const response = await apiClient.post(`/authorize/${ocppId}`, {
      id_tag: idTag,
    });

    // Backend vrací { "idTagInfo": { "status": "Accepted", ... } }
    client.log.info({ status: response.data.idTagInfo.status }, "🔒 Authorized");
    
    return {
      idTagInfo: response.data.idTagInfo,
    };

  } catch (error) {
    client.log.warn({ err: error.message }, "⚠️ Authorization failed");
    return {
      idTagInfo: {
        status: "Invalid", 
      },
    };
  }
}