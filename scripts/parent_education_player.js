(function (global) {
  'use strict';

  function interpolate(frames, year) {
    year = Math.max(frames[0].survey_year, Math.min(frames[frames.length - 1].survey_year, year));
    var i = 0;
    while (i < frames.length - 2 && year > frames[i + 1].survey_year) i++;
    var a = frames[i], b = frames[i + 1];
    var fraction = (year - a.survey_year) / (b.survey_year - a.survey_year);
    var blend = function (x, y) { return x + (y - x) * fraction; };
    var totalA = a.parent_width_weights.reduce(function (x, y) { return x + y; }, 0);
    var totalB = b.parent_width_weights.reduce(function (x, y) { return x + y; }, 0);
    var shares = a.parent_width_weights.map(function (v, p) { return blend(v / totalA, b.parent_width_weights[p] / totalB); });
    var matrix = a.m.map(function (row, p) { return row.map(function (v, c) { return blend(v, b.m[p][c]); }); });
    var exact = frames.find(function (f) { return Math.abs(f.survey_year - year) < 0.0001; });
    return { year: year, shares: shares, matrix: matrix, exact: exact, from: a, to: b };
  }

  function aggregate(state, bands) {
    var shares = bands.map(function (parents) { return parents.reduce(function (sum, p) { return sum + state.shares[p]; }, 0); });
    var matrix = bands.map(function (parents, group) {
      return bands.map(function (children) {
        var joint = parents.reduce(function (sum, p) {
          var total = state.matrix[p].reduce(function (a, b) { return a + b; }, 0);
          var share = children.reduce(function (a, c) { return a + state.matrix[p][c]; }, 0) / total;
          return sum + state.shares[p] * share;
        }, 0);
        return 100 * joint / shares[group];
      });
    });
    return Object.assign({}, state, { shares: shares, matrix: matrix });
  }

  function view(svg) {
    var data = JSON.parse(svg.querySelector('#timeline-data').textContent);
    if (svg.pauseAnimations) svg.pauseAnimations();
    svg.querySelectorAll('animate,animateTransform').forEach(function (node) { node.remove(); });
    svg.querySelectorAll('[data-survey-frame]').forEach(function (g, i) { g.style.display = i ? 'none' : ''; g.setAttribute('opacity', '1'); });
    svg.querySelectorAll('[data-value-frame],[data-total-frame]').forEach(function (text) {
      text.style.display = text.getAttribute('data-value-frame') === '0' || text.getAttribute('data-total-frame') === '0' ? '' : 'none';
      text.setAttribute('opacity', '1');
    });
    return {
      svg: svg, data: data, plot: data.plot,
      title: svg.querySelector('[data-time-title]'), subtitle: svg.querySelector('[data-time-sub]'),
      note: svg.querySelector('[data-width-note]'),
      tiles: Array.from(svg.querySelectorAll('rect[data-parent][data-child]')),
      values: Array.from(svg.querySelectorAll('[data-value-frame="0"]')),
      totals: Array.from(svg.querySelectorAll('[data-total-frame="0"]')),
      parentLabels: Array.from(svg.querySelectorAll('[data-parent-label]')),
      childLabels: Array.from(svg.querySelectorAll('[data-child-label]'))
    };
  }

  // One player and clock for one or more charts built on the same survey frames.
  function create(svgs, host, options) {
    options = options || {};
    var views = (svgs.length === undefined ? [svgs] : Array.from(svgs)).map(view);
    var frames = views[0].data.frames;
    var start = frames[0].survey_year, end = frames[frames.length - 1].survey_year;
    var year = end, playing = false, raf = 0, last = 0, played = false;
    var reduce = global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var box = document.createElement('div'); box.className = 'player time-player';
    var button = document.createElement('button'); button.type = 'button'; button.className = 'main';
    var slider = document.createElement('input'); slider.type = 'range'; slider.min = start; slider.max = end; slider.step = '0.01'; slider.setAttribute('aria-label', 'Animation year');
    var output = document.createElement('output'); output.setAttribute('aria-live', 'off');
    var rounds = document.createElement('div'); rounds.className = 'timeline-rounds'; rounds.setAttribute('role', 'group'); rounds.setAttribute('aria-label', 'Jump to survey');
    box.append(button, slider, output, rounds);
    host.insertBefore(box, host.querySelector('figcaption'));
    frames.forEach(function (frame) {
      var b = document.createElement('button'); b.type = 'button'; b.textContent = frame.title.replace('Survey ', '');
      b.addEventListener('click', function () { seek(frame.survey_year); }); rounds.appendChild(b);
    });

    function drawView(v) {
      var data = v.data, plot = v.plot, title = v.title, subtitle = v.subtitle, note = v.note;
      var state = interpolate(frames, year), x = plot.x;
      if (data.bands) state = aggregate(state, data.bands);
      var positions = state.shares.map(function (share) { var pos = { x: x, width: plot.width * share }; x += pos.width; return pos; });
      var geometry = state.matrix.map(function (row) {
        var sum = row.reduce(function (a, b) { return a + b; }, 0), bottom = plot.y + plot.height;
        return row.map(function (v) { var height = plot.height * v / sum; bottom -= height; return { y: bottom, height: height }; });
      });
      v.tiles.forEach(function (tile) {
        var p = +tile.dataset.parent, c = +tile.dataset.child, pos = positions[p], cell = geometry[p][c];
        tile.setAttribute('x', pos.x); tile.setAttribute('width', pos.width); tile.setAttribute('y', cell.y); tile.setAttribute('height', cell.height);
        tile.querySelector('title').textContent = data.parent_levels[p] + ' → ' + data.own_levels[c] + ': ' + state.matrix[p][c].toFixed(1) + '% (' + (state.exact ? state.exact.title : 'interpolated ' + year.toFixed(1)) + ')';
      });
      v.values.forEach(function (text) {
        var p = +text.dataset.valueParent, c = +text.dataset.valueChild;
        text.setAttribute('x', positions[p].x + positions[p].width / 2);
        text.setAttribute('y', geometry[p][c].y + geometry[p][c].height / 2);
        text.textContent = state.matrix[p][c].toFixed(1);
      });
      v.parentLabels.forEach(function (g) { var pos = positions[+g.dataset.parentLabel]; g.setAttribute('transform', 'translate(' + (pos.x + pos.width / 2) + ' 0)'); });
      v.childLabels.forEach(function (g) { var cell = geometry[0][+g.dataset.childLabel]; g.setAttribute('transform', 'translate(0 ' + (cell.y + cell.height / 2) + ')'); });
      v.totals.forEach(function (text) {
        var p = +text.dataset.parentTotal, pos = positions[p]; text.setAttribute('x', pos.x + pos.width / 2);
        var population = state.exact && state.exact.parent_population;
        var count = population && (data.bands ? data.bands[p].reduce(function (sum, original) { return sum + population[original]; }, 0) : population[p]);
        text.textContent = population ? count.toLocaleString('en-US') : (state.shares[p] * 100).toFixed(1) + '%';
      });
      title.textContent = state.exact ? state.exact.title : 'Year ' + year.toFixed(1);
      subtitle.textContent = state.exact ? state.exact.sub : 'aged 25 to 44 · interpolated between ' + state.from.title.replace('Survey ', '') + ' and ' + state.to.title.replace('Survey ', '');
      note.textContent = state.exact ? (state.exact.parent_width_is_assumed ? 'Estimated widths: extrapolated group proportions; tile values are published survey percentages.' : 'Survey values. Widths = weighted population; numbers above columns = people represented.') : 'Between surveys: tile percentages are interpolated; column widths follow the modeled group proportions.';
      if (data.bands) note.textContent = state.exact ? (state.exact.parent_width_is_assumed ? 'Estimated widths and merged shares use extrapolated parent-group proportions.' : 'Population-weighted merged survey shares; numbers above columns = people represented.') : 'Between surveys: source percentages are interpolated, then merged using parent-group weights.';
      return state;
    }

    function draw() {
      var state = views.map(drawView)[0];
      slider.value = year; output.textContent = state.exact ? state.exact.title.replace('Survey ', '') : year.toFixed(1);
      slider.setAttribute('aria-valuetext', output.textContent + (state.exact ? ', survey round' : ', interpolated'));
      Array.from(rounds.children).forEach(function (b, i) { b.setAttribute('aria-pressed', String(!!state.exact && state.exact === frames[i])); });
      var label = playing ? 'Pause' : year >= end ? 'Replay' : 'Play';
      if (button.getAttribute('aria-label') !== label) {
        button.setAttribute('aria-label', label); button.title = label;
        button.innerHTML = playing ? '<svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true"><path d="M4 3h3v10H4zm5 0h3v10H9z" fill="currentColor"/></svg>' : '<svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true"><path d="M5 2v12l9-6z" fill="currentColor"/></svg>';
      }
    }
    function tick(now) {
      if (!playing) return;
      year = Math.min(end, year + (now - last) / 1000); last = now;
      if (year >= end) playing = false;
      draw(); if (playing) raf = global.requestAnimationFrame(tick);
    }
    function pause() { playing = false; global.cancelAnimationFrame(raf); draw(); }
    function play() { if (playing) return; if (year >= end) year = start; playing = played = true; last = global.performance.now(); draw(); raf = global.requestAnimationFrame(tick); }
    function seek(value) { pause(); played = true; year = Math.max(start, Math.min(end, +value)); draw(); }
    button.addEventListener('click', function () { playing ? pause() : play(); });
    slider.addEventListener('input', function () { seek(slider.value); });
    views.forEach(function (v) { v.svg.addEventListener('click', function () { playing ? pause() : play(); }); v.svg.style.cursor = 'pointer'; });
    draw();
    if (!reduce && options.autoplay !== false) {
      if (options.observe && 'IntersectionObserver' in global) {
        var observer = new global.IntersectionObserver(function (entries) { if (entries.some(function (e) { return e.isIntersecting; }) && !played) { play(); observer.disconnect(); } }, { threshold: 0.5 });
        observer.observe(host);
      } else play();
    }
    return { seek: seek, play: play, pause: pause, getYear: function () { return year; }, isPlaying: function () { return playing; } };
  }
  var api = { interpolate: interpolate, aggregate: aggregate, create: create };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else global.ParentEducationTimeline = api;
})(typeof window !== 'undefined' ? window : globalThis);
