import { ocppResponse } from "../utils/ocppResponse.js";

export default async function handleBootNotification({ client, payload }) {
  console.log(`📦 BootNotification from ${client.identity}:`, payload);

  // Zde bys v budoucnu ověřil nabíječku v DB
  // const charger = await db.getCharger(client.identity);
  
  // Pokud je vše OK, vrátíme Accepted a interval 300s (5 minut)
  return ocppResponse.bootNotification("Accepted", 300);
}