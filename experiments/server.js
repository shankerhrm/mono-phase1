const express = require('express');
const path = require('path');

const app = express();
const port = 3002;

// Serve static files from experiments directory
app.use(express.static(path.join(__dirname)));

// Explicit routes for json files
app.get('/evolution_run.json', (req, res) => {
  res.sendFile(path.join(__dirname, 'evolution_run.json'));
});

app.get('/single_run.json', (req, res) => {
  res.sendFile(path.join(__dirname, 'single_run.json'));
});

// Serve visualize.html at root
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'visualize.html'));
});

app.listen(port, () => {
  console.log(`Visualization server running at http://localhost:${port}`);
  console.log('Open visualize.html in browser');
});
