import { loadHandlers } from "./handlerLoader.js";
import { schemas } from "./schemaLoader.js";

// Handlery načteme jen jednou při startu
const handlers = await loadHandlers();

export async function routeRequest(client, action, payload, messageId) {
  // Logování příchozího requestu (jako DEBUG, aby to nezahlcovalo produkci)
  client.log.debug({ action, payload, messageId }, "📩 Incoming request");

  const handler = handlers[action];

  if (!handler) {
    client.log.warn({ action }, "⚠️ Unknown OCPP action");
    throw {
      code: "NotImplemented",
      message: `Action ${action} not implemented`
    };
  }

  // Validate payload vs JSON schema
  const validate = schemas[action]?.req?.validate;
  if (validate && !validate(payload)) {
    client.log.error({ action, errors: validate.errors }, "❌ Schema validation failed");
    throw {
      code: "FormationViolation",
      message: "Payload does not match schema"
    };
  }

  try {
      // Spuštění handleru
      const result = await handler({ client, payload, messageId });
      
      // Logování úspěšné odpovědi (také spíše DEBUG)
      client.log.debug({ action, result }, "✅ Request handled successfully");
      
      return result;
  } catch (error) {
      // Logování chyby při zpracování v handleru
      client.log.error({ action, err: error }, "💥 Error inside handler");
      throw error; // Poslat chybu zpět nabíječce
  }
}