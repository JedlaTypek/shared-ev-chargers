import fs from "fs";
import path from "path";
import Ajv from "ajv";
import addFormats from "ajv-formats";

const ajv = new Ajv({ allErrors: true });
addFormats(ajv);

export function loadSchemas() {
  const schemasDir = path.join(process.cwd(), "src/schemas");
  const files = fs.readdirSync(schemasDir);

  const map = {}; // { BootNotification: { req, res } }

  for (const file of files) {
    if (!file.endsWith(".json")) continue;

    const fullPath = path.join(schemasDir, file);

    // načti schema
    const schema = JSON.parse(fs.readFileSync(fullPath, "utf8"));

    // získat název bez "Request"/"Response" části
    const base = file.replace(".json", "");
    const isResponse = base.endsWith("Response");

    const action = isResponse
      ? base.replace("Response", "")
      : base;

    // inicializace prázdného objektu, pokud neexistuje
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
  }

  return map;
}
