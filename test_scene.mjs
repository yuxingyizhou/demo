import assert from 'node:assert/strict';
import {readdirSync} from 'node:fs';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import {navAudit} from './districts.mjs';
import {isLanternTown, lanternLandmarks} from './water-town.mjs';

const assets = resolve(process.argv[2] || 'dist', 'assets');
const load = name => import(pathToFileURL(resolve(assets, name)));
const files = readdirSync(assets);
const engine = await load(files.find(name => name.startsWith('field-basketball.scenario-') && name.endsWith('.js')));
const save = await load(files.find(name => name.startsWith('save-') && name.endsWith('.js')));
const {PRESETS, presetPlan, nativeSceneAPI: api} = await load('jiangnan-scene.mjs');

for (const preset of PRESETS) {
  const {seed, plan, audit, world, terrain, initialWorld} = presetPlan(preset.id, api);
  assert.equal(plan.unjoined.length, 0);
  assert.equal(plan.refused, 0);
  assert(!plan.fellBack);
  assert.equal(audit.skipped.length, 0);

  let replay = initialWorld ?? {version: 1, seed, terrainGen: 2, nextSeq: 1,
    blocks: new Map(), floors: new Map(), edges: new Map()};
  for (const edit of plan.edits) {
    assert(api.can(replay, terrain, edit).ok);
    replay = api.apply(replay, terrain, edit);
  }
  assert.deepEqual(replay, world);
  const encoded = save.r(world);
  const decoded = save.n(encoded);
  assert(decoded.ok);
  assert.deepEqual(decoded.world, world);
  assert.deepEqual(api.terrainFromWorld(decoded.world).height, terrain.height);

  const shape = api.resolve(world, terrain);
  const dressing = engine.tt(shape);
  const nav = navAudit(dressing.nav);
  const lamps = dressing.props.filter(prop => prop.type === 'lamp').length;
  assert(nav.main / nav.navTotal >= .8);
  assert(lamps > 0);
  assert(dressing.actors.some(actor => actor.type === 'resident'));

  if (preset.id === 'canal') {
    assert.equal(audit.roles['stone-bridge'], 3);
    assert.equal(audit.roles.bandstand, 1);
    assert(audit.roles.willow >= 8);
    assert.equal(audit.roles.jetty, 4);
    assert.equal(dressing.actors.filter(actor => actor.type === 'rowboat' && actor.params.canal).length, 4);
    assert(!dressing.actors.some(actor => actor.type === 'sailboat' ||
      actor.type === 'ship-call' && actor.variant !== 'barge'));
    const roofs = shape.features.filter(feature => feature.type === 'roof');
    const hardGables = roofs.filter(roof => roof.variant === 'gable');
    assert(hardGables.length > roofs.length / 2);
    assert(roofs.length > hardGables.length);
    assert(roofs.every(roof => roof.variant === 'gable' || roof.variant === 'stepped-gable'));
    const windows = shape.features.filter(feature => feature.type === 'window');
    assert(windows.filter(window => window.variant === 'river-lattice').length >= 15);
    assert(windows.every(window => ['square', 'tall', 'shopfront', 'river-lattice'].includes(window.variant)));
    assert(!shape.features.some(feature => ['corner-oriel', 'dormer', 'balcony'].includes(feature.type) ||
      feature.type === 'chimney' && feature.variant !== 'plain'));
    assert(!dressing.props.some(prop => prop.type === 'maypole' || prop.type === 'terrace-set'));
    assert.equal(nav.mainEntrancesReachable, nav.mainEntrances);
    assert(encoded.length < 6000);
  }

  if (preset.id === 'lantern') {
    assert(isLanternTown(decoded.world));
    assert.equal(audit.roles['stone-bridge'], 3);
    assert.equal(audit.roles.jetty, 4);
    assert.equal(dressing.actors.filter(actor => actor.type === 'rowboat' && actor.params.festival).length, 4);
    assert.equal(dressing.actors.filter(actor => actor.type === 'rower' && actor.params.festival).length, 1);
    const activities = dressing.actors.filter(actor => actor.type === 'festival-market');
    for (const kind of ['turning', 'wash', 'riddles', 'seller', 'guest', 'watch']) {
      assert(activities.some(actor => actor.variant === kind), kind);
    }
    assert(activities.filter(actor => actor.variant === 'child' && actor.params.walk > 1).length >= 3);
    assert(!dressing.props.some(prop => ['bunting', 'cafe-table', 'flag'].includes(prop.type)));
    const earlierBlocks = new Map(world.blocks);
    const newDock = save.U(27, 0, 26);
    earlierBlocks.set(save.U(26, 0, 30), earlierBlocks.get(newDock));
    earlierBlocks.delete(newDock);
    const earlierDressing = engine.tt(api.resolve({...world, blocks: earlierBlocks}, terrain));
    assert(earlierDressing.actors.some(actor => actor.type === 'rower' && actor.params.festival));
    assert(!dressing.actors.some(actor => actor.type === 'sailboat' ||
      actor.type === 'ship-call' && actor.variant !== 'barge'));
    const builder = engine.ht();
    const parts = engine.gt();
    const rangeAt = ({x, z}, level, axis) => {
      const structure = shape.structures.get(shape.structureAt.get(save.U(x, level, z)));
      assert(structure);
      const {position} = builder.build(structure, shape, parts).mesh;
      const coordinates = position.filter((_, index) => index % 3 === axis);
      return Math.max(...coordinates) - Math.min(...coordinates);
    };
    assert(rangeAt(lanternLandmarks.bridge, 0, 1) > 2.3, 'a timber roof rises over the stone deck');
    const {gate} = lanternLandmarks;
    assert(rangeAt({x: gate.x, z: gate.posts[0]}, 1, 2) > 4, 'the gate model spans all three passages');
    assert(rangeAt(lanternLandmarks.tower, 1, 1) > 3.9, 'the pagoda reaches its finial');
    assert.equal(nav.mainEntrancesReachable, nav.mainEntrances);
  }

  console.log(JSON.stringify({id: preset.id, seed, edits: plan.edits.length, ...audit, ...nav, lamps}));
}
