import axios from "axios";
import { config } from "./config.js";
import logger from "./logger.js";

const apiClient = axios.create({
  baseURL: config.apiUrl, // Použije http://api:8000/api/v1/internal
  timeout: 5000,
  headers: {
    "Content-Type": "application/json",
    // Pokud používáš API Key pro zabezpečení interní komunikace:
    ...(config.apiKey && { "x-api-key": config.apiKey }),
  },
});

// Volitelné: Logování requestů/response pro debugování (můžeš zakomentovat)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const url = error.config?.url;
    const method = error.config?.method?.toUpperCase();
    
    if (error.response) {
      // Server odpověděl chybou (4xx, 5xx)
      logger.warn(
        { status: error.response.status, url, method, data: error.response.data }, 
        "⚠️ API Error Response"
      );
    } else if (error.request) {
      // Server neodpověděl (timeout, network error)
      logger.error(
        { url, method, message: error.message }, 
        "💥 API Network Error"
      );
    }
    return Promise.reject(error);
  }
);

export default apiClient;