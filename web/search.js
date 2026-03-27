// ===== GLOBAL SEARCH (Ctrl+K) =====
(function() {
    const overlay = document.getElementById('search-overlay');
    const input = document.getElementById('search-input');
    const results = document.getElementById('search-results');
    let selectedIdx = -1;

    function openSearch() {
        overlay.classList.add('open');
        input.value = '';
        input.focus();
        results.innerHTML = '<div class="search-empty">Digite para buscar...</div>';
        selectedIdx = -1;
    }
    function closeSearch() { overlay.classList.remove('open'); }

    function highlightText(text, query) {
        if (!query) return text;
        const safe = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        const re = new RegExp('(' + safe + ')', 'gi');
        return text.replace(re, '<mark>$1</mark>');
    }
    function escS(s) { if (!s) return ''; return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

    function searchAll(query) {
        if (!query || query.length < 2) {
            results.innerHTML = '<div class="search-empty">Digite pelo menos 2 caracteres...</div>';
            return;
        }
        const q = query.toLowerCase();
        const items = [];

        if (window.__tl_data) {
            const D = window.__tl_data;
            const t = D.tree || {};

            // People
            if (t.nome_completo && t.nome_completo.toLowerCase().includes(q))
                items.push({icon:'👤',title:t.nome_completo,sub:t.profissao||'',section:'pessoa',id:'person'});
            if (t.conjuge && t.conjuge.nome_completo && t.conjuge.nome_completo.toLowerCase().includes(q))
                items.push({icon:'👩',title:t.conjuge.nome_completo,sub:'Cônjuge',section:'família',id:'family'});
            (D.paisTios||[]).forEach(function(s) {
                if (s.nome_completo && s.nome_completo.toLowerCase().includes(q))
                    items.push({icon:'👨',title:s.nome_completo,sub:'Geração 3',section:'família',id:'family'});
            });
            (D.primos||[]).forEach(function(s) {
                if (s.nome_completo && s.nome_completo.toLowerCase().includes(q))
                    items.push({icon:'👧',title:s.nome_completo,sub:'Geração 4',section:'família',id:'family'});
            });

            // Companies
            (D.companies||[]).forEach(function(c) {
                var name = c.nome_fantasia || c.razao_social || '';
                if (name.toLowerCase().includes(q) || (c.cnpj||'').includes(q))
                    items.push({icon:'🏢',title:name,sub:c.cnpj||'',section:'empresas',id:'companies'});
            });

            // Properties
            (D.properties||[]).forEach(function(p) {
                var addr = p.address || p.building_name || '';
                if (addr.toLowerCase().includes(q))
                    items.push({icon:'🏠',title:p.building_name||addr,sub:p.city||'',section:'imóveis',id:'properties'});
            });

            // Legal
            (D.legal||[]).forEach(function(p) {
                var txt = (p.process_number||'')+(p.subject||'')+(p.parties||'');
                if (txt.toLowerCase().includes(q))
                    items.push({icon:'⚖️',title:p.process_number||p.subject||'Processo',sub:p.parties||'',section:'processos',id:'legal'});
            });

            // Contacts
            (D.contacts||[]).forEach(function(c) {
                var txt = (c.nome||'')+(c.email||'')+(c.empresa||'');
                if (txt.toLowerCase().includes(q))
                    items.push({icon:'📞',title:c.nome||'',sub:c.role||c.empresa||'',section:'contatos',id:'contacts'});
            });

            // Timeline
            (D.timeline||[]).forEach(function(e) {
                var txt = (e.description||'')+(e.person_name||'');
                if (txt.toLowerCase().includes(q))
                    items.push({icon:'📅',title:e.person_name||'Evento',sub:(e.description||'').substring(0,60),section:'timeline',id:'timeline'});
            });
        }

        if (items.length === 0) {
            results.innerHTML = '<div class="search-empty">Nenhum resultado para "' + escS(query) + '"</div>';
            return;
        }

        results.innerHTML = items.map(function(item, i) {
            return '<div class="search-result" data-idx="'+i+'" data-target="'+item.id+'">' +
                '<div class="search-result-icon">'+item.icon+'</div>' +
                '<div class="search-result-text">' +
                    '<div class="search-result-title">'+highlightText(escS(item.title), query)+'</div>' +
                    (item.sub ? '<div class="search-result-sub">'+highlightText(escS(item.sub), query)+'</div>' : '') +
                '</div>' +
                '<span class="search-result-section">'+item.section+'</span>' +
            '</div>';
        }).join('');

        results.querySelectorAll('.search-result').forEach(function(el) {
            el.addEventListener('click', function() {
                closeSearch();
                var target = document.getElementById(el.dataset.target);
                if (target) target.scrollIntoView({behavior:'smooth'});
            });
        });
        selectedIdx = -1;
    }

    function selectResult(idx) {
        var els = results.querySelectorAll('.search-result');
        els.forEach(function(el) { el.classList.remove('selected'); });
        if (idx >= 0 && idx < els.length) {
            els[idx].classList.add('selected');
            els[idx].scrollIntoView({block:'nearest'});
        }
        selectedIdx = idx;
    }

    document.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            if (overlay.classList.contains('open')) closeSearch(); else openSearch();
            return;
        }
        if (!overlay.classList.contains('open')) return;
        if (e.key === 'Escape') { closeSearch(); return; }
        if (e.key === 'ArrowDown') { e.preventDefault(); selectResult(Math.min(selectedIdx+1, results.querySelectorAll('.search-result').length-1)); return; }
        if (e.key === 'ArrowUp') { e.preventDefault(); selectResult(Math.max(selectedIdx-1, 0)); return; }
        if (e.key === 'Enter' && selectedIdx >= 0) {
            var el = results.querySelector('.search-result.selected');
            if (el) el.click();
            return;
        }
    });

    input.addEventListener('input', function() { searchAll(this.value); });
    overlay.addEventListener('click', function(e) { if (e.target === overlay) closeSearch(); });
})();
