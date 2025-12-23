import { RPCServer } from "ocpp-rpc";
import { routeRequest } from "./router.js";
import logger from "./utils/logger.js";
import { config } from "./utils/config.js";
import axios from "axios"; 

async function start() {
  const server = new RPCServer({
    protocols: ["ocpp1.6"],
    strictMode: true
  });

  // 1. Změna signatury: (accept, reject, handshake)
  server.auth(async (accept, reject, handshake) => {
      // 2. Získání identity z handshake objektu
      const { identity } = handshake;

      // 3. Oprava logování (Pino syntaxe: objekt první, zpráva druhá)
      logger.info({ identity }, "🔐 Auth request (Handshake)");

      try {
          // Volání API pro ověření
          const response = await axios.get(
              `${config.apiUrl}/chargers/exists/${identity}`,
              { timeout: 5000 }
          );

          // API vrátilo 200 OK -> máme ID
          const { id } = response.data;
          
          logger.info({ identity, dbId: id }, "✅ Charger authorized");

          // Přijmeme spojení a předáme ID dál
          accept({ 
              identity,
              dbId: id
          });

      } catch (error) {
          // Chyba při ověření (404/403 nebo výpadek API)
          if (error.response && (error.response.status === 404 || error.response.status === 403)) {
              logger.warn({ identity, status: error.response.status }, "🚫 Auth failed: Charger rejected by API");
              reject(404); 
          } else {
              logger.error({ identity, err: error.message }, "💥 Auth error: API unreachable");
              reject(500); 
          }
      }
  });

  server.on("client", (client) => {
    // Vytáhneme data ze session (která jsme tam dali v auth)
    const sessionId = client.session.sessionId;
    const dbId = client.session.dbId; 

    // Vytvoříme logger pro tohoto klienta
    client.log = logger.child({ 
        identity: client.identity, 
        sessionId: sessionId,
        dbId: dbId 
    });
    
    // Uložíme ID na klienta pro snadný přístup v handlerech
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
  
  // 4. Oprava logování na konci (použití template stringu nebo objektu)
  logger.info({ port: config.port }, "🚀 OCPP backend listening");
}

start().catch((err) => {
    logger.fatal(err, "💥 Startup failed");
});