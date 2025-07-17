#!/usr/bin/env python3
"""
HTML templates for ETS2 Local Radio web interface
"""

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>ETS2 Local Radio - Linux Fork</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/hls.js/1.4.12/hls.min.js"></script>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
            margin: 0;
        }
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .status-card {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        .status-value {
            font-size: 2em;
            font-weight: bold;
            color: #4CAF50;
            margin-bottom: 5px;
        }
        .status-label {
            font-size: 0.9em;
            opacity: 0.8;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .coordinate-display {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        .coordinate-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        .coordinate-item {
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        .coordinate-value {
            font-size: 1.5em;
            font-weight: bold;
            color: #03A9F4;
        }
        .signal-strength {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        .signal-bar {
            width: 100%;
            height: 25px;
            background: rgba(255,255,255,0.2);
            border-radius: 12px;
            overflow: hidden;
            margin: 15px 0;
        }
        .signal-fill {
            height: 100%;
            background: linear-gradient(90deg, #f44336, #ff9800, #4caf50);
            transition: width 0.5s ease;
            border-radius: 12px;
        }
        .player-section {
            background: rgba(255,255,255,0.1);
            padding: 25px;
            border-radius: 12px;
            margin-bottom: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        .now-playing {
            font-size: 1.2em;
            margin-bottom: 20px;
            text-align: center;
            min-height: 30px;
        }
        .audio-player {
            width: 100%;
            max-width: 500px;
            margin: 20px auto;
            display: block;
        }
        .controls {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin: 20px 0;
            flex-wrap: wrap;
        }
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 500;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
        }
        .btn-primary {
            background: #2196F3;
            color: white;
        }
        .btn-primary:hover {
            background: #1976D2;
            transform: translateY(-2px);
        }
        .btn-success {
            background: #4CAF50;
            color: white;
        }
        .btn-success:hover {
            background: #45a049;
            transform: translateY(-2px);
        }
        .btn-warning {
            background: #FF9800;
            color: white;
        }
        .btn-warning:hover {
            background: #F57C00;
            transform: translateY(-2px);
        }
        .stations-section {
            background: rgba(255,255,255,0.1);
            padding: 25px;
            border-radius: 12px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        .stations-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        .station-card {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s ease;
            border: 2px solid transparent;
            text-align: center;
        }
        .station-card:hover {
            transform: translateY(-5px);
            background: rgba(255,255,255,0.2);
            border-color: rgba(255,255,255,0.3);
        }
        .station-card.playing {
            background: rgba(76, 175, 80, 0.3);
            border-color: rgba(76, 175, 80, 0.6);
        }
        .station-logo {
            width: 64px;
            height: 64px;
            margin: 0 auto 15px;
            background: rgba(255,255,255,0.2);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            overflow: hidden;
        }
        .station-logo img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            border-radius: 50%;
        }
        .station-name {
            font-size: 1.1em;
            font-weight: bold;
            margin-bottom: 8px;
        }
        .station-location {
            font-size: 0.9em;
            opacity: 0.8;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .message {
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            text-align: center;
            font-weight: 500;
        }
        .message.success {
            background: rgba(76, 175, 80, 0.2);
            border: 1px solid rgba(76, 175, 80, 0.5);
        }
        .message.error {
            background: rgba(244, 67, 54, 0.2);
            border: 1px solid rgba(244, 67, 54, 0.5);
        }
        .hidden {
            display: none;
        }
        @media (max-width: 768px) {
            .status-grid {
                grid-template-columns: 1fr;
            }
            .coordinate-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            .controls {
                flex-direction: column;
                align-items: center;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚛 ETS2 Local Radio</h1>
            <p>Linux Fork - Real-time Location-based Radio</p>
        </div>
        
        <div class="status-grid">
            <div class="status-card">
                <div class="status-value" id="tracking-mode">Loading...</div>
                <div class="status-label">Tracking Mode</div>
            </div>
            <div class="status-card">
                <div class="status-value" id="current-country">-</div>
                <div class="status-label">Current Country</div>
            </div>
            <div class="status-card">
                <div class="status-value" id="current-city">-</div>
                <div class="status-label">Current City</div>
            </div>
            <div class="status-card">
                <div class="status-value" id="total-stations">-</div>
                <div class="status-label">Total Stations</div>
            </div>
        </div>
        
        <div class="coordinate-display" id="coordinate-display" style="display: none;">
            <h3>📍 Live Position Tracking</h3>
            <div class="coordinate-grid">
                <div class="coordinate-item">
                    <div class="coordinate-value" id="coord-x">-</div>
                    <div>X Position</div>
                </div>
                <div class="coordinate-item">
                    <div class="coordinate-value" id="coord-y">-</div>
                    <div>Y Position</div>
                </div>
                <div class="coordinate-item">
                    <div class="coordinate-value" id="coord-z">-</div>
                    <div>Z Position</div>
                </div>
                <div class="coordinate-item">
                    <div class="coordinate-value" id="coord-time">-</div>
                    <div>Last Update</div>
                </div>
            </div>
        </div>
        
        <div class="signal-strength" id="signal-display" style="display: none;">
            <h3>📡 Signal Strength</h3>
            <div class="signal-bar">
                <div class="signal-fill" id="signal-fill" style="width: 0%"></div>
            </div>
            <div id="signal-text">No signal</div>
        </div>
        
        <div class="player-section">
            <h3>🎵 Radio Player</h3>
            <div class="now-playing" id="now-playing">Select a station or drive to a city for automatic switching</div>
            <audio id="audio-player" class="audio-player" controls preload="none">
                Your browser does not support the audio element.
            </audio>
            <div class="controls">
                <button class="btn btn-warning" onclick="playRandomStation()">🎲 Random Station</button>
                <button class="btn btn-primary" onclick="stopRadio()">⏹️ Stop</button>
                <button class="btn btn-success" onclick="refreshStatus()">🔄 Refresh</button>
                <button class="btn btn-success" onclick="reloadStations()">📡 Reload Stations</button>
                <button class="btn btn-primary" id="auto-switch-btn" onclick="toggleAutoSwitch()">🔄 Auto-Switch: ON</button>
            </div>
        </div>
        
        <div id="messages"></div>
        
        <div class="stations-section">
            <h3>📻 Available Stations</h3>
            <div id="stations-grid" class="stations-grid">
                <div>Loading stations...</div>
            </div>
        </div>
    </div>

    <script>
        let currentCountry = null;
        let currentStationCard = null;
        let statusData = null;
        let updateInterval = null;
        let hlsInstance = null;
        let lastSuggestedStation = null;
        let autoSwitchEnabled = true; // Can be toggled by user
        
        const audioPlayer = document.getElementById('audio-player');
        const messagesDiv = document.getElementById('messages');
        
        // Audio player event listeners
        audioPlayer.addEventListener('loadstart', () => {
            console.log('Loading stream...');
            showMessage('Loading radio stream...', 'success');
        });
        
        audioPlayer.addEventListener('canplay', () => {
            console.log('Stream ready');
            hideMessages();
        });
        
        audioPlayer.addEventListener('playing', () => {
            console.log('Stream playing');
            hideMessages();
        });
        
        audioPlayer.addEventListener('error', (e) => {
            console.error('Audio error:', e);
            showMessage('Failed to load radio stream. The station may be offline.', 'error');
        });
        
        audioPlayer.addEventListener('ended', () => {
            console.log('Stream ended');
            showMessage('Radio stream ended', 'error');
        });
        
        function updateStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    statusData = data;
                    
                    // Update status panel
                    document.getElementById('tracking-mode').textContent = 
                        data.plugin_connected ? '🎯 Plugin' : '📄 Manual';
                    document.getElementById('current-country').textContent = 
                        data.country ? data.country.charAt(0).toUpperCase() + data.country.slice(1) : 'None';
                    document.getElementById('current-city').textContent = 
                        data.city ? data.city.name : 'None';
                    document.getElementById('total-stations').textContent = data.total_stations;
                    
                    // Update coordinates if available
                    if (data.coordinates && data.plugin_connected) {
                        document.getElementById('coordinate-display').style.display = 'block';
                        document.getElementById('coord-x').textContent = data.coordinates.x.toFixed(1);
                        document.getElementById('coord-y').textContent = data.coordinates.y.toFixed(1);
                        document.getElementById('coord-z').textContent = data.coordinates.z.toFixed(1);
                        document.getElementById('coord-time').textContent = new Date().toLocaleTimeString();
                    } else {
                        document.getElementById('coordinate-display').style.display = 'none';
                    }
                    
                    // Update signal strength
                    if (data.city && data.city.signal_strength !== undefined) {
                        document.getElementById('signal-display').style.display = 'block';
                        const strength = data.city.signal_strength;
                        document.getElementById('signal-fill').style.width = (strength * 100) + '%';
                        document.getElementById('signal-text').textContent = 
                            `${(strength * 100).toFixed(0)}% - ${data.city.name}, ${data.city.country}`;
                    } else {
                        document.getElementById('signal-display').style.display = 'none';
                    }
                    
                    // Handle auto-switching if enabled
                    if (autoSwitchEnabled && data.suggested_station && 
                        data.suggested_station !== lastSuggestedStation) {
                        
                        lastSuggestedStation = data.suggested_station;
                        
                        // Only auto-switch if we should (not playing a station from same country)
                        let shouldAutoSwitch = false;
                        
                        if (!data.playing_station) {
                            // No station playing
                            shouldAutoSwitch = true;
                        } else if (data.playing_station.country && data.suggested_station.country) {
                            // Check if playing station is from different country
                            const playingCountry = data.playing_station.country.toLowerCase();
                            const suggestedCountry = data.suggested_station.country.toLowerCase();
                            shouldAutoSwitch = playingCountry !== suggestedCountry;
                        }
                        
                        if (shouldAutoSwitch) {
                            // Find the station card and auto-play it
                            const cards = document.querySelectorAll('.station-card');
                            for (let card of cards) {
                                const name = card.querySelector('.station-name').textContent;
                                if (name === data.suggested_station.name) {
                                    showMessage(`🎵 Auto-switching to ${data.suggested_station.name}`, 'success');
                                    playStation(data.suggested_station, card);
                                    break;
                                }
                            }
                        }
                    }
                    
                    // Update stations if country changed
                    if (data.country !== currentCountry) {
                        currentCountry = data.country;
                        displayStations(data.stations);
                        
                        // Show country change message
                        if (data.country) {
                            const countryName = data.country.charAt(0).toUpperCase() + data.country.slice(1);
                            showMessage(`🌍 Entered ${countryName} - ${data.stations.length} stations available`, 'success');
                        }
                    }
                })
                .catch(error => {
                    console.error('Status update error:', error);
                    document.getElementById('tracking-mode').textContent = 'Error';
                    showMessage('Connection error. Please check if the server is running.', 'error');
                });
        }
        
        function displayStations(stations) {
            const container = document.getElementById('stations-grid');
            
            if (!stations || stations.length === 0) {
                container.innerHTML = '<div style="text-align: center; padding: 20px;">No stations available for this country.<br>Drive to a different country or reload stations.</div>';
                return;
            }
            
            container.innerHTML = '';
            stations.forEach(station => {
                const card = document.createElement('div');
                card.className = 'station-card';
                card.onclick = () => playStation(station, card);
                
                const logoHtml = station.logo ? 
                    `<img src="${station.logo}" alt="${station.name}" onerror="this.style.display='none'; this.parentElement.innerHTML='📻';">` :
                    '📻';
                
                card.innerHTML = `
                    <div class="station-logo">${logoHtml}</div>
                    <div class="station-name">${station.name}</div>
                    <div class="station-location">${station.city ? station.city + ', ' : ''}${station.country}</div>
                `;
                
                container.appendChild(card);
            });
        }
        
        function playStation(station, cardElement) {
            // Update UI
            if (currentStationCard) {
                currentStationCard.classList.remove('playing');
            }
            currentStationCard = cardElement;
            cardElement.classList.add('playing');
            
            // Update now playing
            document.getElementById('now-playing').textContent = `Loading ${station.name}...`;
            
            // Clean up previous HLS instance
            if (hlsInstance) {
                hlsInstance.destroy();
                hlsInstance = null;
            }
            
            const streamUrl = station.stream_url;
            
            // Check if it's an M3U8 stream
            if (streamUrl.includes('.m3u8') || streamUrl.includes('m3u8')) {
                // Handle HLS stream
                if (Hls.isSupported()) {
                    hlsInstance = new Hls({
                        enableWorker: false,
                        lowLatencyMode: true,
                        backBufferLength: 90
                    });
                    
                    hlsInstance.loadSource(streamUrl);
                    hlsInstance.attachMedia(audioPlayer);
                    
                    hlsInstance.on(Hls.Events.MANIFEST_PARSED, function() {
                        console.log('HLS manifest parsed, starting playback');
                        audioPlayer.play().then(() => {
                            document.getElementById('now-playing').textContent = 
                                `🎵 ${station.name} - ${station.city ? station.city + ', ' : ''}${station.country}`;
                            hideMessages();
                            
                            // Notify backend that this station is now playing
                            notifyStationPlaying(station);
                        }).catch(error => {
                            console.error('HLS play error:', error);
                            handlePlayError(error, station);
                        });
                    });
                    
                    hlsInstance.on(Hls.Events.ERROR, function(event, data) {
                        console.error('HLS error:', data);
                        if (data.fatal) {
                            switch(data.type) {
                                case Hls.ErrorTypes.NETWORK_ERROR:
                                    showMessage('Network error loading stream. Please try again.', 'error');
                                    break;
                                case Hls.ErrorTypes.MEDIA_ERROR:
                                    showMessage('Media error. This stream format may not be supported.', 'error');
                                    break;
                                default:
                                    showMessage('Failed to load HLS stream. The station may be offline.', 'error');
                                    break;
                            }
                            document.getElementById('now-playing').textContent = 'Error loading station';
                        }
                    });
                    
                } else if (audioPlayer.canPlayType('application/vnd.apple.mpegurl')) {
                    // Safari native HLS support
                    audioPlayer.src = streamUrl;
                    audioPlayer.load();
                    audioPlayer.play().then(() => {
                        document.getElementById('now-playing').textContent = 
                            `🎵 ${station.name} - ${station.city ? station.city + ', ' : ''}${station.country}`;
                        hideMessages();
                        
                        // Notify backend that this station is now playing
                        notifyStationPlaying(station);
                    }).catch(error => {
                        console.error('Safari HLS play error:', error);
                        handlePlayError(error, station);
                    });
                } else {
                    showMessage('HLS streams are not supported in this browser. Please use Chrome, Firefox, or Safari.', 'error');
                    document.getElementById('now-playing').textContent = 'Stream not supported';
                }
            } else {
                // Handle regular audio streams (MP3, AAC, etc.)
                audioPlayer.src = streamUrl;
                audioPlayer.load();
                
                audioPlayer.play().then(() => {
                    document.getElementById('now-playing').textContent = 
                        `🎵 ${station.name} - ${station.city ? station.city + ', ' : ''}${station.country}`;
                    hideMessages();
                    
                    // Notify backend that this station is now playing
                    notifyStationPlaying(station);
                }).catch(error => {
                    console.error('Play error:', error);
                    handlePlayError(error, station);
                });
            }
        }
        
        function handlePlayError(error, station) {
            if (error.name === 'NotAllowedError') {
                showMessage('Click play on the audio player to start listening (browser security policy).', 'error');
                document.getElementById('now-playing').textContent = `Ready: ${station.name}`;
            } else {
                showMessage('Failed to play station. Please try another station.', 'error');
                document.getElementById('now-playing').textContent = 'Error playing station';
            }
        }
        
        function playRandomStation() {
            fetch('/api/random_station')
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        const station = data.station;
                        
                        // Find the corresponding card
                        const cards = document.querySelectorAll('.station-card');
                        for (let card of cards) {
                            const name = card.querySelector('.station-name').textContent;
                            if (name === station.name) {
                                playStation(station, card);
                                break;
                            }
                        }
                    } else {
                        showMessage(data.message, 'error');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showMessage('Failed to get random station', 'error');
                });
        }
        
        function notifyStationPlaying(station) {
            fetch('/api/set_playing_station', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ station: station })
            }).catch(error => {
                console.error('Error notifying station playing:', error);
            });
        }
        
        function notifyStationStopped() {
            fetch('/api/stop_playing', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            }).catch(error => {
                console.error('Error notifying station stopped:', error);
            });
        }
        
        function stopRadio() {
            if (hlsInstance) {
                hlsInstance.destroy();
                hlsInstance = null;
            }
            
            audioPlayer.pause();
            audioPlayer.src = '';
            document.getElementById('now-playing').textContent = 
                'Select a station or drive to a city for automatic switching';
            
            if (currentStationCard) {
                currentStationCard.classList.remove('playing');
                currentStationCard = null;
            }
            
            // Notify backend that playback stopped
            notifyStationStopped();
            
            hideMessages();
            console.log('Radio stopped');
        }
        
        function refreshStatus() {
            updateStatus();
            showMessage('Status refreshed', 'success');
        }
        
        function reloadStations() {
            showMessage('Reloading stations from remote source...', 'success');
            
            fetch('/api/reload_stations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    showMessage(data.message, 'success');
                    updateStatus();
                } else {
                    showMessage(data.message, 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showMessage('Failed to reload stations', 'error');
            });
        }
        
        function toggleAutoSwitch() {
            autoSwitchEnabled = !autoSwitchEnabled;
            const btn = document.getElementById('auto-switch-btn');
            btn.textContent = autoSwitchEnabled ? '🔄 Auto-Switch: ON' : '🔄 Auto-Switch: OFF';
            btn.className = autoSwitchEnabled ? 'btn btn-success' : 'btn btn-warning';
            
            const message = autoSwitchEnabled ? 'Auto-switching enabled' : 'Auto-switching disabled';
            showMessage(message, 'success');
        }
        
        function showMessage(text, type = 'success') {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}`;
            messageDiv.textContent = text;
            
            messagesDiv.innerHTML = '';
            messagesDiv.appendChild(messageDiv);
            
            // Auto-hide after 5 seconds
            setTimeout(() => {
                if (messagesDiv.contains(messageDiv)) {
                    messagesDiv.removeChild(messageDiv);
                }
            }, 5000);
        }
        
        function hideMessages() {
            messagesDiv.innerHTML = '';
        }
        
        // Initialize the application
        function initApp() {
            // Start status updates
            updateStatus();
            updateInterval = setInterval(updateStatus, 2000); // Update every 2 seconds
            
            // Show welcome message
            setTimeout(() => {
                showMessage('🎉 ETS2 Local Radio is running! Drive around to experience automatic station switching.', 'success');
            }, 1000);
        }
        
        // Handle page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'visible') {
                if (!updateInterval) {
                    updateInterval = setInterval(updateStatus, 2000);
                }
            } else {
                if (updateInterval) {
                    clearInterval(updateInterval);
                    updateInterval = null;
                }
            }
        });
        
        // Handle page unload
        window.addEventListener('beforeunload', () => {
            if (updateInterval) {
                clearInterval(updateInterval);
            }
        });
        
        // Start the application
        initApp();
    </script>
</body>
</html>
"""