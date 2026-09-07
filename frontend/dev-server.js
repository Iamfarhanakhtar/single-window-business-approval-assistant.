const { createServer } = require("http");
const { parse } = require("url");
const next = require("next");

const dev = process.env.NODE_ENV !== "production";
const hostname = "0.0.0.0";
const port = parseInt(process.env.PORT || "3000", 10);

const app = next({ dev, hostname, port, dir: __dirname });
const handle = app.getRequestHandler();

let isPrepared = false;
console.log(`[Next.js Server] Initializing on http://localhost:${port} (dev=${dev})...`);

const preparePromise = app.prepare().then(() => {
  isPrepared = true;
  console.log(`[Next.js Server] Ready and compiled on http://localhost:${port}`);
}).catch(err => {
  console.error("[Next.js Server] Prepare error:", err);
});

const server = createServer(async (req, res) => {
  try {
    if (!isPrepared) {
      await preparePromise;
    }
    const parsedUrl = parse(req.url, true);
    await handle(req, res, parsedUrl);
  } catch (err) {
    console.error("Error handling request:", err);
    res.statusCode = 500;
    res.end("Internal Server Error");
  }
});

server.listen(port, hostname, () => {
  console.log(`[Next.js Server] Socket bound to http://localhost:${port}`);
});
