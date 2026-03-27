// ===== TIMELINE GROUP BY YEAR =====
// Wraps timeline events in collapsible year groups
(function() {
    var origRender = window.__renderTimelineFiltered;
    if (!origRender) return;

    window.__renderTimelineFiltered = function(events) {
        var _scrollY = window.scrollY;
        if (window.__scrollObserver) window.__scrollObserver.disconnect();
        var tl = document.getElementById('timeline-container');
        if (!tl) return;
        var filters = window.__tl_filters || { types: new Set(), sources: new Set() };
        var types = filters.types, sources = filters.sources;
        var active = types.size > 0 || sources.size > 0;
        var filtered = active ? events.filter(function(e) {
            if (types.size > 0 && !types.has(e.event_type || 'default')) return false;
            if (sources.size > 0) {
                var raw = e.source_type || e.source || '';
                var s = raw.startsWith('intel') ? 'INTEL' : (raw && raw !== 'timeline.md' ? raw.replace('.md','').toUpperCase() : 'OUTRO');
                if (!sources.has(s)) return false;
            }
            return true;
        }) : events;

        if (filtered.length === 0) {
            tl.innerHTML = '<div class="timeline-empty-filtered">Nenhum evento para os filtros selecionados</div>';
            return;
        }

        var typeClasses = {'birth':'birth','death':'death','marriage':'marriage','company':'company','legal':'legal','research':'research','family_contact':'family_contact','paternity':'paternity','name_change':'name_change','career':'career','default':'default'};
        var TL_EMOJI = {'birth':'\uD83D\uDC76','death':'\u26B0\uFE0F','marriage':'\uD83D\uDC8D','company':'\uD83C\uDFE2','name_change':'\u270F\uFE0F','paternity':'\uD83E\uDD1D','career':'\uD83D\uDCBC','legal':'\u2696\uFE0F','family_contact':'\uD83D\uDCDE','default':'\uD83D\uDCCB'};
        var TL_LABELS = {'birth':'NASCIMENTO','death':'FALECIMENTO','marriage':'CASAMENTO','company':'EMPRESA','career':'CARREIRA','name_change':'NOME','paternity':'PATERNIDADE','legal':'LEGAL','family_contact':'CONTATO','default':'OUTRO'};

        // Group by year
        var yearGroups = {};
        var yearOrder = [];
        filtered.forEach(function(e) {
            var yr = '?';
            if (e.event_date) {
                var raw = String(e.event_date);
                var d = raw.startsWith('~') ? raw.substring(1) : raw;
                var parts = d.split('-');
                if (parts[0] && parts[0].length === 4) yr = parts[0];
            }
            if (!yearGroups[yr]) { yearGroups[yr] = []; yearOrder.push(yr); }
            yearGroups[yr].push(e);
        });

        // Sort years descending
        yearOrder.sort(function(a, b) { return (b === '?' ? 9999 : parseInt(b)) - (a === '?' ? 9999 : parseInt(a)); });

        var html = '';
        yearOrder.forEach(function(yr) {
            var evts = yearGroups[yr];
            html += '<div class="tl-year-group">';
            html += '<div class="tl-year-header" onclick="this.parentElement.classList.toggle(\'collapsed\')">';
            html += '<span class="tl-year-toggle">▼</span> ';
            html += '<span class="tl-year-label">' + yr + '</span>';
            html += ' <span class="tl-year-count">(' + evts.length + ')</span>';
            html += '</div>';
            html += '<div class="tl-year-events">';

            evts.forEach(function(e) {
                var dateDisplay = '-';
                if (e.event_date) {
                    var raw = String(e.event_date);
                    dateDisplay = raw.startsWith('~') ? fmtDate(raw.substring(1)) + ' <span style="color:var(--text-muted);font-size:11px">(aprox.)</span>' : fmtDate(raw);
                }
                var typeKey = e.event_type || 'default', cssClass = typeClasses[typeKey] || 'default';
                var tlEmoji = TL_EMOJI[typeKey] || '';
                var tlLabel = TL_LABELS[typeKey] || typeKey;
                var sourceBadge = '';
                var rawFonte = e.source_type || e.source || '';
                var fonteKey = rawFonte.startsWith('intel') ? 'INTEL' : (rawFonte && rawFonte !== 'timeline.md' ? rawFonte.replace('.md','').toUpperCase() : 'OUTRO');
                if (fonteKey && fonteKey !== 'EVENTOS') sourceBadge = ' ' + sourceBadgeHTML(fonteKey, 'sm');
                html += '<div class="timeline-event"><div class="timeline-date">' + dateDisplay + '</div><div class="timeline-person">' + esc(e.person_name||'Unknown') + '</div><span class="timeline-type ' + cssClass + '">' + tlEmoji + ' ' + esc(tlLabel) + '</span>' + sourceBadge + '<div class="timeline-desc">' + esc(e.description||'') + '</div></div>';
            });

            html += '</div></div>';
        });

        tl.innerHTML = html;
        if (window.__updateActiveFilterBar) window.__updateActiveFilterBar();
        requestAnimationFrame(function() {
            window.scrollTo(0, _scrollY);
            if (window.__scrollObserver) {
                document.querySelectorAll('.section[id]').forEach(function(s) { window.__scrollObserver.observe(s); });
            }
        });
    };
})();
