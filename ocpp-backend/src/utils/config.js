// Kontrola existence klíčových proměnných
if (!process.env.BACKEND_INTERNAL_URL) {
  console.warn("⚠️ BACKEND_INTERNAL_URL is missing in .env! Using default http://api:8000/api/v1/internal");
}

if (!process.env.OCPP_API_KEY) {
  console.warn("⚠️ OCPP_API_KEY is missing in .env! Security is compromised.");
}

export const config = {
  port: process.env.PORT || 9000,
  logLevel: process.env.LOG_LEVEL || "info",

  // Původní URL (pokud je ještě potřeba pro staré části kódu)
  apiUrl: process.env.API_URL || "http://api:8000/api/v1",

  // Nová interní URL pro volání Internal API (Boot, Authorize, atd.)
  backendInternalUrl: process.env.BACKEND_INTERNAL_URL || "http://api:8000/api/v1/internal",

  // Načtení API klíče
  ocppApiKey: process.env.OCPP_API_KEY,
};