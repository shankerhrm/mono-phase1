let ws = new WebSocket('ws://localhost:8080');
let drones = {};
let myDroneId = null;

const config = {
    type: Phaser.AUTO,
    width: 800,
    height: 600,
    backgroundColor: '#222',
    physics: { default: 'arcade' },
    scene: {
        preload: preload,
        create: create,
        update: update
    },
    parent: 'body'
};

const game = new Phaser.Game(config);
let droneSprites = {};
let droneLabels = {};
let landingZone;
let leaderboardText;

function preload() { }

function create() {
    landingZone = this.add.rectangle(400, 525, 100, 50, 0x00ff00);
    this.add.text(400, 525, 'LANDING ZONE', { fontSize: '12px', color: '#000', fontStyle: 'bold' }).setOrigin(0.5);

    ws.onmessage = (msg) => {
        const data = JSON.parse(msg.data);
        if (data.droneId && data.drones) {
            myDroneId = data.droneId;
            drones = data.drones;
        } else {
            drones = data;
        }
    };

    this.input.keyboard.on('keydown', (event) => {
        if (ws.readyState === WebSocket.OPEN) {
            const keyMap = { ArrowUp: 'up', ArrowDown: 'down', ArrowLeft: 'left', ArrowRight: 'right', w: 'up', s: 'down', a: 'left', d: 'right' };
            if (keyMap[event.key]) ws.send(JSON.stringify({ command: keyMap[event.key] }));
        }
    });

    this.add.text(10, 10, 'MONO AI Drone Training Ground (Phase 31.3)', { fontSize: '18px', fill: '#00ff00', fontStyle: 'bold' });

    leaderboardText = this.add.text(600, 20, '', {
        fontSize: '14px',
        fill: '#00ff00',
        backgroundColor: '#000000',
        padding: { x: 10, y: 10 }
    }).setScrollFactor(0);
}

function update() {
    // Leaderboard Update
    const topAgents = Object.values(drones)
        .sort((a, b) => b.fitness - a.fitness)
        .slice(0, 5);

    let leaderboardStr = "--- TOP AGENTS ---\n";
    topAgents.forEach(d => {
        leaderboardStr += `${d.agentId} (G${d.generation}): ${Math.round(d.fitness)}\n`;
    });
    if (leaderboardText) leaderboardText.setText(leaderboardStr);

    for (let id in drones) {
        const d = drones[id];

        // Create if missing
        if (!droneSprites[id]) {
            droneSprites[id] = this.add.circle(d.x, d.y, 10, 0xff00ff);
            droneLabels[id] = this.add.text(d.x, d.y - 30, '', { fontSize: '11px', fill: '#ffffff' }).setOrigin(0.5);
        }

        // Update positions
        droneSprites[id].x = d.x;
        droneSprites[id].y = d.y;
        droneLabels[id].x = d.x;
        droneLabels[id].y = d.y - 40;

        // Life-value visualization
        if (d.landed) {
            droneSprites[id].fillColor = 0x00ffff;
        } else if (d.collision) {
            droneSprites[id].fillColor = 0x666666;
        } else {
            // Heat map based on energy
            const heat = Math.min(d.energy / 100, 1);
            const r = 255;
            const b = Math.floor(255 * (1 - heat));
            droneSprites[id].fillColor = (r << 16) | (0 << 8) | b;
        }

        // Enhanced HUD content
        droneLabels[id].setText(
            `${d.agentId} G${d.generation}\nFit: ${Math.round(d.fitness)} En: ${Math.round(d.energy)}`
        );
    }

    // Cleanup
    for (let id in droneSprites) {
        if (!drones[id]) {
            droneSprites[id].destroy();
            droneLabels[id].destroy();
            delete droneSprites[id];
            delete droneLabels[id];
        }
    }
}
