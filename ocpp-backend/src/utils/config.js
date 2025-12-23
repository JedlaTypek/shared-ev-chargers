// Jednoduchá kontrola, aby se nestalo, že proměnná chybí
if (!process.env.API_URL) {
  console.warn("⚠️ API_URL is missing in .env! Using default http://api:80/api/v1");
}

export const config = {
  port: process.env.PORT || 9000,
  apiUrl: process.env.API_URL || "http://api:80/api/v1",
  logLevel: process.env.LOG_LEVEL || "info",
};