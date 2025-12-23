import { ocppResponse } from "../utils/ocppResponse.js";
// import axios from "axios"; // Zatím nepoužíváme, ale bude se hodit pro update "last_seen"

export default async function handleHeartbeat({ client }) {
  // Změna: Použijeme client.log místo console.log pro konzistentní JSON logy
  client.log.info("💓 Heartbeat received");
  
  // TODO: V budoucnu zde můžeš volat API:
  // await axios.post(`${config.apiUrl}/chargers/${client.identity}/heartbeat`);
  
  return ocppResponse.heartbeat();
}