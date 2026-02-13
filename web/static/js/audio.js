/**
 * ETS2 Truck Companion - Audio Engine (Static Interference + Alert Tones)
 */

const ETS2Audio = (function() {
    'use strict';

    let audioCtx = null;
    let sourceNode = null;
    let streamGain = null;
    let staticGain = null;
    let staticSource = null;
    let staticBuffer = null;
    let masterGain = null;

    let staticEnabled = true;
    let alertsEnabled = false;
    let currentSignal = 1.0;

    // Lazy-init AudioContext on first user interaction
    function ensureContext() {
        if (audioCtx) return true;
        try {
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();

            // Create gain nodes
            streamGain = audioCtx.createGain();
            staticGain = audioCtx.createGain();
            masterGain = audioCtx.createGain();

            streamGain.connect(masterGain);
            staticGain.connect(masterGain);
            masterGain.connect(audioCtx.destination);

            // Static noise defaults to off
            staticGain.gain.value = 0;
            streamGain.gain.value = 1;

            // Generate white noise buffer (2 seconds, mono)
            createStaticBuffer();
            startStaticLoop();

            return true;
        } catch (e) {
            console.warn('Web Audio API not available:', e);
            return false;
        }
    }

    function createStaticBuffer() {
        const sampleRate = audioCtx.sampleRate;
        const length = sampleRate * 2; // 2 seconds
        staticBuffer = audioCtx.createBuffer(1, length, sampleRate);
        const data = staticBuffer.getChannelData(0);
        for (let i = 0; i < length; i++) {
            data[i] = Math.random() * 2 - 1;
        }
    }

    function startStaticLoop() {
        if (staticSource) {
            try { staticSource.stop(); } catch (_) {}
        }
        staticSource = audioCtx.createBufferSource();
        staticSource.buffer = staticBuffer;
        staticSource.loop = true;
        staticSource.connect(staticGain);
        staticSource.start();
    }

    function connectSource(audioElement) {
        if (!ensureContext()) return;

        // Resume context if suspended (autoplay policy)
        if (audioCtx.state === 'suspended') {
            audioCtx.resume();
        }

        // Disconnect old source
        if (sourceNode) {
            try { sourceNode.disconnect(); } catch (_) {}
        }

        try {
            sourceNode = audioCtx.createMediaElementSource(audioElement);
            sourceNode.connect(streamGain);
        } catch (e) {
            // Element may already have a source node; just reconnect
            if (sourceNode) {
                sourceNode.connect(streamGain);
            }
        }
    }

    function disconnectSource() {
        if (sourceNode) {
            try { sourceNode.disconnect(); } catch (_) {}
            sourceNode = null;
        }
    }

    function updateSignal(signal) {
        currentSignal = signal;
        if (!audioCtx || !staticEnabled) return;

        const now = audioCtx.currentTime;
        const ramp = 0.3; // smooth transition time

        // Crossfade based on signal strength
        let sGain, nGain;
        if (signal >= 1.0) {
            sGain = 1.0; nGain = 0.0;
        } else if (signal >= 0.5) {
            // 1.0 -> 0.5: stream 1.0->0.8, static 0.0->0.15
            const t = (1.0 - signal) / 0.5; // 0..1
            sGain = 1.0 - t * 0.2;
            nGain = t * 0.15;
        } else if (signal >= 0.1) {
            // 0.5 -> 0.1: stream 0.8->0.4, static 0.15->0.5
            const t = (0.5 - signal) / 0.4;
            sGain = 0.8 - t * 0.4;
            nGain = 0.15 + t * 0.35;
        } else {
            // 0.1 -> 0: stream 0.4->0.0, static 0.5->0.7
            const t = (0.1 - signal) / 0.1;
            sGain = 0.4 - t * 0.4;
            nGain = 0.5 + t * 0.2;
        }

        streamGain.gain.linearRampToValueAtTime(sGain, now + ramp);
        staticGain.gain.linearRampToValueAtTime(nGain, now + ramp);

        // Occasional crackle: random gain spike on static
        if (signal < 0.8 && Math.random() < 0.05) {
            const spike = nGain + 0.15;
            staticGain.gain.setValueAtTime(spike, now + ramp + 0.01);
            staticGain.gain.linearRampToValueAtTime(nGain, now + ramp + 0.08);
        }
    }

    // ---- Alert tones ----
    function playAlertTone(type) {
        if (!alertsEnabled) return;
        if (!ensureContext()) return;

        switch (type) {
            case 'speed':
                playBeeps(800, 0.1, 2, 0.1);
                break;
            case 'fuel':
                playTone(400, 0.5);
                break;
            case 'rest':
                playBeeps(600, 0.2, 3, 0.15);
                break;
            case 'fine':
                playSweep(600, 400, 0.3);
                break;
        }
    }

    function playTone(freq, duration) {
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.frequency.value = freq;
        osc.type = 'sine';
        gain.gain.value = 0.3;
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        const now = audioCtx.currentTime;
        osc.start(now);
        gain.gain.linearRampToValueAtTime(0, now + duration);
        osc.stop(now + duration + 0.05);
    }

    function playBeeps(freq, duration, count, gap) {
        for (let i = 0; i < count; i++) {
            const delay = i * (duration + gap);
            setTimeout(() => playTone(freq, duration), delay * 1000);
        }
    }

    function playSweep(startFreq, endFreq, duration) {
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.frequency.value = startFreq;
        osc.type = 'sine';
        gain.gain.value = 0.3;
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        const now = audioCtx.currentTime;
        osc.frequency.linearRampToValueAtTime(endFreq, now + duration);
        osc.start(now);
        gain.gain.linearRampToValueAtTime(0, now + duration);
        osc.stop(now + duration + 0.05);
    }

    // ---- Settings ----
    function setStaticEnabled(enabled) {
        staticEnabled = enabled;
        if (!audioCtx) return;
        if (!enabled) {
            staticGain.gain.linearRampToValueAtTime(0, audioCtx.currentTime + 0.2);
            streamGain.gain.linearRampToValueAtTime(1, audioCtx.currentTime + 0.2);
        } else {
            updateSignal(currentSignal);
        }
    }

    function setAlertsEnabled(enabled) {
        alertsEnabled = enabled;
    }

    return {
        connectSource,
        disconnectSource,
        updateSignal,
        playAlertTone,
        setStaticEnabled,
        setAlertsEnabled,
    };
})();
