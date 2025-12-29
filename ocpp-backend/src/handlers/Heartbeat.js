// src/handlers/Heartbeat.js
export default async function handleHeartbeat({ client, payload }) {
    // client.log.debug("💓 Heartbeat"); 
    return {
        currentTime: new Date().toISOString()
    };
}