import {pavilionPlan} from './districts.mjs';

export const waterTownSeed = 46;
export const lanternTownSeed = 208;
const size = 48;
const cell = (x, y, z) => x + 64 * z + 4096 * y;
export const lanternLandmarks = {
  bridge: {x: 22, z: 22},
  gate: {x: 34, z: 22, posts: [20, 21, 23, 24]},
  tower: {x: 13, z: 22},
};
export const lanternLanding = {x: 28, z: 26};
export const lanternStalls = [[30, 21], [31, 23], [33, 20], [35, 24]];

export function lanternActivities(plan) {
  const sites = [
    ['turning', 32, 22, .32, .25], ['wash', 32, 22, .32, .25, 1.15],
    ['wash', 30, 22, .40, .32, 1.25], ['wash', 31, 23, .38, .31, .85],
    ['wash', 28, 26, .35, .5, .52],
    ['riddles', 29, 20, .44, .8], ['riddles', 31, 22, .15, .52], ['riddles', 28, 27, .27, .26],
    ['child', 24, 22, .55, .31, 4.4], ['child', 26, 22, .1, .68, 3.5],
    ['child', 30, 22, .49, .76, 2.6], ['child', 32, 21, .71, .79, 1.18],
    ['child', 28, 26, .24, .82],
    ['stroll', 28, 22, .26, .64, 2.6],
    ['watch', 28, 26, .47, .38], ['watch', 28, 27, .28, .54],
    ['riddle', 29, 22, .29, .08], ['riddle', 30, 20, .27, .8],
    ['riddle', 30, 22, .23, .34], ['guest', 30, 22, .67, .7],
    ['seller', 30, 20, .44, .93], ['guest', 31, 22, .6, .81],
    ['guest', 31, 21, .55, .36], ['stroll', 31, 21, .46, .71, 2],
    ['riddle', 32, 22, .77, .83], ['riddle', 33, 22, .34, .24], ['guest', 32, 23, .14, .31],
    ['seller', 35, 23, .47, .94], ['guest', 35, 23, .86, .43],
  ];
  return sites.flatMap(([kind, x, z, dx, dz, extent], index) => {
    const anchor = cell(x, 1, z);
    if (!plan.floorAt.has(anchor) || plan.kinds.has(anchor)) return [];
    let walk = extent ?? 0;
    if (kind === 'stroll' || kind === 'child') {
      for (let col = x + 1; col <= Math.floor(x + dx + walk); col++) {
        const next = cell(col, 1, z);
        if (!plan.floorAt.has(next) || plan.kinds.has(next)) {
          walk = Math.max(0, col - x - dx - .12);
          break;
        }
      }
    }
    return [{anchor, key: String(index), data: {kind, x: x + dx, z: z + dz, walk, index}}];
  });
}
const crossings = [13, 22, 32];
const landings = [[15, 0], [17, 1], [27, 0], [30, 1]];
// x at the river end, first and last z, depth, storeys, colour, style
const westRows = [
  [19, 9, 12, 2, 2, 0, 1], [19, 14, 16, 2, 1, 5, 3], [20, 17, 20, 3, 2, 2, 4],
  [20, 23, 24, 2, 2, 1, 3], [21, 25, 28, 2, 2, 0, 1], [21, 29, 31, 2, 1, 3, 5],
  [22, 33, 35, 3, 2, 5, 4], [22, 36, 38, 2, 1, 2, 1],
];
const eastRows = [
  [25, 9, 11, 2, 1, 1, 5], [26, 12, 12, 2, 2, 0, 4], [25, 14, 16, 2, 2, 5, 3],
  [27, 18, 20, 2, 2, 0, 1], [27, 23, 24, 2, 2, 5, 4], [28, 25, 28, 2, 1, 1, 5],
  [27, 29, 29, 2, 2, 2, 3], [28, 33, 36, 2, 2, 0, 4], [29, 37, 38, 2, 1, 3, 5],
];

function banks(z) {
  const west = 20 + Math.floor((z - 9) / 8);
  return [west, west + (z >= 18 && z <= 28 ? 6 : 5)];
}

const offshoreRules = new Set(['L19.sailboats', 'L38.galleon', 'L39.cog', 'L42.passing-sails']);
const canalShapeRules = new Set(['R-H05.boathouse', 'R-H16.watermill', 'U11-F.hall-front']);
const lanternDecorations = new Set(['D04.bunting', 'D08.cafe-tables', 'D13.flags', 'D13-T.tallest-flag',
  'D27.post', 'D31.viewpoint', 'D35.festival-lights']);
const terrainSignature = [[5, 20, 0], [8, 20, 1], [24, 25, 0], [35, 11, 1]];

export function isWaterTown(world) {
  const terrain = world.terrainEdits;
  return isLanternTown(world) || world.seed === waterTownSeed && (terrain?.size ?? 0) >= 500 &&
    terrainSignature.filter(([x, z, height]) => terrain.get(x + z * size) === height).length >= 3;
}

export function isLanternTown(world) {
  const terrain = world.terrainEdits;
  return world.seed === lanternTownSeed && (terrain?.size ?? 0) >= 290 &&
    terrainSignature.filter(([x, z, height]) => terrain.get(x + z * size) === height).length >= 2;
}

export function waterTownRules(world, rules) {
  const lantern = isLanternTown(world);
  return isWaterTown(world) ? rules.filter(rule => !offshoreRules.has(rule.id) &&
    !(lantern && lanternDecorations.has(rule.id))) : rules;
}

export function waterTownShapeRules(world, rules) {
  const lantern = isLanternTown(world);
  return isWaterTown(world) ? rules.filter(rule => !canalShapeRules.has(rule.id) &&
    !(lantern && rule.id === 'J22.plaza-paving')) : rules;
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
  const festival = spec.seed === lanternTownSeed;
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
    if (world.blocks.has(at)) return;
    if (world.floors.get(at) === kind) return;
    if (world.floors.has(at)) apply({type: 'eraseFloor', cell: at});
    apply({type: 'placeFloor', cell: at, floor: kind});
  }
  function block(x, y, z, kind, color = 0, style = 0) {
    apply({type: 'placeBlock', cell: cell(x, y, z), kind, color, style});
  }

  for (const z of crossings) {
    const [west, east] = banks(z);
    for (let x = west + 1; x < east; x++) block(x, 0, z, 'arch', 3);
    for (let x = west - 7; x <= east + 7; x++) floor(x, z);
  }

  function houses(rows, direction) {
    for (const [x, from, to, depth, storeys, color, style] of rows) {
      for (let y = 1; y <= storeys; y++) {
        for (let z = from; z <= to; z++) {
          for (let offset = 0; offset < depth; offset++) block(x + direction * offset, y, z, 'house', color, style);
        }
      }
    }
  }
  houses(westRows, -1);
  houses(festival ? eastRows.map(row => row[1] === 25 ? [row[0] + 1, ...row.slice(1)] : row) : eastRows, 1);
  houses(festival ? [[14, 9, 13, 2, 2, 0, 4], [15, 15, 19, 2, 1, 5, 1],
    [13, 26, 29, 2, 1, 0, 5], [16, 34, 37, 2, 2, 5, 1]] :
    [[15, 10, 12, 1, 1, 0, 5], [14, 14, 16, 2, 2, 2, 3], [15, 18, 20, 2, 1, 5, 1],
      [14, 28, 30, 2, 1, 2, 5], [16, 34, 37, 2, 2, 5, 1]], -1);
  houses(festival ? [[31, 9, 11, 2, 2, 5, 4], [32, 14, 17, 2, 2, 0, 3], [36, 23, 26, 2, 2, 5, 4],
    [31, 28, 31, 2, 1, 1, 4], [33, 34, 38, 2, 1, 5, 3]] :
    [[31, 9, 11, 2, 2, 5, 4], [31, 15, 16, 2, 1, 0, 3], [32, 23, 26, 2, 2, 3, 1],
      [31, 28, 31, 2, 1, 1, 4], [33, 34, 38, 2, 1, 5, 3]], 1);

  for (let z = 8; z <= 38; z++) {
    const [west, east] = banks(z);
    for (const x of [west, west - 4, east + 2]) floor(x, z);
    if (z !== 8 && banks(z - 1)[1] !== east) floor(banks(z - 1)[1] + 2, z);
  }
  for (const [z, side, end] of [[14, 1, 31], [21, 0, 14], [27, 1, 33], [30, 0, 16], [33, 1, 34]]) {
    const start = banks(z)[side];
    for (let x = Math.min(start, end); x <= Math.max(start, end); x++) floor(x, z);
  }

  for (const [z, side] of festival ? [...landings.slice(0, 3), [lanternLanding.z, 1]] : landings) {
    const bank = banks(z)[side];
    floor(bank, z);
    block(bank + (side === 0 ? 1 : -1), 0, z, 'dock');
  }
  for (const [z, side, inset] of [[8, 0, -1], [8, 1, 0], [12, 1, 0], [21, 1, 0],
    [31, 1, 0], [37, 0, 0], [37, 1, 0], [38, 1, 0]]) {
    block(banks(z)[side] + inset, 1, z, 'tree');
  }
  for (const [x, z] of [[11, 11], [11, 18], [12, 23], [10, 25], [13, 27], [12, 29],
    [12, 33], [13, 36], [36, 10], [38, 13], [37, 17], [36, 20], [35, 23], [39, 24],
    [38, 29], [37, 35]]) {
    if (!world.blocks.has(cell(x, 1, z)) && !(festival && x >= 34 && x <= 37 && z >= 20 && z <= 24)) block(x, 1, z, 'tree');
  }

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
  for (let z = 20; z <= 22; z++) for (let x = east + 2; x <= east + 5; x++) floor(x, z, 'plaza');
  if (!festival) for (const z of [20, 21]) block(east + 5, 1, z, 'stall');

  if (festival) {
    const {gate, tower} = lanternLandmarks;
    floor(28, 30);
    for (let z = 25; z <= 28; z++) floor(28, z);
    for (let x = 29; x <= 31; x++) for (let z = 20; z <= 24; z++) floor(x, z, 'plaza');
    for (let z = 19; z <= 24; z++) for (let x = 31; x <= 37; x++) floor(x, z, 'plaza');
    for (const z of gate.posts) block(gate.x, 1, z, 'pillar', 6);
    for (const [x, z] of lanternStalls) block(x, 1, z, 'stall');
    for (let y = 1; y <= 5; y++) block(tower.x, y, tower.z, 'tower', 6);
    for (let z = 20; z <= 24; z++) for (let x = 12; x <= 14; x++) floor(x, z, 'plaza');
  }

  for (const [minX, maxX, minZ, maxZ] of [[11, 15, 12, 17], [34, 37, 28, 34]]) {
    for (let z = minZ; z <= maxZ; z++) for (let x = minX; x <= maxX; x++) floor(x, z, 'garden');
  }

  const roles = {};
  for (const {role} of api.resolve(world, terrain).roles.values()) roles[role] = (roles[role] ?? 0) + 1;
  if (roles['stone-bridge'] !== crossings.length || !roles.bandstand) throw new Error('水乡石桥或凉亭没有形成');
  return {seed: spec.seed, name: spec.name, world, terrain, initialWorld,
    camera: festival ? {target: [27.5, 1, 23.8], yaw: 317, pitch: 32, zoom: 3.7} :
      {target: [24, 1, 23], yaw: 322, pitch: 29, zoom: 2.65},
    time: festival ? 'dusk' : undefined,
    timeProgress: festival ? .67 : undefined,
    plan: {character: 'river', edits, unjoined: [], refused: 0, fellBack: false},
    audit: {removed: 0, skipped: [], roles, blocks: world.blocks.size, floors: world.floors.size,
      edges: world.edges.size, bridges: crossings, terrainColumns: initialWorld.terrainEdits.size}};
}
