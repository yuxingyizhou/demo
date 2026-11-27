import {pavilionPlan} from './districts.mjs';

export const waterTownSeed = 46;
const size = 48;
const cell = (x, y, z) => x + 64 * z + 4096 * y;
const crossings = [13, 22, 32];
const landings = [[15, 0], [17, 1], [27, 0], [30, 1]];
const neighborhoods = [
  [9, 10, 0], [11, 12, 3], [15, 16, 5], [17, 18, 1], [19, 20, 2],
  [24, 25, 5], [26, 27, 0], [28, 29, 4], [34, 35, 2], [36, 37, 7],
];

function banks(z) {
  const west = 20 + Math.floor((z - 9) / 8);
  return [west, west + (z >= 18 && z <= 28 ? 6 : 5)];
}

const offshoreRules = new Set(['L19.sailboats', 'L38.galleon', 'L39.cog', 'L42.passing-sails']);
const terrainSignature = [[5, 20, 0], [8, 20, 1], [24, 25, 0], [35, 11, 1]];

export function isWaterTown(world) {
  const terrain = world.terrainEdits;
  return world.seed === waterTownSeed && (terrain?.size ?? 0) >= 500 &&
    terrainSignature.filter(([x, z, height]) => terrain.get(x + z * size) === height).length >= 3;
}

export function waterTownRules(world, rules) {
  return isWaterTown(world) ? rules.filter(rule => !offshoreRules.has(rule.id)) : rules;
}

function makeTerrain(seed, api) {
  const base = api.terrain(seed, 2);
  const terrainEdits = new Map();
  for (let z = 5; z < 43; z++) {
    const [west, east] = banks(z);
    const point = z <= 25 ? 25 - z : z - 25;
    const shoulder = Math.max(0, Math.floor((point - 8) / 2));
    const left = 7 + shoulder + (z >= 34 ? 1 : 0);
    const right = 41 - shoulder - (z <= 13 ? 1 : 0);
    for (let x = 5; x < 43; x++) {
      const inside = z >= 7 && z <= 39 && (x >= left && x <= west || x >= east && x <= right);
      const height = inside ? 1 : 0;
      const col = x + z * size;
      if (base.height[col] !== height) terrainEdits.set(col, height);
    }
  }
  return {version: 1, seed, terrainGen: 2, terrainEdits, nextSeq: 1,
    blocks: new Map(), floors: new Map(), edges: new Map()};
}

export function waterTown(spec, api) {
  const initialWorld = makeTerrain(spec.seed, api);
  const terrain = api.terrainFromWorld(initialWorld);
  let world = initialWorld;
  const edits = [];
  function apply(edit) {
    const check = api.can(world, terrain, edit);
    if (!check.ok) throw new Error(`水乡构件无法放置 ${JSON.stringify(edit)} (${check.reason})`);
    world = api.apply(world, terrain, edit);
    edits.push(edit);
  }
  function floor(x, z, kind = 'path', y = 1) {
    const at = cell(x, y, z);
    if (world.floors.get(at) === kind) return;
    if (world.floors.has(at)) apply({type: 'eraseFloor', cell: at});
    apply({type: 'placeFloor', cell: at, floor: kind});
  }
  function block(x, y, z, kind, color = 0, style = 0) {
    apply({type: 'placeBlock', cell: cell(x, y, z), kind, color, style});
  }

  for (let z = 8; z <= 38; z++) {
    const [west, east] = banks(z);
    for (const x of [west - 1, west, east, east + 1]) floor(x, z);
    const opening = crossings.some(crossing => Math.abs(z - crossing) <= 1) ||
      landings.some(([landing]) => landing === z);
    if (!opening) {
      apply({type: 'placeEdge', edge: cell(west, 1, z) * 2, kind: 'wall'});
      apply({type: 'placeEdge', edge: cell(east - 1, 1, z) * 2, kind: 'wall'});
    }
  }

  for (const z of crossings) {
    const [west, east] = banks(z);
    for (let x = west + 1; x < east; x++) block(x, 0, z, 'arch', 3);
    for (let x = west - 4; x <= east + 4; x++) floor(x, z);
  }

  for (const [from, to, color] of neighborhoods) {
    for (const [side, offset] of [[0, -1], [1, 1]]) {
      const frontage = banks(from)[side] + offset * 2;
      const style = offset < 0 ? 1 + color % 3 : 3 + color % 3;
      for (let z = from; z <= to; z++) {
        block(frontage, 1, z, 'house', color, style);
        block(frontage + offset, 1, z, 'house', color, style);
        if (color !== 4 && (color !== 7 || side === 0)) block(frontage, 2, z, 'house', color, style);
      }
    }
  }

  for (const [z, side, end] of [[14, 1, 35], [21, 0, 13], [30, 0, 13], [33, 1, 35]]) {
    const start = banks(z)[side];
    for (let x = Math.min(start, end); x <= Math.max(start, end); x++) floor(x, z);
  }
  for (const [x, z, color, style] of [[34, 15, 3, 2], [12, 19, 5, 5], [13, 31, 1, 1], [35, 35, 2, 3]]) {
    for (const dx of [0, 1]) for (const dz of [0, 1]) block(x + dx, 1, z + dz, 'house', color, style);
    block(x, 2, z, 'house', color, style);
    block(x + 1, 2, z, 'house', color, style);
  }

  for (const [z, side] of landings) {
    const bank = banks(z)[side];
    block(bank + (side === 0 ? 1 : -1), 0, z, 'dock');
  }
  for (const z of [8, 14, 23, 30, 38]) {
    const [west, east] = banks(z);
    block(west, 1, z, 'tree');
    block(east, 1, z, 'tree');
  }
  for (const [x, z] of [[11, 11], [11, 18], [12, 23], [10, 25], [13, 27], [12, 29],
    [12, 33], [15, 36], [36, 10], [38, 13], [37, 17], [36, 20], [35, 23], [39, 24],
    [38, 29], [37, 35]]) block(x, 1, z, 'tree');

  const [gardenBank] = banks(23);
  const pavilion = pavilionPlan(world, terrain, cell(gardenBank - 6, 1, 24), api);
  if (!pavilion.edits.length) throw new Error(pavilion.refusal);
  pavilion.edits.forEach(apply);
  for (let z = 23; z < 28; z++) {
    floor(gardenBank - 7, z, z === 23 ? 'path' : 'garden');
    floor(gardenBank - 4, z, 'garden');
  }
  for (let x = gardenBank - 7; x <= gardenBank - 4; x++) floor(x, 22);
  const east = banks(22)[1];
  for (let z = 21; z <= 23; z++) for (let x = east + 2; x <= east + 5; x++) floor(x, z, 'plaza');
  for (const z of [21, 23]) block(east + 5, 1, z, 'stall');

  for (const [minX, maxX, minZ, maxZ] of [[11, 15, 12, 17], [34, 37, 28, 34]]) {
    for (let z = minZ; z <= maxZ; z++) for (let x = minX; x <= maxX; x++) floor(x, z, 'garden');
  }

  const roles = {};
  for (const {role} of api.resolve(world, terrain).roles.values()) roles[role] = (roles[role] ?? 0) + 1;
  if (roles['stone-bridge'] !== crossings.length || !roles.bandstand) throw new Error('水乡石桥或凉亭没有形成');
  return {seed: spec.seed, name: spec.name, world, terrain, initialWorld,
    camera: {target: [24, 1, 23], yaw: 36, pitch: 34, zoom: 2.8},
    plan: {character: 'river', edits, unjoined: [], refused: 0, fellBack: false},
    audit: {removed: 0, skipped: [], roles, blocks: world.blocks.size, floors: world.floors.size,
      edges: world.edges.size, bridges: crossings, terrainColumns: initialWorld.terrainEdits.size}};
}
