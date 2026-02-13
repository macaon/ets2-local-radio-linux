/**
 * ETS2 Truck Companion - Travel Log UI
 */

const ETS2TravelLog = (function() {
    'use strict';

    function refresh() {
        loadStats();
        loadRecentVisits();
        loadJobHistory();
    }

    function loadStats() {
        fetch('/api/travel/stats')
            .then(r => r.json())
            .then(data => {
                setText('stat-distance', Math.round(data.total_distance || 0).toLocaleString());
                setText('stat-cities', data.cities_visited || 0);
                setText('stat-jobs', data.jobs_completed || 0);
                setText('stat-income', (data.total_income || 0).toLocaleString());
                setText('stat-fines', (data.total_fines || 0).toLocaleString());
            })
            .catch(() => {});
    }

    function loadRecentVisits() {
        fetch('/api/travel/recent')
            .then(r => r.json())
            .then(visits => {
                const list = document.getElementById('visit-list');
                if (!visits || visits.length === 0) {
                    list.innerHTML = '<div class="no-job-message">No visits recorded yet</div>';
                    return;
                }
                list.innerHTML = visits.map(v =>
                    '<div class="visit-item">' +
                        '<div><span class="visit-city">' + escapeHtml(v.city) + '</span> ' +
                        '<span class="visit-country">' + escapeHtml(v.country) + '</span></div>' +
                        '<span class="visit-time">' + formatTimestamp(v.timestamp) + '</span>' +
                    '</div>'
                ).join('');
            })
            .catch(() => {});
    }

    function loadJobHistory() {
        fetch('/api/travel/jobs')
            .then(r => r.json())
            .then(jobs => {
                const list = document.getElementById('job-list');
                if (!jobs || jobs.length === 0) {
                    list.innerHTML = '<div class="no-job-message">No completed jobs yet</div>';
                    return;
                }
                list.innerHTML = jobs.map(j =>
                    '<div class="job-item">' +
                        '<div>' +
                            '<div><strong>' + escapeHtml(j.cargo || 'Unknown') + '</strong></div>' +
                            '<div style="font-size:0.85em;opacity:0.7;">' +
                                escapeHtml(j.source_city || '?') + ' &#10230; ' +
                                escapeHtml(j.dest_city || '?') +
                            '</div>' +
                        '</div>' +
                        '<div style="text-align:right;">' +
                            '<div style="color:#4CAF50;font-weight:bold;">' +
                                (j.income || 0).toLocaleString() +
                            '</div>' +
                            '<div style="font-size:0.8em;opacity:0.5;">' +
                                (j.distance_km || 0) + ' km' +
                            '</div>' +
                        '</div>' +
                    '</div>'
                ).join('');
            })
            .catch(() => {});
    }

    function formatTimestamp(ts) {
        if (!ts) return '';
        const d = new Date(ts * 1000);
        return d.toLocaleString(undefined, {
            month: 'short', day: 'numeric',
            hour: '2-digit', minute: '2-digit'
        });
    }

    function setText(id, val) {
        const el = document.getElementById(id);
        if (el) el.textContent = val;
    }

    function escapeHtml(s) {
        const d = document.createElement('div');
        d.textContent = s || '';
        return d.innerHTML;
    }

    return { refresh };
})();
