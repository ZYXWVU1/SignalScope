import { cpSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";

const standalone = new URL("../.next/standalone/", import.meta.url);
const server = new URL("server.js", standalone);
if (!existsSync(server)) throw new Error("Run npm run build before npm start.");
cpSync(
  new URL("../.next/static/", import.meta.url),
  new URL(".next/static/", standalone),
  {
    recursive: true,
  },
);
process.env.HOSTNAME ??= "127.0.0.1";
process.chdir(fileURLToPath(standalone));
await import(server.href);
