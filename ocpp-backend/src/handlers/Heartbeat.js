import { ocppResponse } from "../utils/ocppResponse.js";

export default async function handleHeartbeat({ client }) {
  console.log(`💓 Heartbeat from ${client.identity}`);
  
  // Aktualizace času "naposledy viděn" v DB nebo Redis
  
  return ocppResponse.heartbeat();
}