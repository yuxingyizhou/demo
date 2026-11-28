const timber = '#6e392e';
const darkWood = '#483833';
const stone = '#aca79c';
const tile = '#37474a';
const ripplePattern = 41;

export function festivalLantern(mesh, y, radius, glow) {
  mesh.with({color: '#eb6036', pattern: glow, ink: 'festival-lantern'}, () => {
    mesh.lathe([[radius * .55, y], [radius, y + radius * .6], [radius, y + radius * 1.35],
      [radius * .55, y + radius * 1.9]], {segments: 10, capTop: true, capBottom: true});
  });
  mesh.with({color: '#c89851', ink: 'lantern-rims'}, () => {
    mesh.lathe([[radius * .61, y - .008], [radius * .61, y + .014]], {segments: 10});
    mesh.lathe([[radius * .61, y + radius * 1.88], [radius * .61, y + radius * 2.04]], {segments: 10});
    mesh.box([-.012, y - .15, -.012], [.012, y, .012]);
    mesh.box([-.009, y + 2 * radius, -.009], [.009, y + 2 * radius + .10, .009]);
  });
}

export function lanternRipples(mesh, water, x, z, direction = 1, scale = 1) {
  const color = ['#e89957', '#c8804e', '#e9aa69', '#ae6947', '#c48b58', '#99644e'];
  const shift = [0, -.023, .019, .045, -.038, .01];
  mesh.with({pattern: ripplePattern, ink: 'lantern-water-glints'}, () => {
    for (let step = 0; step < color.length; step++) {
      const distance = (step + .5) * .17 * scale;
      const cx = x + shift[step] * scale;
      const cz = z + direction * distance;
      const half = (.077 + step * .018) * scale;
      const depth = .022 * scale;
      mesh.setColor(color[step]);
      mesh.quad([cx - half, water, cz], [cx - half * .55, water, cz + depth],
        [cx + half, water, cz + depth * .6], [cx + half * .65, water, cz - depth]);
    }
  });
}

export function boatLantern(mesh, glow, big = false) {
  const length = big ? .49 : .39;
  mesh.with({color: darkWood, ink: 'boat-lamp-stanchion'}, () => {
    mesh.box([-.123, .044, -.018], [-.102, length, .018]);
    mesh.box([-.123, length - .026, -.02], [.04, length + .003, .02]);
  });
  festivalLantern(mesh, big ? .19 : .142, big ? .106 : .077, glow);
  lanternRipples(mesh, .026, .20, -.11, -1, big ? .72 : .56);
}

export function marketLanterns(mesh, glow) {
  for (const x of [-.26, .26]) {
    for (const z of [-.285, .285]) {
      mesh.translate(x, 0, z);
      festivalLantern(mesh, .365, .095, glow);
      mesh.translate(-x, 0, -z);
    }
  }
}

function ridgeRoof(mesh, halfLength, depth, foot, rise, shingles, turn = .08) {
  const row = [0, .48, 1];
  const width = Math.max(2, Math.ceil(halfLength * 12));
  const point = (index, across) => {
    const along = 2 * index / width - 1;
    const slope = Math.abs(across);
    const sweptTip = turn * Math.max(0, (Math.abs(along) - .73) / .27) * slope;
    return [halfLength * along, foot + rise * (1 - slope) ** 1.26 + sweptTip, depth * across];
  };
  mesh.with({pattern: shingles, ink: 'curved-roof-tiles'}, () => {
    for (let bay = 0; bay < width; bay++) {
      mesh.setColor(bay % 3 === 0 ? '#435253' : tile);
      for (const steps of [[-1, -.48, 0], row]) {
        for (let course = 0; course < 2; course++) {
          const [back, front] = steps.slice(course, course + 2);
          mesh.quad(point(bay, back), point(bay, front), point(bay + 1, front), point(bay + 1, back));
        }
      }
    }
    mesh.box([-halfLength - .017, foot + rise - .018, -.028], [halfLength + .017, foot + rise + .041, .028]);
  });
  mesh.with({color: darkWood, ink: 'eave-fascia'}, () => {
    for (const across of [-1, 1]) {
      for (let index = 0; index < width; index++) {
        const a = point(index, across), b = point(index + 1, across);
        const drop = ([x, y, z]) => [x, y - .053, z];
        const face = [drop(a), drop(b), b, a];
        mesh.quad(...(across > 0 ? face : face.reverse()));
      }
    }
  });
}

export function coveredBridge(mesh, span, level, hump, water, materials) {
  const eave = level + 1.44;
  const bays = Math.max(3, Math.round(span));
  const half = span * .5 + .18;
  const width = .55;
  mesh.with({color: timber, pattern: materials.wood, ink: 'bridge-gallery-timber'}, () => {
    for (const z of [-width, width]) {
      mesh.box([-half, eave - .15, z - .035], [half, eave - .04, z + .035]);
      for (let bay = 0; bay <= bays; bay++) {
        const alpha = (.23 + bay * (span - .46) / bays) / span;
        const x = (alpha - .5) * span;
        const foot = level + hump * Math.sin(Math.PI * alpha);
        mesh.box([x - .045, foot, z - .045], [x + .045, eave, z + .045]);
        mesh.box([x - .12, eave - .205, z - .056], [x + .12, eave - .139, z + .056]);
      }
    }
  });
  ridgeRoof(mesh, half, width + .22, eave, .34, materials.tiles);
  for (const z of [-.51, .51]) {
    for (let bay = 0; bay < bays; bay++) {
      const x = (bay + .5 - bays / 2) * (span - .46) / bays;
      mesh.translate(x, 0, z);
      festivalLantern(mesh, eave - .44, .126, materials.glow);
      mesh.translate(-x, 0, -z);
      const side = Math.sign(z);
      lanternRipples(mesh, water + .018, x, side * .67, side);
    }
  }
}

export function gatePost(mesh, height, materials) {
  mesh.with({color: stone, pattern: materials.stone, ink: 'gate-stone-foot'}, () => {
    mesh.box([-.19, 0, -.19], [.19, .12, .19]);
    mesh.box([-.14, .12, -.14], [.14, .28, .14]);
  });
  mesh.with({color: timber, pattern: materials.wood, ink: 'gate-pillar'}, () =>
    mesh.box([-.103, .24, -.103], [.103, height + .05, .103]));
}

export function gateRoof(mesh, materials) {
  const levels = [[-1.5, .66, 1.28, .26], [0, 1.19, 1.85, .41], [1.5, .66, 1.28, .26]];
  for (const [x, width, height, rise] of levels) {
    mesh.translate(x, 0, 0);
    mesh.with({color: timber, pattern: materials.wood, ink: 'gate-beams'}, () => {
      mesh.box([-width, height - .22, -.118], [width, height - .085, .118]);
      mesh.box([-width * .76, height - .095, -.156], [width * .76, height, .156]);
    });
    ridgeRoof(mesh, width, x === 0 ? .46 : .38, height, rise, materials.tiles, .125);
    if (x !== 0) festivalLantern(mesh, height - .61, .135, materials.glow);
    mesh.translate(-x, 0, 0);
  }
  mesh.with({color: '#31524d', ink: 'lacquered-gate-plaque'}, () => {
    mesh.box([-.41, 1.38, -.148], [.41, 1.64, .148]);
  });
  mesh.with({color: '#c5a161', ink: 'gate-plaque-border'}, () => {
    for (const z of [-.153, .153]) {
      mesh.box([-.42, 1.381, z - .008], [.42, 1.405, z + .008]);
      mesh.box([-.42, 1.619, z - .008], [.42, 1.643, z + .008]);
    }
  });
}

export function pagoda(mesh, materials, storeys = 4) {
  mesh.with({color: stone, pattern: materials.stone, ink: 'octagonal-stone-plinth'}, () => {
    mesh.lathe([[.82, 0], [.82, .1], [.76, .17], [.76, .25], [.68, .28]], {segments: 8});
  });
  for (let floor = 0; floor < storeys; floor++) {
    const r = .66 - floor * .096;
    const y = .26 + floor * .77;
    mesh.with({color: floor ? '#d1b49c' : '#b5907a', pattern: materials.stone, ink: 'pagoda-brick'}, () => {
      mesh.lathe([[r, y], [r, y + .61]], {segments: 8});
    });
    mesh.with({color: timber, pattern: materials.wood, ink: 'pagoda-framing'}, () => {
      mesh.lathe([[r + .035, y + .055], [r + .035, y + .12], [r, y + .16]], {segments: 8});
      mesh.lathe([[r + .01, y + .49], [r + .09, y + .56], [r + .15, y + .61]], {segments: 8});
      for (let face = 0; face < 8; face++) {
        mesh.rotateY((face + .5) * Math.PI / 4);
        const front = r * Math.cos(Math.PI / 8) + .013;
        mesh.box([-.1, y + .16, front - .022], [.1, y + .49, front]);
        mesh.rotateY(-(face + .5) * Math.PI / 4);
      }
    });
    mesh.with({color: '#d3a251', pattern: materials.glow, ink: 'pagoda-window-light'}, () => {
      for (let face = 0; face < 8; face++) {
        mesh.rotateY((face + .5) * Math.PI / 4);
        const front = r * Math.cos(Math.PI / 8) + .02;
        mesh.box([-.073, y + .21, front - .01], [.073, y + .431, front]);
        mesh.rotateY(-(face + .5) * Math.PI / 4);
      }
    });
    mesh.with({color: tile, pattern: materials.tiles, ink: 'pagoda-eaves'}, () => {
      const last = floor === storeys - 1;
      const upper = last ? .065 : r - .096;
      mesh.lathe([[r + .24, y + .636], [r + .24, y + .687], [r + .13, y + .66],
        [r + .01, y + .71], [upper, y + (last ? 1.10 : .82)]], {segments: 8});
    });
  }
  const height = .77 * (storeys - 4);
  mesh.with({color: '#b39b5b', ink: 'pagoda-finial'}, () => {
    mesh.lathe([[.084, 3.63 + height], [.084, 3.71 + height], [.047, 3.78 + height],
      [.047, 3.93 + height], [.008, 4.05 + height]], {segments: 8, capTop: true});
  });
}
