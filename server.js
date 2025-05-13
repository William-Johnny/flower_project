const express = require("express");
const http = require("http");
const WebSocket = require("ws");
const path = require("path");

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });
const { exec } = require("child_process");

// Serve static files from "public" directory
app.use(express.static(path.join(__dirname, "public")));

// Route `/` to index.html
app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "index.html"));
});

// Handle WebSocket messages
wss.on("connection", (ws) => {
  console.log("🔌 New WebSocket connection");

  ws.on("message", (message) => {
    try {
      const data = JSON.parse(message);
      console.log("🟢 Received from client:", data.pressed);
      if (data.pressed === true) {
        const pythonScript = path.join(__dirname, "flowerProject.py");
        const command = `~/miniforge3/bin/python "${pythonScript}"`;

        exec(command, (error, stdout, stderr) => {
          if (error) {
            console.error("❌ Error running transcription:", error);
            return;
          }
          if (stderr) {
            console.error("⚠️ Python error:", stderr);
          }

          console.log("📝 Transcription result:");
          console.log(stdout);
        });
      }
    } catch (e) {
      console.error("⚠️ Invalid message format", e);
    }
  });

  ws.on("close", () => {
    console.log("🔌 Client disconnected");
  });
});

// Start the HTTP & WebSocket server
const PORT = 8080;
const HOST = "192.168.1.71"; // or your specific IP, like '192.168.1.42'

server.listen(PORT, HOST, () => {
  console.log(`🚀 Server running at http://${HOST}:${PORT}`);
});
