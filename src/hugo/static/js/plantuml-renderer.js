/**
 * PlantUML client-side renderer.
 * Finds all .plantuml-source elements, encodes the source using deflate + PlantUML encoding,
 * and renders as images via a PlantUML server.
 *
 * Requires pako.min.js to be loaded before this script.
 * Server URL is read from data-server attribute on body, or defaults to public server.
 */
(function () {
  'use strict';

  var SERVER = document.body.getAttribute('data-plantuml-server') || 'https://www.plantuml.com/plantuml';
  var FORMAT = document.body.getAttribute('data-plantuml-format') || 'svg';

  function encode6bit(b) {
    if (b < 10) return String.fromCharCode(48 + b);
    b -= 10;
    if (b < 26) return String.fromCharCode(65 + b);
    b -= 26;
    if (b < 26) return String.fromCharCode(97 + b);
    b -= 26;
    if (b === 0) return '-';
    if (b === 1) return '_';
    return '?';
  }

  function append3bytes(b1, b2, b3) {
    var c1 = b1 >> 2;
    var c2 = ((b1 & 0x3) << 4) | (b2 >> 4);
    var c3 = ((b2 & 0xF) << 2) | (b3 >> 6);
    var c4 = b3 & 0x3F;
    return encode6bit(c1 & 0x3F) + encode6bit(c2 & 0x3F) + encode6bit(c3 & 0x3F) + encode6bit(c4 & 0x3F);
  }

  function encode64(data) {
    var r = '';
    for (var i = 0; i < data.length; i += 3) {
      if (i + 2 === data.length) {
        r += append3bytes(data[i], data[i + 1], 0);
      } else if (i + 1 === data.length) {
        r += append3bytes(data[i], 0, 0);
      } else {
        r += append3bytes(data[i], data[i + 1], data[i + 2]);
      }
    }
    return r;
  }

  function encodePlantUml(source) {
    var utf8 = new TextEncoder().encode(source);
    var deflated = pako.deflateRaw(utf8, { level: 9 });
    return '~1' + encode64(deflated);
  }

  function renderDiagrams() {
    var diagrams = document.querySelectorAll('.plantuml-diagram');
    diagrams.forEach(function (container) {
      var sourceEl = container.querySelector('.plantuml-source');
      if (!sourceEl) return;

      var source = sourceEl.textContent.trim();
      var encoded = encodePlantUml(source);
      var url = SERVER + '/' + FORMAT + '/' + encoded;

      if (FORMAT === 'svg') {
        var obj = document.createElement('object');
        obj.type = 'image/svg+xml';
        obj.data = url;
        obj.style.maxWidth = '100%';
        obj.setAttribute('aria-label', 'PlantUML Diagram');
        container.appendChild(obj);
      } else {
        var img = document.createElement('img');
        img.src = url;
        img.alt = 'PlantUML Diagram';
        img.loading = 'lazy';
        img.style.maxWidth = '100%';
        container.appendChild(img);
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', renderDiagrams);
  } else {
    renderDiagrams();
  }
})();
