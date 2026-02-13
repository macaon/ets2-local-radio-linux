/**
 * ETS2 Truck Companion - Gamepad Support
 */

const ETS2Gamepad = (function() {
    'use strict';

    let gamepadIndex = null;
    let rafId = null;
    let lastButtonState = {};
    const DEBOUNCE_MS = 300;
    let lastActionTime = {};
    let enabled = true;

    // Standard gamepad button mapping
    // D-pad: buttons 12(up), 13(down), 14(left), 15(right)
    const ACTIONS = {
        14: 'prevStation',  // D-pad left
        15: 'nextStation',  // D-pad right
        12: 'volumeUp',     // D-pad up
        13: 'volumeDown',   // D-pad down
    };

    function init() {
        window.addEventListener('gamepadconnected', onConnect);
        window.addEventListener('gamepaddisconnected', onDisconnect);
    }

    function onConnect(e) {
        gamepadIndex = e.gamepad.index;
        console.log('Gamepad connected:', e.gamepad.id);
        showIndicator(true);
        if (!rafId) pollLoop();
    }

    function onDisconnect(e) {
        if (e.gamepad.index === gamepadIndex) {
            gamepadIndex = null;
            showIndicator(false);
            if (rafId) { cancelAnimationFrame(rafId); rafId = null; }
        }
    }

    function pollLoop() {
        if (gamepadIndex === null || !enabled) {
            rafId = requestAnimationFrame(pollLoop);
            return;
        }

        const gp = navigator.getGamepads()[gamepadIndex];
        if (!gp) {
            rafId = requestAnimationFrame(pollLoop);
            return;
        }

        const now = Date.now();

        for (const [btnIdx, action] of Object.entries(ACTIONS)) {
            const btn = gp.buttons[btnIdx];
            if (!btn) continue;

            const pressed = btn.pressed;
            const wasPressed = lastButtonState[btnIdx] || false;

            // Trigger on press edge (not hold) with debounce
            if (pressed && !wasPressed) {
                const lastTime = lastActionTime[action] || 0;
                if (now - lastTime >= DEBOUNCE_MS) {
                    executeAction(action);
                    lastActionTime[action] = now;
                }
            }

            lastButtonState[btnIdx] = pressed;
        }

        rafId = requestAnimationFrame(pollLoop);
    }

    function executeAction(action) {
        const stations = ETS2App.getStationList();
        const audioPlayer = ETS2App.getAudioPlayer();
        let idx;

        switch (action) {
            case 'prevStation':
                idx = ETS2App.getCurrentStationIndex();
                if (stations.length === 0) break;
                idx = idx <= 0 ? stations.length - 1 : idx - 1;
                playStationByIndex(idx, stations);
                break;

            case 'nextStation':
                idx = ETS2App.getCurrentStationIndex();
                if (stations.length === 0) break;
                idx = (idx + 1) % stations.length;
                playStationByIndex(idx, stations);
                break;

            case 'volumeUp':
                if (audioPlayer) {
                    audioPlayer.volume = Math.min(1, audioPlayer.volume + 0.1);
                }
                break;

            case 'volumeDown':
                if (audioPlayer) {
                    audioPlayer.volume = Math.max(0, audioPlayer.volume - 0.1);
                }
                break;
        }
    }

    function playStationByIndex(idx, stations) {
        const station = stations[idx];
        if (!station) return;

        // Find the card in DOM
        const cards = document.querySelectorAll('.station-card');
        let targetCard = null;
        for (const card of cards) {
            const name = card.querySelector('.station-name');
            if (name && name.textContent === station.name) {
                targetCard = card;
                break;
            }
        }

        ETS2App.playStation(station, targetCard);
        ETS2App.showMessage('Gamepad: ' + station.name, 'success');
    }

    function showIndicator(visible) {
        const el = document.getElementById('gamepad-indicator');
        if (el) {
            el.classList.toggle('visible', visible);
        }
    }

    function setEnabled(val) {
        enabled = val;
        if (!val) showIndicator(false);
        else if (gamepadIndex !== null) showIndicator(true);
    }

    // Auto-init
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    return { setEnabled };
})();
