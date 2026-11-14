/* Turf Club ERP Academy - presenter mode, copy buttons, code highlighting, Mermaid diagrams, table of contents. */
(function () {
  'use strict';

  // ---------- presenter mode (remembered per browser) ----------
  var KEY = 'tc-academy-presenter';
  var toggle = document.getElementById('presenterToggle');
  function setPresenter(on) {
    document.body.classList.toggle('presenter', on);
    if (toggle) {
      toggle.setAttribute('aria-pressed', on ? 'true' : 'false');
      toggle.querySelector('span').textContent = on ? 'Presenter mode on' : 'Presenter mode';
    }
    try { localStorage.setItem(KEY, on ? '1' : '0'); } catch (e) { /* storage blocked: ignore */ }
  }
  var stored = false;
  try { stored = localStorage.getItem(KEY) === '1'; } catch (e) { stored = false; }
  setPresenter(stored);
  if (toggle) toggle.addEventListener('click', function () { setPresenter(!document.body.classList.contains('presenter')); });

  // ---------- copy buttons ----------
  function copyText(text, button) {
    function done() {
      var original = button.innerHTML;
      button.classList.add('copied');
      button.innerHTML = '<i class="bi bi-check2"></i> Copied';
      setTimeout(function () { button.classList.remove('copied'); button.innerHTML = original; }, 1600);
    }
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(done, function () { fallback(text); done(); });
    } else {
      fallback(text);
      done();
    }
  }
  function fallback(text) {
    var area = document.createElement('textarea');
    area.value = text;
    area.setAttribute('readonly', '');
    area.style.position = 'fixed';
    area.style.opacity = '0';
    document.body.appendChild(area);
    area.select();
    try { document.execCommand('copy'); } catch (e) { /* nothing else to try */ }
    document.body.removeChild(area);
  }
  document.addEventListener('click', function (event) {
    var button = event.target.closest('.tc-copy');
    if (!button) return;
    var target = button.getAttribute('data-copy-target');
    var text = '';
    if (target === 'code') {
      var code = button.closest('.tc-code').querySelector('pre code');
      text = code ? code.textContent : '';
    } else if (target === 'outline') {
      var outline = button.closest('.tc-episode').querySelector('[data-outline]');
      text = outline ? outline.textContent : '';
    }
    if (text) copyText(text, button);
  });

  // ---------- code highlighting ----------
  if (window.hljs) {
    document.querySelectorAll('.tc-code pre code').forEach(function (block) {
      try { window.hljs.highlightElement(block); } catch (e) { /* unknown language: leave plain */ }
    });
  }

  // ---------- Mermaid diagrams, each with a Download SVG button ----------
  if (window.mermaid) {
    window.mermaid.initialize({
      startOnLoad: false,
      securityLevel: 'loose',          // allows the "click" links in the module diagrams
      theme: 'base',
      themeVariables: {
        primaryColor: '#e8edff', primaryBorderColor: '#3b5bfd', primaryTextColor: '#0b1f4b',
        lineColor: '#2a46d6', secondaryColor: '#f4f6fc', tertiaryColor: '#ffffff',
        fontFamily: 'Inter, "Segoe UI", system-ui, sans-serif', fontSize: '14px'
      },
      flowchart: { htmlLabels: true, curve: 'basis' },
      er: { layoutDirection: 'TB' },
      sequence: { mirrorActors: false }
    });
    window.mermaid.run({ querySelector: 'pre.mermaid' }).then(addDownloadButtons, function (err) {
      console.error('Mermaid failed', err);
      addDownloadButtons();
    });
  }
  function addDownloadButtons() {
    document.querySelectorAll('.tc-diagram').forEach(function (box, i) {
      var svg = box.querySelector('svg');
      if (!svg || box.querySelector('.tc-diagram-tools')) return;
      var tools = document.createElement('div');
      tools.className = 'tc-diagram-tools';
      var button = document.createElement('button');
      button.type = 'button';
      button.className = 'btn btn-sm btn-outline-primary';
      button.innerHTML = '<i class="bi bi-download"></i> Download SVG';
      button.addEventListener('click', function () {
        var section = box.closest('section');
        var name = (document.title.split(' · ')[0] + '-' + (section ? section.id : 'diagram-' + i))
          .toLowerCase().replace(/[^a-z0-9]+/g, '-');
        var source = new XMLSerializer().serializeToString(svg);
        var blob = new Blob(['<?xml version="1.0" encoding="UTF-8"?>\n' + source], { type: 'image/svg+xml' });
        var link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = name + '.svg';
        document.body.appendChild(link);
        link.click();
        setTimeout(function () { URL.revokeObjectURL(link.href); link.remove(); }, 500);
      });
      tools.appendChild(button);
      box.appendChild(tools);
    });
  }

  // ---------- "On this page": highlight the section being read ----------
  var toc = document.getElementById('toc');
  if (toc && 'IntersectionObserver' in window) {
    var links = {};
    toc.querySelectorAll('a[href^="#"]').forEach(function (a) { links[a.getAttribute('href').slice(1)] = a; });
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting && links[entry.target.id]) {
          Object.keys(links).forEach(function (k) { links[k].classList.remove('active'); });
          links[entry.target.id].classList.add('active');
        }
      });
    }, { rootMargin: '-80px 0px -70% 0px' });
    Object.keys(links).forEach(function (id) {
      var el = document.getElementById(id);
      if (el) observer.observe(el);
    });
  }
})();
