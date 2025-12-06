import { loadHandlers } from "./handlerLoader.js";
import { schemas } from "./schemaLoader.js";

const handlers = await loadHandlers();

export async function routeRequest(client, action, payload, messageId) {
  const handler = handlers[action];

  if (!handler) {
    console.warn(`⚠️ Unknown OCPP action: ${action}`);
    throw {
      code: "NotImplemented",
      message: `Action ${action} not implemented`
    };
  }

  // Validate payload vs JSON schema
  const validate = schemas[action]?.req?.validate;
  if (validate && !validate(payload)) {
    console.error(`❌ Invalid payload for ${action}`, validate.errors);
    throw {
      code: "FormationViolation",
      message: "Payload does not match schema"
    };
  }

  // Run handler
  return handler({ client, payload, messageId });
}
