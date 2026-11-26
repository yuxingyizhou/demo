const timber = '#5d4437';
const stone = '#b6b5a5';

export function roofLift(distance, span, pitch, across, along) {
  const corner = Math.max(0, Math.abs(along - .5) * 2 - .7) / .3;
  if (distance < 0) {
    return Math.min(.105, -distance * (.27 + .75 * corner));
  }
  return -.29 * pitch * span * across * (1 - across);
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

export function pavilionHeight(base, pitch, distance, point, outline) {
  const curve = .025 * Math.exp(-Math.max(0, distance) * 6);
  if (!point || outline.length !== 4) return base + distance * pitch + curve;
  const nearest = Math.min(...outline.map(([x, z]) => Math.hypot(point[0] - x, point[1] - z)));
  return base + distance * pitch + curve + .106 * Math.max(0, 1 - nearest / .5) ** 2;
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
