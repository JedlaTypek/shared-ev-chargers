import fs from "fs";
import path from "path";
import Ajv from "ajv";
import addFormats from "ajv-formats";
import logger from "./logger.js"; 

const ajv = new Ajv({ allErrors: true });
addFormats(ajv);

export function loadSchemas() {
  // Cesta k adresáři se schématy. 
  // process.cwd() vrací kořen projektu, takže cesta "src/schemas" je správná, 
  // pokud spouštíš aplikaci příkazem `npm start` z kořenové složky.
  const schemasDir = path.join(process.cwd(), "src/schemas");

  // Kontrola, zda složka existuje
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
      // Načtení a parsování schématu
      const schema = JSON.parse(fs.readFileSync(fullPath, "utf8"));

      // Získat název akce bez "Request"/"Response" a přípony
      // Např. "BootNotificationResponse.json" -> "BootNotification"
      const base = file.replace(".json", "");
      const isResponse = base.endsWith("Response");

      const action = isResponse
        ? base.replace("Response", "")
        : base;

      // Inicializace prázdného objektu pro danou akci, pokud neexistuje
      if (!map[action]) map[action] = {};

      // Kompilace schématu pomocí AJV
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
      // Pokud je JSON poškozený, logujeme chybu, ale neshodíme celý server
      logger.error({ err, file }, `❌ Failed to load schema ${file}`);
    }
  }

  // Logování úspěchu
  const count = Object.keys(map).length;
  logger.info(`📜 Loaded schemas for ${count} OCPP actions`);

  return map;
}