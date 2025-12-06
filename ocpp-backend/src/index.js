import { RPCServer } from "ocpp-rpc";
import { routeRequest } from "./router.js";
import logger from "./utils/logger.js"; // Import loggeru

async function start() {
  const server = new RPCServer({
    protocols: ["ocpp1.6"],
    strictMode: true
  });

  server.auth((accept, { sessionId, identity }) => {
      // Zde logujeme pokus o auth
      logger.info({ sessionId, identity }, "🔐 Auth request");
      // TODO: Logika ověření hesla v DB
      accept({ sessionId });
  });

  server.on("client", (client) => {
    // Vytvoříme child logger specifický pro toto připojení
    // Každý log přes 'client.log' bude mít automaticky { identity: "..." }
    client.log = logger.child({ 
        identity: client.identity, 
        sessionId: client.session.sessionId 
    });

    client.log.info("🔌 Connected");

    client.handle(async ({ method, params, messageId }) => {
      // Předáme logování i do routeru
      return routeRequest(client, method, params, messageId);
    });

    client.on("disconnect", () => {
        client.log.info("❌ Disconnected");
    });
  });

  await server.listen(9000, "0.0.0.0");
  logger.info("🚀 OCPP backend listening on port 9000");
}

start().catch((err) => {
    logger.fatal(err, "💥 Startup failed");
});