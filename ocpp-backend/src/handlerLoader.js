import fs from "fs";
import path from "path";

export async function loadHandlers() {
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

  return handlers;
}
