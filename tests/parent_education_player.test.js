const test = require('node:test');
const assert = require('node:assert/strict');
const { interpolate, aggregate } = require('../scripts/parent_education_player.js');
const { frames_age_25_44: frames, frames_matura_threshold: maturaFrames, frames_degree_threshold: degreeFrames } = require('../data/parent-education.json');

function close(actual, expected) { assert.ok(Math.abs(actual - expected) < 1e-10, `${actual} != ${expected}`); }

test('survey dates preserve published percentages and population proportions', () => {
  for (const frame of frames) {
    const state = interpolate(frames, frame.survey_year);
    assert.equal(state.exact, frame);
    const total = frame.parent_width_weights.reduce((a, b) => a + b, 0);
    for (let p = 0; p < 4; p++) {
      close(state.shares[p], frame.parent_width_weights[p] / total);
      for (let c = 0; c < 4; c++) close(state.matrix[p][c], frame.m[p][c]);
    }
  }
});

test('intermediate dates use calendar spacing and identify estimated values', () => {
  const state = interpolate(frames, 2010);
  assert.equal(state.exact, undefined);
  assert.equal(state.from, frames[0]);
  assert.equal(state.to, frames[1]);
  close(state.matrix[0][0], 30.1 + (27.3 - 30.1) * 3 / 4.5);
  const midpoint = interpolate(frames, 2019.5);
  close(midpoint.matrix[3][3], (57.3 + 61.3) / 2);
});

test('the entire timeline has positive shares totaling one without mutating sources', () => {
  const before = JSON.stringify(frames);
  for (let year = 2007; year <= 2022.5; year += 0.05) {
    const state = interpolate(frames, year);
    close(state.shares.reduce((a, b) => a + b, 0), 1);
    assert.ok(state.shares.every(v => v > 0));
    for (let p = 0; p < 4; p++) for (let c = 0; c < 4; c++) {
      const value = state.matrix[p][c];
      assert.ok(value >= Math.min(state.from.m[p][c], state.to.m[p][c]) - 1e-10);
      assert.ok(value <= Math.max(state.from.m[p][c], state.to.m[p][c]) + 1e-10);
    }
  }
  assert.equal(JSON.stringify(frames), before);
});

test('seeking beyond the timeline clamps to its endpoints', () => {
  assert.equal(interpolate(frames, 1900).exact, frames[0]);
  assert.equal(interpolate(frames, 2100).exact, frames[3]);
});

test('merging at Matura preserves all four joint population blocks at every date', () => {
  const bands = [[0, 1], [2, 3]];
  for (let year = 2007; year <= 2022.5; year += 0.25) {
    const original = interpolate(frames, year);
    const grouped = aggregate(original, bands);
    close(grouped.shares.reduce((a, b) => a + b, 0), 1);
    for (let p = 0; p < 2; p++) {
      close(grouped.matrix[p][0] + grouped.matrix[p][1], 100);
      for (let c = 0; c < 2; c++) {
        const expected = bands[p].reduce((sum, parent) => {
          const total = original.matrix[parent].reduce((a, b) => a + b, 0);
          return sum + original.shares[parent] * bands[c].reduce((a, child) => a + original.matrix[parent][child], 0) / total;
        }, 0);
        close(grouped.shares[p] * grouped.matrix[p][c] / 100, expected);
      }
    }
  }
});

test('generated two-group survey matrices match the continuous player', () => {
  for (let i = 0; i < frames.length; i++) {
    const grouped = aggregate(interpolate(frames, frames[i].survey_year), [[0, 1], [2, 3]]);
    for (let p = 0; p < 2; p++) for (let c = 0; c < 2; c++) close(grouped.matrix[p][c], maturaFrames[i].m[p][c]);
  }
  assert.deepEqual(maturaFrames[3].parent_population, [1580100, 822300]);
  assert.equal(maturaFrames[0].parent_population, null);
});

test('generated degree-threshold matrices match the continuous player', () => {
  const bands = [[0, 1, 2], [3]];
  for (let i = 0; i < frames.length; i++) {
    const grouped = aggregate(interpolate(frames, frames[i].survey_year), bands);
    for (let p = 0; p < 2; p++) {
      close(grouped.matrix[p][0] + grouped.matrix[p][1], 100);
      for (let c = 0; c < 2; c++) close(grouped.matrix[p][c], degreeFrames[i].m[p][c]);
    }
    // Parents with a degree form a single source group, so their published rate is kept exactly.
    close(degreeFrames[i].m[1][1], frames[i].m[3][3] / frames[i].m[3].reduce((a, b) => a + b, 0) * 100);
  }
  assert.deepEqual(degreeFrames[3].parent_population, [1959100, 443300]);
  assert.equal(degreeFrames[0].parent_population, null);
});
