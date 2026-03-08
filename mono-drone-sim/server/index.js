const WebSocket = require('ws');

const wss = new WebSocket.Server({ port: 8080 });

let drones = {}; // { droneId: {x, y, vx, vy, landed, energy, fitness, collision, agentId, generation} }
let agentCounter = 0;

function createDrone(id, x, y, gen = 1) {
    const agentId = `mono_${String(agentCounter++).padStart(3, '0')}`;
    return { id, x, y, vx: 0, vy: 0, landed: false, energy: 0, fitness: 0, collision: false, agentId, generation: gen };
}

// Fallback heuristic if MONO Core is down
function monoAIAgent(drone) {
    const targetX = 400;
    const targetY = 525;
    const dx = targetX - drone.x;
    const dy = targetY - drone.y;
    if (Math.abs(dx) < 10 && Math.abs(dy) < 10) return null;
    if (Math.abs(dx) > Math.abs(dy)) {
        return dx > 0 ? 'right' : 'left';
    } else {
        return dy > 0 ? 'down' : 'up';
    }
}

async function getCommandFromCore(drone) {
    try {
        const response = await fetch('http://127.0.0.1:8000/api/drone/control', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(drone)
        });
        const data = await response.json();
        return data.command;
    } catch (e) {
        return monoAIAgent(drone);
    }
}

async function reportTelemetry() {
    const droneList = Object.values(drones);
    if (droneList.length === 0) return;
    try {
        await fetch('http://127.0.0.1:8000/api/drone/telemetry', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(droneList)
        });
    } catch (e) { }
}

wss.on('connection', ws => {
    const droneId = `auto_${Date.now()}`;
    drones[droneId] = createDrone(droneId, Math.random() * 600 + 100, 50);

    ws.send(JSON.stringify({ droneId, drones }));

    ws.on('message', message => {
        try {
            const { command } = JSON.parse(message);
            const drone = drones[droneId];
            if (drone && !drone.landed) {
                applyCommand(drone, command, 2.0);
            }
        } catch (e) { }
    });

    ws.on('close', () => {
        delete drones[droneId];
    });
});

function applyCommand(drone, command, scalar = 1.5) {
    if (command === 'up') drone.vy -= scalar;
    else if (command === 'down') drone.vy += scalar;
    else if (command === 'left') drone.vx -= scalar;
    else if (command === 'right') drone.vx += scalar;
    drone.energy += (Math.abs(drone.vx) + Math.abs(drone.vy)) * 0.1;
}

// Initial Swarm (All Autopilot)
for (let i = 0; i < 5; i++) {
    const id = `auto_pilot_${i}`;
    drones[id] = createDrone(id, 100 + i * 140, 50);
}

// AI loop (10Hz)
setInterval(async () => {
    for (let id in drones) {
        const drone = drones[id];
        if (!drone.landed) {
            const command = await getCommandFromCore(drone);
            if (command) applyCommand(drone, command, 1.2);
        }
    }
}, 100);

// Telemetry loop (2Hz)
setInterval(reportTelemetry, 500);

function respawnDrone(id) {
    const old = drones[id];
    const newGen = old.generation + 1;
    const droneId = `auto_respawn_${Date.now()}`;
    drones[droneId] = createDrone(droneId, Math.random() * 600 + 100, 50, newGen);
    delete drones[id];
}

// Update loop (20Hz): physics + safe landing + fitness + respawn
setInterval(() => {
    for (let id in drones) {
        let d = drones[id];

        if (d.landed || d.collision) {
            // Auto-respawn after a short visual delay
            if (Math.random() < 0.05) {
                respawnDrone(id);
            }
            continue;
        }

        d.x += d.vx;
        d.y += d.vy;
        d.vx *= 0.85;
        d.vy *= 0.85;

        if (d.x <= 0 || d.x >= 800 || d.y <= 0 || d.y >= 600) {
            d.collision = true;
        }

        if (d.x > 350 && d.x < 450 && d.y > 500 && d.y < 550) {
            if (Math.abs(d.vx) < 3 && Math.abs(d.vy) < 3) {
                d.landed = true;
                d.vx = 0;
                d.vy = 0;
            }
        }

        d.x = Math.max(0, Math.min(800, d.x));
        d.y = Math.max(0, Math.min(600, d.y));

        d.fitness = (d.landed ? 100 : 0) - d.energy + (d.collision ? -50 : 0);
    }

    const state = JSON.stringify(drones);
    wss.clients.forEach(client => {
        if (client.readyState === WebSocket.OPEN) {
            client.send(state);
        }
    });
}, 50);

console.log('WebSocket server started (MONO AI Life Ecosystem Mode)');
