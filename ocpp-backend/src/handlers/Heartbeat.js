import apiClient from "../utils/apiClient.js";

export default async function handleHeartbeat({ client, payload }) {
    client.log.debug("💓 Heartbeat");

    try {
        // Forward heartbeat to API (saves to Redis)
        const response = await apiClient.post(`/heartbeat/${client.identity}`);

        return {
            currentTime: response.data.currentTime
        };
    } catch (error) {
        client.log.error({ err: error.message }, "⚠️ Failed to forward heartbeat");
        // Fallback if API is down
        return {
            currentTime: new Date().toISOString()
        };
    }
}