const express = require('express');
const cors = require('cors');
const WebSocket = require('ws');

const app = express();
const PORT = 4000;

// Middleware
app.use(cors());
app.use(express.json());

// Routes
app.get('/health', (req, res) => {
  res.json({ status: 'OK' });
});

// Start REST server
const server = app.listen(PORT, () => {
  console.log(`REST API running at http://localhost:${PORT}`);
});

// WebSocket Server
const wss = new WebSocket.Server({ server });
wss.on('connection', (ws) => {
  console.log('WS client connected');
  ws.on('message', (msg) => {
    console.log('Received:', msg.toString());
    ws.send(`Echo: ${msg}`);
  });
});
