const timber = '#5d4437';
const stone = '#b6b5a5';
const tile = '#46504e';
const rebuiltDetails = new Set(['U09.vista-end', 'U10.corners', 'J05.roof-terrace', 'J10.dormers', 'D28.terrace-furniture']);
const adaptedRules = new WeakMap();

export function dwellingRules(rules) {
  if (!adaptedRules.has(rules)) adaptedRules.set(rules, rules.filter(rule => !rebuiltDetails.has(rule.id)));
  return adaptedRules.get(rules);
}

export function roofLift(distance, span, pitch, across, along, hardGable = false) {
  const corner = Math.max(0, Math.abs(along - .5) * 2 - .7) / .3;
  if (distance < 0) {
    return hardGable ? 0 : Math.min(.062, -distance * (.17 + .28 * corner));
  }
  return (hardGable ? -.16 : -.29) * pitch * span * across * (1 - across);
}

export function roofNormal(a, b, c, fallback) {
  const u = b.map((value, index) => value - a[index]);
  const v = c.map((value, index) => value - a[index]);
  const normal = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2],
    u[0] * v[1] - u[1] * v[0]];
  return Math.hypot(...normal) > 1e-9 ? normal : fallback;
}

export function tileEnds(mesh, point, from, to, color) {
  if (to - from < .08) return;
  const count = Math.ceil((to - from) * 9);
  mesh.with({color, ink: 'eave-tiles'}, () => {
    for (let i = 0; i < count; i++) {
      const offset = (to - from) / count;
      const left = from + (i + .08) * offset;
      const right = from + (i + .92) * offset;
      const upperLeft = point(left, .006, .005);
      const upperRight = point(right, .006, .005);
      const tip = point((left + right) / 2, .009, -.019);
      mesh.tri(upperRight, upperLeft, tip);
    }
  });
}

export function lattice(mesh, line, left, right, bottom, top, depth, style) {
  const x = t => left + (right - left) * t;
  const y = t => bottom + (top - bottom) * t;
  const beam = (a, b, c, d) => line(mesh, x(a), y(b), x(c), y(d), .014, depth);
  mesh.with({color: timber, ink: 'timber-lattice'}, () => {
    if (style === 'diamond') {
      beam(0, .5, .5, 1);
      beam(.5, 1, 1, .5);
      beam(1, .5, .5, 0);
      beam(.5, 0, 0, .5);
      beam(.5, 0, .5, 1);
    } else {
      for (const at of [1 / 3, 2 / 3]) {
        beam(at, 0, at, 1);
        beam(0, at, 1, at);
      }
    }
  });
}

export function entryFrame(mesh, roofColor, style, tilePattern) {
  const shop = style === 'shop';
  const half = shop ? .419 : .3;
  const height = shop ? .577 : .602;
  mesh.with({color: timber, ink: 'timber-portal'}, () => {
    for (const x of [-half, half]) {
      mesh.box([x - .019, .033, .043], [x + .019, height, .077]);
      mesh.box([x - .04, height - .072, .052], [x + .04, height - .021, .102]);
    }
    mesh.box([-half - .028, height - .008, .048], [half + .028, height + .037, .106]);
  });
  mesh.with({color: roofColor, pattern: tilePattern, ink: 'portal-awning'}, () => {
    const edge = half + .055;
    const rear = [height + .111, .015];
    const middle = [height + .06, .12];
    const front = [height + .04, .17];
    for (const [[ay, az], [by, bz]] of [[rear, middle], [middle, front]]) {
      mesh.quad([-edge, ay, az], [-edge, by, bz], [edge, by, bz], [edge, ay, az]);
    }
    mesh.box([-edge, front[0] - .018, front[1] - .012], [edge, ...front]);
  });
  mesh.with({color: stone, ink: 'portal-bases'}, () => {
    for (const x of [-half, half]) {
      mesh.box([x - .034, .022, .035], [x + .034, .08, .09]);
    }
  });
}

export function hardGable(mesh, sample, from, to, depth, plasterColor, plaster, shingles) {
  const outside = -depth + .035;
  const inside = -depth - .065;
  const steps = 4;
  for (let index = 0; index < steps; index++) {
    const left = from + (to - from) * index / steps;
    const right = from + (to - from) * (index + 1) / steps;
    const a = Math.max(0, sample(left)) + .076;
    const b = Math.max(0, sample(right)) + .076;
    mesh.with({color: plasterColor, pattern: plaster, ink: 'hard-gable-wall'}, () => {
      mesh.quad([left, 0, outside], [right, 0, outside], [right, b, outside], [left, a, outside]);
      mesh.quad([right, 0, inside], [left, 0, inside], [left, a, inside], [right, b, inside]);
      if (index === 0) mesh.quad([left, 0, inside], [left, 0, outside], [left, a, outside], [left, a, inside]);
      if (index === steps - 1) mesh.quad([right, 0, outside], [right, 0, inside], [right, b, inside], [right, b, outside]);
    });
    mesh.with({color: tile, pattern: shingles, ink: 'gable-tile-coping'}, () => {
      mesh.quad([left, a + .023, inside - .018], [left, a + .023, outside + .018],
        [right, b + .023, outside + .018], [right, b + .023, inside - .018]);
      mesh.quad([left, a, outside + .018], [right, b, outside + .018],
        [right, b + .023, outside + .018], [left, a + .023, outside + .018]);
      mesh.quad([right, b, inside - .018], [left, a, inside - .018],
        [left, a + .023, inside - .018], [right, b + .023, inside - .018]);
    });
  }
}

function tiledSlope(mesh, halfWidth, back, front, pattern) {
  const [backY, backZ] = back;
  const [frontY, frontZ] = front;
  mesh.with({color: tile, pattern, ink: 'grey-tile-slope'}, () => {
    mesh.quad([-halfWidth, backY, backZ], [-halfWidth, frontY, frontZ],
      [halfWidth, frontY, frontZ], [halfWidth, backY, backZ]);
    mesh.quad([halfWidth, backY - .023, backZ], [halfWidth, frontY - .023, frontZ],
      [-halfWidth, frontY - .023, frontZ], [-halfWidth, backY - .023, backZ]);
    mesh.box([-halfWidth, frontY - .033, frontZ - .008], [halfWidth, frontY, frontZ + .008]);
  });
  const count = Math.ceil(halfWidth * 20);
  mesh.with({color: '#545e58', pattern, ink: 'tile-joints'}, () => {
    for (let index = 0; index < count; index++) {
      const x = halfWidth * (2 * (index + .5) / count - 1);
      mesh.tri([x - .009, frontY + .003, frontZ], [x + .009, frontY + .003, frontZ],
        [x, backY + .013, backZ]);
    }
  });
}

export function tiledAwning(mesh, shingles) {
  tiledSlope(mesh, .4, [.063, 0], [-.085, .31], shingles);
  mesh.with({color: timber, ink: 'awning-brackets'}, () => {
    for (const x of [-.28, .28]) {
      mesh.box([x - .022, -.09, 0], [x + .022, -.059, .289]);
      mesh.tri([x - .022, -.21, 0], [x - .022, -.09, 0], [x - .022, -.09, .207]);
      mesh.tri([x + .022, -.09, .207], [x + .022, -.09, 0], [x + .022, -.21, 0]);
    }
  });
}

export function tiledStall(mesh, halfWidth, back, ridge, front, shingles) {
  mesh.with({color: timber, ink: 'market-posts'}, () => {
    for (const x of [-halfWidth + .055, halfWidth - .055]) {
      for (const [y, z] of [back, front]) {
        const post = z + (z < ridge[1] ? .055 : -.065);
        mesh.box([x - .024, 0, post - .024], [x + .024, y, post + .024]);
      }
    }
  });
  tiledSlope(mesh, halfWidth, ridge, front, shingles);
  // The other slope faces the rear of the stall.
  tiledSlope(mesh, halfWidth, back, ridge, shingles);
  mesh.with({color: tile, ink: 'market-tile-ridge'}, () =>
    mesh.box([-halfWidth, ridge[0] - .012, ridge[1] - .022], [halfWidth, ridge[0] + .022, ridge[1] + .022]));
}

export function timberShopFront(mesh, bars, center, low, width, height, depth) {
  const left = center - width / 2;
  const right = center + width / 2;
  mesh.with({color: timber, ink: 'paneled-storefront'}, () => {
    for (const x of [left, center, right]) bars(mesh, x, low, x, low + height, .027, depth);
    for (const y of [low, low + height * .38, low + height]) bars(mesh, left, y, right, y, .02, depth);
    for (const x of [left + width / 4, right - width / 4]) {
      bars(mesh, x, low + height * .38, x, low + height, .013, depth);
    }
  });
}

export function pavilionHeight(base, pitch, distance, point, outline) {
  const curve = .025 * Math.exp(-Math.max(0, distance) * 6);
  if (!point || !outline.length) return base + distance * pitch + curve;
  const nearest = Math.min(...outline.map(([x, z]) => Math.hypot(point[0] - x, point[1] - z)));
  return base + distance * pitch + curve + .13 * Math.max(0, 1 - nearest / .48) ** 2;
}

export function stoveVent(mesh, tilePattern) {
  mesh.with({color: '#746657', ink: 'stove-vent'}, () => {
    mesh.box([-.07, -.29, -.067], [.07, .065, .067]);
    for (const x of [-.052, .052]) {
      mesh.box([x - .013, .065, -.046], [x + .013, .103, .046]);
    }
  });
  mesh.with({color: '#45494a', pattern: tilePattern, ink: 'vent-tile'}, () => {
    mesh.box([-.088, .103, -.078], [.088, .133, .078]);
  });
}

export function towerEaves(mesh, radius, rise, roofColor, pattern) {
  const eave = radius * 1.38;
  mesh.with({color: timber, ink: 'tower-rail'}, () => {
    mesh.lathe([[radius * .75, .05], [radius * .70, rise * .53]], {segments: 8});
  });
  mesh.with({color: roofColor, pattern, ink: 'tower-tiled-eaves'}, () => {
    mesh.lathe([[radius, .015], [eave, .005], [eave, .052], [radius * 1.1, .079],
      [radius * .71, rise * .4]], {segments: 8});
    mesh.lathe([[radius * .62, rise * .53], [eave * .78, rise * .49],
      [eave * .79, rise * .56], [radius * .73, rise * .63], [radius * .45, rise * .79],
      [0, rise]], {segments: 8});
  });
}
