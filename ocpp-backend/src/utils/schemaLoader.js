import fs from "fs";
import path from "path";
import Ajv from "ajv";
import addFormats from "ajv-formats";
import logger from "./logger.js"; 

// 1. Inicializace AJV s vypnutou striktní kontrolou
const ajv = new Ajv({ 
  allErrors: true,
  strict: false,        // Ignoruje varování o chybějících definicích
  validateSchema: false // Nevaliduje samotné schéma (to způsobuje tu chybu)
});
addFormats(ajv);

export function loadSchemas() {
  const schemasDir = path.join(process.cwd(), "src/schemas");

  if (!fs.existsSync(schemasDir)) {
    logger.error(`❌ Schemas directory not found at: ${schemasDir}`);
    return {};
  }

  const files = fs.readdirSync(schemasDir);
  const map = {}; 

  for (const file of files) {
    if (!file.endsWith(".json")) continue;

    const fullPath = path.join(schemasDir, file);

    try {
      const content = fs.readFileSync(fullPath, "utf8");
      const schema = JSON.parse(content);

      // 2. KLÍČOVÁ OPRAVA: Odstraníme odkaz na starou verzi JSON schématu
      // Tím zabráníme chybě "no schema with key or ref..."
      delete schema.$schema; 
      
      // Pokus o další čištění ID, které někdy dělá problémy
      delete schema.id; 

      const base = file.replace(".json", "");
      const isResponse = base.endsWith("Response");
      const action = isResponse ? base.replace("Response", "") : base;

      if (!map[action]) map[action] = {};

      if (isResponse) {
        map[action].res = {
          raw: schema,
          validate: ajv.compile(schema)
        };
      } else {
        map[action].req = {
          raw: schema,
          validate: ajv.compile(schema)
        };
      }
    } catch (err) {
      logger.error({ err, file }, `❌ Failed to load schema ${file}`);
    }
  }

  const count = Object.keys(map).length;
  logger.info(`📜 Loaded schemas for ${count} OCPP actions`);

  return map;
}