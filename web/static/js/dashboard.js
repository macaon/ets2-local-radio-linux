/**
 * ETS2 Truck Companion - Dashboard Gauges & Updates
 */

const ETS2Dashboard = (function() {
    'use strict';

    function update(data) {
        if (!data) return;
        updateGauges(data.truck || {});
        updateJob(data.job || {});
        updateDamage(data.damage || {});
    }

    function updateGauges(truck) {
        if (!truck.speed && truck.speed !== 0) return;

        // Speed gauge (max ~150 km/h for display)
        const speed = Math.round(truck.speed || 0);
        const speedLimit = Math.round(truck.speedLimit || 0);
        const speedPct = Math.min(speed / 150, 1);
        const speedGauge = document.getElementById('speed-gauge');
        const speeding = speedLimit > 0 && speed > speedLimit;

        document.getElementById('speed-value').textContent = speed;
        speedGauge.style.setProperty('--gauge-angle', (speedPct * 360) + 'deg');
        speedGauge.className = speeding ? 'gauge-ring speed-warning' : 'gauge-ring';
        document.getElementById('speed-limit-text').textContent =
            speedLimit > 0 ? 'Limit: ' + speedLimit + ' km/h' : 'Limit: --';

        // RPM gauge (max ~2500 for trucks)
        const rpm = Math.round(truck.engineRpm || 0);
        const rpmPct = Math.min(rpm / 2500, 1);
        document.getElementById('rpm-value').textContent = rpm;
        document.getElementById('rpm-gauge').style.setProperty('--gauge-angle', (rpmPct * 360) + 'deg');

        // Gear display
        const gear = truck.gearDashboard || truck.gear || 0;
        let gearText;
        if (gear === 0) gearText = 'N';
        else if (gear < 0) gearText = 'R' + Math.abs(gear);
        else gearText = String(gear);
        document.getElementById('gear-display').textContent = gearText;
        document.getElementById('gear-text').textContent = 'Gear: ' + gearText;

        // Fuel gauge
        const fuel = truck.fuel || 0;
        const cap = truck.fuelCapacity || 1;
        const fuelPct = Math.min(fuel / cap, 1);
        const fuelGauge = document.getElementById('fuel-gauge');
        document.getElementById('fuel-value').textContent = Math.round(fuelPct * 100);
        fuelGauge.style.setProperty('--gauge-angle', (fuelPct * 360) + 'deg');
        fuelGauge.className = fuelPct < 0.15 ? 'gauge-ring fuel-warning' : 'gauge-ring';
        document.getElementById('fuel-detail').textContent =
            Math.round(fuel) + ' / ' + Math.round(cap) + ' L';

        // Odometer
        const odo = truck.odometer || 0;
        document.getElementById('odometer-text').textContent =
            'Odometer: ' + Math.round(odo).toLocaleString() + ' km';
    }

    function updateJob(job) {
        const content = document.getElementById('job-content');
        if (!job.active) {
            content.innerHTML = '<div class="no-job-message">No active job - pick one up at a company!</div>';
            return;
        }

        const distLeft = job.routeDistance ? Math.round(job.routeDistance / 1000) : '--';
        const timeLeft = job.routeTime ? formatTime(job.routeTime) : '--';

        content.innerHTML =
            '<div class="job-route">' +
                '<span>' + escapeHtml(job.citySrc || '?') + '</span>' +
                '<span class="arrow">&#10230;</span>' +
                '<span>' + escapeHtml(job.cityDst || '?') + '</span>' +
            '</div>' +
            '<div class="job-details">' +
                '<span class="job-detail-label">Cargo</span>' +
                '<span class="job-detail-value">' + escapeHtml(job.cargo || 'Unknown') + '</span>' +
                '<span class="job-detail-label">Distance Left</span>' +
                '<span class="job-detail-value">' + distLeft + ' km</span>' +
                '<span class="job-detail-label">Time Left</span>' +
                '<span class="job-detail-value">' + timeLeft + '</span>' +
                '<span class="job-detail-label">Income</span>' +
                '<span class="job-detail-value">' + (job.income || 0).toLocaleString() + '</span>' +
                '<span class="job-detail-label">From</span>' +
                '<span class="job-detail-value">' + escapeHtml(job.compSrc || '-') + '</span>' +
                '<span class="job-detail-label">To</span>' +
                '<span class="job-detail-value">' + escapeHtml(job.compDst || '-') + '</span>' +
            '</div>';
    }

    function updateDamage(damage) {
        const components = ['engine', 'transmission', 'cabin', 'chassis', 'wheels', 'cargo'];
        components.forEach(c => {
            const wear = damage[c] || 0;
            const health = Math.max(0, Math.round((1 - wear) * 100));
            const bar = document.getElementById('dmg-' + c);
            const pct = document.getElementById('dmg-' + c + '-pct');
            if (bar) {
                bar.style.width = health + '%';
                bar.className = 'damage-bar-fill' +
                    (health < 30 ? ' danger' : health < 60 ? ' warn' : '');
            }
            if (pct) pct.textContent = health + '%';
        });
    }

    function formatTime(seconds) {
        const h = Math.floor(seconds / 3600);
        const m = Math.floor((seconds % 3600) / 60);
        if (h > 0) return h + 'h ' + m + 'm';
        return m + 'm';
    }

    function escapeHtml(s) {
        const d = document.createElement('div');
        d.textContent = s || '';
        return d.innerHTML;
    }

    return { update };
})();
