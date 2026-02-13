/**
 * ETS2 Truck Companion - Core Application Logic
 */

const ETS2App = (function() {
    'use strict';

    let currentCountry = null;
    let currentStationCard = null;
    let statusData = null;
    let updateInterval = null;
    let hlsInstance = null;
    let lastSuggestedStation = null;
    let autoSwitchEnabled = true;
    let settings = {};

    const audioPlayer = document.getElementById('audio-player');
    const messagesDiv = document.getElementById('messages');

    // ---- Tab navigation ----
    function initTabs() {
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                btn.classList.add('active');
                const tab = document.getElementById('tab-' + btn.dataset.tab);
                if (tab) tab.classList.add('active');

                // Load travel log data when switching to that tab
                if (btn.dataset.tab === 'travel' && typeof ETS2TravelLog !== 'undefined') {
                    ETS2TravelLog.refresh();
                }
            });
        });
    }

    // ---- Audio player events ----
    function initAudioEvents() {
        audioPlayer.addEventListener('loadstart', () => {
            showMessage('Loading radio stream...', 'success');
        });
        audioPlayer.addEventListener('canplay', hideMessages);
        audioPlayer.addEventListener('playing', hideMessages);
        audioPlayer.addEventListener('error', () => {
            showMessage('Failed to load radio stream. The station may be offline.', 'error');
        });
        audioPlayer.addEventListener('ended', () => {
            showMessage('Radio stream ended', 'error');
        });
    }

    // ---- Status polling ----
    function updateStatus() {
        fetch('/api/status')
            .then(r => r.json())
            .then(data => {
                statusData = data;

                // Top-level status cards
                document.getElementById('tracking-mode').textContent =
                    data.plugin_connected ? 'Plugin' : 'Manual';
                document.getElementById('current-country').textContent =
                    data.country ? capitalize(data.country) : 'None';
                document.getElementById('current-city').textContent =
                    data.city ? data.city.name : 'None';

                // Truck info card
                if (data.truck && data.truck.brand) {
                    document.getElementById('truck-info').textContent =
                        data.truck.brand + ' ' + data.truck.name;
                }

                // Coordinates
                if (data.coordinates && data.plugin_connected) {
                    document.getElementById('coordinate-display').style.display = '';
                    document.getElementById('coord-x').textContent = data.coordinates.x.toFixed(1);
                    document.getElementById('coord-y').textContent = data.coordinates.y.toFixed(1);
                    document.getElementById('coord-z').textContent = data.coordinates.z.toFixed(1);
                    document.getElementById('coord-time').textContent = new Date().toLocaleTimeString();
                } else {
                    document.getElementById('coordinate-display').style.display = 'none';
                }

                // Signal strength
                if (data.city && data.city.signal_strength !== undefined) {
                    document.getElementById('signal-display').style.display = '';
                    const s = data.city.signal_strength;
                    document.getElementById('signal-fill').style.width = (s * 100) + '%';
                    document.getElementById('signal-text').textContent =
                        (s * 100).toFixed(0) + '% - ' + data.city.name + ', ' + data.city.country;
                } else {
                    document.getElementById('signal-display').style.display = 'none';
                }

                // Dashboard update
                if (typeof ETS2Dashboard !== 'undefined') {
                    ETS2Dashboard.update(data);
                }

                // Audio static update
                if (typeof ETS2Audio !== 'undefined') {
                    ETS2Audio.updateSignal(data.signal_strength || 0);
                }

                // Process alerts from backend
                if (data.alerts && data.alerts.length > 0) {
                    // Consume alerts
                    fetch('/api/alerts').then(r => r.json()).then(alerts => {
                        alerts.forEach(a => showAlert(a));
                        if (typeof ETS2Audio !== 'undefined') {
                            alerts.forEach(a => ETS2Audio.playAlertTone(a.type));
                        }
                    });
                }

                // Auto-switching
                if (autoSwitchEnabled && data.suggested_station &&
                    data.suggested_station !== lastSuggestedStation) {

                    lastSuggestedStation = data.suggested_station;
                    let shouldAutoSwitch = false;

                    if (!data.playing_station) {
                        shouldAutoSwitch = true;
                    } else if (data.playing_station.country && data.suggested_station.country) {
                        shouldAutoSwitch =
                            data.playing_station.country.toLowerCase() !==
                            data.suggested_station.country.toLowerCase();
                    }

                    if (shouldAutoSwitch) {
                        const cards = document.querySelectorAll('.station-card');
                        for (let card of cards) {
                            const name = card.querySelector('.station-name').textContent;
                            if (name === data.suggested_station.name) {
                                showMessage('Auto-switching to ' + data.suggested_station.name, 'success');
                                playStation(data.suggested_station, card);
                                break;
                            }
                        }
                    }
                }

                // Update station list on country change
                if (data.country !== currentCountry) {
                    currentCountry = data.country;
                    displayStations(data.stations);
                    if (data.country) {
                        showMessage('Entered ' + capitalize(data.country) +
                            ' - ' + data.stations.length + ' stations available', 'success');
                    }
                }
            })
            .catch(() => {
                document.getElementById('tracking-mode').textContent = 'Error';
            });
    }

    // ---- Station display ----
    function displayStations(stations) {
        const container = document.getElementById('stations-grid');
        if (!stations || stations.length === 0) {
            container.innerHTML = '<div style="text-align:center;padding:20px;opacity:0.6;">' +
                'No stations available for this country.</div>';
            return;
        }

        container.innerHTML = '';
        stations.forEach(station => {
            const card = document.createElement('div');
            card.className = 'station-card';
            card.onclick = () => playStation(station, card);

            const logoHtml = station.logo ?
                '<img src="' + station.logo + '" alt="" onerror="this.style.display=\'none\';this.parentElement.textContent=\'📻\';">' :
                '📻';

            card.innerHTML =
                '<div class="station-logo">' + logoHtml + '</div>' +
                '<div class="station-name">' + escapeHtml(station.name) + '</div>' +
                '<div class="station-location">' +
                (station.city ? escapeHtml(station.city) + ', ' : '') +
                escapeHtml(station.country) + '</div>';

            container.appendChild(card);
        });
    }

    // ---- Playback ----
    function playStation(station, cardElement) {
        if (currentStationCard) currentStationCard.classList.remove('playing');
        currentStationCard = cardElement;
        if (cardElement) cardElement.classList.add('playing');

        document.getElementById('now-playing').textContent = 'Loading ' + station.name + '...';

        if (hlsInstance) {
            hlsInstance.destroy();
            hlsInstance = null;
        }

        // Disconnect audio graph from old source if applicable
        if (typeof ETS2Audio !== 'undefined') {
            ETS2Audio.disconnectSource();
        }

        const url = station.stream_url;

        if (url.includes('.m3u8') || url.includes('m3u8')) {
            if (typeof Hls !== 'undefined' && Hls.isSupported()) {
                hlsInstance = new Hls({ enableWorker: false, lowLatencyMode: true, backBufferLength: 90 });
                hlsInstance.loadSource(url);
                hlsInstance.attachMedia(audioPlayer);
                hlsInstance.on(Hls.Events.MANIFEST_PARSED, () => {
                    startPlayback(station);
                });
                hlsInstance.on(Hls.Events.ERROR, (_, d) => {
                    if (d.fatal) {
                        showMessage('Failed to load HLS stream.', 'error');
                        document.getElementById('now-playing').textContent = 'Error loading station';
                    }
                });
            } else if (audioPlayer.canPlayType('application/vnd.apple.mpegurl')) {
                audioPlayer.src = url;
                audioPlayer.load();
                startPlayback(station);
            } else {
                showMessage('HLS not supported in this browser.', 'error');
            }
        } else {
            audioPlayer.src = url;
            audioPlayer.load();
            startPlayback(station);
        }
    }

    function startPlayback(station) {
        audioPlayer.play().then(() => {
            document.getElementById('now-playing').textContent =
                station.name + ' - ' + (station.city ? station.city + ', ' : '') + station.country;
            hideMessages();
            notifyStationPlaying(station);

            // Connect to audio graph for static/interference
            if (typeof ETS2Audio !== 'undefined') {
                ETS2Audio.connectSource(audioPlayer);
            }
        }).catch(err => {
            if (err.name === 'NotAllowedError') {
                showMessage('Click play on the audio player to start.', 'error');
                document.getElementById('now-playing').textContent = 'Ready: ' + station.name;
            } else {
                showMessage('Failed to play station.', 'error');
            }
        });
    }

    function stopRadio() {
        if (hlsInstance) { hlsInstance.destroy(); hlsInstance = null; }
        if (typeof ETS2Audio !== 'undefined') ETS2Audio.disconnectSource();
        audioPlayer.pause();
        audioPlayer.src = '';
        document.getElementById('now-playing').textContent =
            'Select a station or drive to a city for automatic switching';
        if (currentStationCard) {
            currentStationCard.classList.remove('playing');
            currentStationCard = null;
        }
        notifyStationStopped();
        hideMessages();
    }

    function playRandomStation() {
        fetch('/api/random_station')
            .then(r => r.json())
            .then(data => {
                if (data.status === 'success') {
                    const cards = document.querySelectorAll('.station-card');
                    for (let card of cards) {
                        if (card.querySelector('.station-name').textContent === data.station.name) {
                            playStation(data.station, card);
                            return;
                        }
                    }
                    // Station not in current list, play anyway
                    playStation(data.station, null);
                } else {
                    showMessage(data.message, 'error');
                }
            })
            .catch(() => showMessage('Failed to get random station', 'error'));
    }

    function notifyStationPlaying(station) {
        fetch('/api/set_playing_station', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ station: station })
        }).catch(() => {});
    }

    function notifyStationStopped() {
        fetch('/api/stop_playing', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        }).catch(() => {});
    }

    function toggleAutoSwitch() {
        autoSwitchEnabled = !autoSwitchEnabled;
        const btn = document.getElementById('auto-switch-btn');
        btn.textContent = autoSwitchEnabled ? 'Auto-Switch: ON' : 'Auto-Switch: OFF';
        btn.className = autoSwitchEnabled ? 'btn btn-success' : 'btn btn-warning';
        showMessage(autoSwitchEnabled ? 'Auto-switching enabled' : 'Auto-switching disabled', 'success');

        // Sync with settings toggle
        const toggle = document.getElementById('setting-auto-switch');
        if (toggle) toggle.checked = autoSwitchEnabled;
        saveSetting('auto_switch_enabled', autoSwitchEnabled);
    }

    // ---- Messages ----
    function showMessage(text, type) {
        const div = document.createElement('div');
        div.className = 'message ' + (type || 'success');
        div.textContent = text;
        messagesDiv.innerHTML = '';
        messagesDiv.appendChild(div);
        setTimeout(() => { if (messagesDiv.contains(div)) messagesDiv.removeChild(div); }, 5000);
    }

    function hideMessages() { messagesDiv.innerHTML = ''; }

    // ---- Alerts ----
    function showAlert(alert) {
        const container = document.getElementById('alert-toast');
        const el = document.createElement('div');
        el.className = 'alert-item ' + alert.type;
        el.textContent = alert.message;
        container.appendChild(el);
        setTimeout(() => { if (container.contains(el)) container.removeChild(el); }, 5000);
    }

    // ---- Settings ----
    function loadSettings() {
        fetch('/api/settings')
            .then(r => r.json())
            .then(data => {
                settings = data;
                applySettings(data);
            })
            .catch(() => {});
    }

    function applySettings(s) {
        setChecked('setting-audio-alerts', s.audio_alerts_enabled);
        setChecked('setting-static', s.static_interference_enabled);
        setChecked('setting-auto-switch', s.auto_switch_enabled);
        setChecked('setting-gamepad', s.gamepad_enabled);
        setChecked('setting-dashboard', s.dashboard_visible);

        autoSwitchEnabled = s.auto_switch_enabled !== false;
        const btn = document.getElementById('auto-switch-btn');
        if (btn) {
            btn.textContent = autoSwitchEnabled ? 'Auto-Switch: ON' : 'Auto-Switch: OFF';
            btn.className = autoSwitchEnabled ? 'btn btn-success' : 'btn btn-warning';
        }

        if (typeof ETS2Audio !== 'undefined') {
            ETS2Audio.setStaticEnabled(s.static_interference_enabled !== false);
            ETS2Audio.setAlertsEnabled(!!s.audio_alerts_enabled);
        }

        const dashGauges = document.getElementById('dashboard-gauges');
        if (dashGauges) {
            dashGauges.style.display = s.dashboard_visible === false ? 'none' : '';
        }
    }

    function saveSetting(key, value) {
        settings[key] = value;
        fetch('/api/settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(settings)
        }).catch(() => {});

        // Live-apply certain settings
        if (key === 'static_interference_enabled' && typeof ETS2Audio !== 'undefined') {
            ETS2Audio.setStaticEnabled(value);
        }
        if (key === 'audio_alerts_enabled' && typeof ETS2Audio !== 'undefined') {
            ETS2Audio.setAlertsEnabled(value);
        }
        if (key === 'auto_switch_enabled') {
            autoSwitchEnabled = value;
            const btn = document.getElementById('auto-switch-btn');
            if (btn) {
                btn.textContent = value ? 'Auto-Switch: ON' : 'Auto-Switch: OFF';
                btn.className = value ? 'btn btn-success' : 'btn btn-warning';
            }
        }
        if (key === 'dashboard_visible') {
            const dg = document.getElementById('dashboard-gauges');
            if (dg) dg.style.display = value ? '' : 'none';
        }
    }

    // ---- Helpers ----
    function capitalize(s) { return s ? s.charAt(0).toUpperCase() + s.slice(1) : ''; }
    function setChecked(id, val) {
        const el = document.getElementById(id);
        if (el) el.checked = val !== false && val !== undefined;
    }
    function escapeHtml(s) {
        const d = document.createElement('div');
        d.textContent = s;
        return d.innerHTML;
    }

    function refreshStatus() {
        updateStatus();
        showMessage('Status refreshed', 'success');
    }

    function reloadStations() {
        showMessage('Reloading stations...', 'success');
        fetch('/api/reload_stations', { method: 'POST', headers: { 'Content-Type': 'application/json' } })
            .then(r => r.json())
            .then(data => {
                showMessage(data.message, data.status === 'success' ? 'success' : 'error');
                if (data.status === 'success') updateStatus();
            })
            .catch(() => showMessage('Failed to reload stations', 'error'));
    }

    // ---- Init ----
    function init() {
        initTabs();
        initAudioEvents();
        loadSettings();
        updateStatus();
        updateInterval = setInterval(updateStatus, 2000);

        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'visible') {
                if (!updateInterval) updateInterval = setInterval(updateStatus, 2000);
            } else {
                if (updateInterval) { clearInterval(updateInterval); updateInterval = null; }
            }
        });
    }

    // Start when DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Public API
    return {
        playStation,
        stopRadio,
        playRandomStation,
        toggleAutoSwitch,
        refreshStatus,
        reloadStations,
        showMessage,
        showAlert,
        saveSetting,
        getStatusData: () => statusData,
        getAudioPlayer: () => audioPlayer,
        getStationList: () => (statusData && statusData.stations) || [],
        getCurrentStationIndex: () => {
            if (!statusData || !statusData.stations || !statusData.playing_station) return -1;
            return statusData.stations.findIndex(s => s.name === statusData.playing_station.name);
        },
    };
})();
