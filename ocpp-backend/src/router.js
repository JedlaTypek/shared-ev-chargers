import { loadHandlers } from "./utils/handlerLoader.js";
import { loadSchemas } from "./utils/schemaLoader.js";

// Načtení handlerů a schémat při startu
const handlers = await loadHandlers();

// OPRAVA: loadSchemas je funkce, musíme ji zavolat, abychom dostali mapu schémat
const schemas = loadSchemas(); 

export async function routeRequest(client, action, payload, messageId) {
  // Logování příchozího requestu
  client.log.debug({ action, payload, messageId }, "📩 Incoming request");

  const handler = handlers[action];

  if (!handler) {
    client.log.warn({ action }, "⚠️ Unknown OCPP action");
    throw {
      code: "NotImplemented",
      message: `Action ${action} not implemented`
    };
  }

  // Validace
  const validate = schemas[action]?.req?.validate;
  if (validate && !validate(payload)) {
    client.log.error({ action, errors: validate.errors }, "❌ Schema validation failed");
    throw {
      code: "FormationViolation",
      message: "Payload does not match schema"
    };
  }

  try {
      const result = await handler({ client, payload, messageId });
      client.log.debug({ action, result }, "✅ Request handled successfully");
      return result;
  } catch (error) {
      client.log.error({ action, err: error }, "💥 Error inside handler");
      throw error;
  }
}