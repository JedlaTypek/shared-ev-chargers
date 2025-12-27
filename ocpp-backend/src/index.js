import { RPCServer } from "ocpp-rpc";
import { routeRequest } from "./router.js";
import logger from "./utils/logger.js";
import { config } from "./utils/config.js";
// ZMĚNA: Importujeme našeho klienta místo axiosu
import apiClient from "./utils/apiClient.js"; 

async function start() {
  const server = new RPCServer({
    protocols: ["ocpp1.6"],
    strictMode: true
  });

  server.auth(async (accept, reject, handshake) => {
      const { identity } = handshake;

      logger.info({ identity }, "🔐 Auth request (Handshake)");

      try {
          const response = await apiClient.get(`/charger/exists/${identity}`);

          const { id } = response.data;
          
          logger.info({ identity, dbId: id }, "✅ Charger authorized");

          accept({ 
              identity,
              dbId: id
          });

      } catch (error) {
          // apiClient (axios) vyhodí error při stauts 4xx/5xx
          if (error.response && (error.response.status === 404 || error.response.status === 403)) {
              logger.warn({ identity, status: error.response.status }, "🚫 Auth failed: Charger rejected by API");
              reject(404); 
          } else {
              // Logování chyby už částečně řeší apiClient, ale tady to potřebujeme pro reject
              // logger.error je zde redundantní pokud máš interceptor v apiClient, ale nevadí to
              logger.error({ identity, err: error.message }, "💥 Auth error: API unreachable");
              reject(500); 
          }
      }
  });

  server.on("client", (client) => {
    const sessionId = client.session.sessionId;
    const dbId = client.session.dbId; 

    client.log = logger.child({ 
        identity: client.identity, 
        sessionId: sessionId,
        dbId: dbId 
    });
    
    client.dbId = dbId;

    client.log.info("🔌 Connected");

    client.handle(async ({ method, params, messageId }) => {
      return routeRequest(client, method, params, messageId);
    });

    client.on("disconnect", () => {
        client.log.info("❌ Disconnected");
    });
  });

  await server.listen(config.port, "0.0.0.0");
  
  logger.info({ port: config.port }, "🚀 OCPP backend listening");
}

start().catch((err) => {
    logger.fatal(err, "💥 Startup failed");
});