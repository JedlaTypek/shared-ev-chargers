import fs from "fs";
import path from "path";
import logger from "./logger.js"; 

export async function loadHandlers() {
  // process.cwd() vrací kořen projektu, takže cesta k handlers zůstává "src/handlers"
  // To je v pořádku, pokud spouštíš appku z kořene projektu.
  const handlersDir = path.join(process.cwd(), "src/handlers");
  const files = fs.readdirSync(handlersDir);

  const handlers = {};

  for (const file of files) {
    if (!file.endsWith(".js")) continue;

    const name = path.basename(file, ".js");
    const modulePath = path.join(handlersDir, file);

    const handlerModule = await import(modulePath);
    handlers[name] = handlerModule.default;
  }
  
  // (Volitelné) Logování
  if (logger) logger.info(`📂 Loaded ${Object.keys(handlers).length} OCPP handlers`);

  return handlers;
}