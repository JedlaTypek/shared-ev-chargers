import { RPCServer } from "ocpp-rpc";
import { routeRequest } from "./router.js";

async function start() {
  const server = new RPCServer({
    protocols: ["ocpp1.6"],
    strictMode: true
  });

  server.auth((accept) => accept({ sessionId: "OK" }));

  server.on("client", (client) => {
    console.log(`🔌 ${client.identity} connected`);

    client.handle(({ method, params, messageId }) => {
      return routeRequest(client, method, params, messageId);
    });
  });

  await server.listen(9000, "0.0.0.0");
  console.log("🚀 OCPP backend listening on port 9000");
}

start().catch(console.error);
