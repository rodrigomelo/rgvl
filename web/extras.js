// ===== BACK TO TOP BUTTON =====
(function() {
    var btn = document.createElement('button');
    btn.id = 'back-to-top';
    btn.innerHTML = '⬆';
    btn.title = 'Voltar ao topo';
    btn.style.cssText = 'position:fixed;bottom:24px;right:24px;width:44px;height:44px;border-radius:50%;border:none;background:var(--primary);color:white;font-size:20px;cursor:pointer;box-shadow:0 4px 12px rgba(0,0,0,0.2);z-index:90;opacity:0;transition:opacity 0.3s;pointer-events:none;';
    document.body.appendChild(btn);

    window.addEventListener('scroll', function() {
        if (window.scrollY > 400) {
            btn.style.opacity = '1';
            btn.style.pointerEvents = 'auto';
        } else {
            btn.style.opacity = '0';
            btn.style.pointerEvents = 'none';
        }
    });

    btn.addEventListener('click', function() {
        window.scrollTo({top: 0, behavior: 'smooth'});
    });
})();

// ===== CLICKABLE TREE NODES =====
// Opens a detail drawer when clicking a person node in the family tree
(function() {
    document.addEventListener('click', function(e) {
        var node = e.target.closest('.node');
        if (!node) return;
        // Only handle clicks inside the family tree section
        var familySection = document.getElementById('family');
        if (!familySection || !familySection.contains(node)) return;

        var nameEl = node.querySelector('.node-name');
        if (!nameEl) return;
        var name = nameEl.textContent.replace(/^[^\wÀ-ÿ]+/, '').trim(); // Remove leading emoji
        if (!name) return;

        // Gather detail lines
        var details = [];
        node.querySelectorAll('.node-detail').forEach(function(d) {
            var txt = d.textContent.trim();
            if (txt) details.push(txt);
        });

        showPersonDrawer(name, details);
    });

    function showPersonDrawer(name, details) {
        // Remove existing drawer
        var existing = document.querySelector('.person-drawer-overlay');
        if (existing) existing.remove();

        var overlay = document.createElement('div');
        overlay.className = 'person-drawer-overlay';
        overlay.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.4);z-index:200;display:flex;justify-content:flex-end;';

        var drawer = document.createElement('div');
        drawer.style.cssText = 'width:380px;max-width:95vw;background:white;height:100%;overflow-y:auto;padding:24px;box-shadow:-4px 0 20px rgba(0,0,0,0.15);';

        var html = '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;padding-bottom:12px;border-bottom:2px solid var(--accent)">';
        html += '<span style="font-size:16px;font-weight:600;color:var(--primary)">' + name + '</span>';
        html += '<button onclick="this.closest(\'.person-drawer-overlay\').remove()" style="background:none;border:none;font-size:22px;cursor:pointer;color:var(--text-muted);padding:0;line-height:1">×</button>';
        html += '</div>';

        if (details.length > 0) {
            html += '<div style="display:flex;flex-direction:column;gap:8px">';
            details.forEach(function(d) {
                html += '<div style="display:flex;justify-content:space-between;padding:8px 12px;background:var(--bg);border-radius:6px;font-size:13px">';
                html += '<span style="color:var(--text)">' + d + '</span>';
                html += '</div>';
            });
            html += '</div>';
        } else {
            html += '<div style="text-align:center;color:var(--text-muted);padding:40px;font-size:13px">Sem detalhes disponíveis</div>';
        }

        // Find matching timeline events
        if (window.__tl_data && window.__tl_data.timeline) {
            var events = window.__tl_data.timeline.filter(function(e) {
                return e.person_name && e.person_name.toLowerCase().includes(name.toLowerCase().split(' ')[0].toLowerCase());
            });
            if (events.length > 0) {
                html += '<div style="margin-top:20px;padding-top:16px;border-top:1px solid var(--border)">';
                html += '<div style="font-size:13px;font-weight:600;color:var(--primary);margin-bottom:12px">📅 Eventos (' + events.length + ')</div>';
                events.slice(0, 10).forEach(function(e) {
                    var date = e.event_date || '?';
                    var desc = (e.description || '').substring(0, 80);
                    html += '<div style="padding:8px 12px;background:var(--bg);border-radius:6px;margin-bottom:6px;font-size:12px">';
                    html += '<div style="color:var(--text-muted)">' + date + '</div>';
                    html += '<div style="color:var(--text)">' + desc + '</div>';
                    html += '</div>';
                });
                html += '</div>';
            }
        }

        drawer.innerHTML = html;
        overlay.appendChild(drawer);
        overlay.addEventListener('click', function(e) { if (e.target === overlay) overlay.remove(); });
        document.body.appendChild(overlay);

        // ESC to close
        var escHandler = function(e) { if (e.key === 'Escape') { overlay.remove(); document.removeEventListener('keydown', escHandler); } };
        document.addEventListener('keydown', escHandler);
    }
})();
