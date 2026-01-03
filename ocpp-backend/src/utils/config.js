// ocpp-backend/src/config.js
export const config = {
    port: process.env.OCPP_PORT || 9001,
    apiKey: process.env.API_KEY,
    apiUrl: process.env.API_URL || 'http://api:8000',
    // Logging a Prostředí
    debug: process.env.DEBUG === 'true',
    logLevel: process.env.LOG_LEVEL || 'info',
    nodeEnv: process.env.NODE_ENV || 'development'
};