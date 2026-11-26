const ink = '#353733';
const sash = '#67473c';
const lining = '#e4d7bb';
const bamboo = '#a88756';

export function outfit(sample, child) {
  if (child) return sample < .48 ? 'child-wrap' : 'child-tunic';
  if (sample < .29) return 'jacket';
  if (sample < .56) return 'skirt';
  if (sample < .79) return 'apron';
  return 'reed-hat';
}

// Parts sit in the original rig's local coordinates. The body faces positive Z.
export function residentMeshes(builder, tools, person, rig) {
  const {profile, ball, scale} = tools;
  const {top, bottom, skin, hair, girth, jiangnan: style} = person;
  const winter = person.hat === 'bobble';
  const skirt = style === 'skirt' || (winter && person.dress);
  const apron = style === 'apron';
  const guard = style === 'guard';
  const shortSleeves = !winter && (apron || style === 'reed-hat' || style === 'child-tunic');
  const wrap = style !== 'skirt';
  const draw = (mesh, label, color, callback) => mesh.with({ink: label, color}, callback);
  const body = builder();
  const jacket = [[.051, .167], [.06, .219], [.061, rig.shoulderY], [.033, .283], [0, .292]];
  const lapelPoint = (x, y) => {
    const next = jacket.findIndex(([, height]) => height >= y);
    const [r0, y0] = jacket[next - 1];
    const [r1, y1] = jacket[next];
    const r = r0 + (r1 - r0) * (y - y0) / (y1 - y0);
    return [x, y, Math.sqrt(Math.max(0, r * r - x * x)) + .009];
  };
  const lapel = points => {
    for (let i = 1; i < points.length; i++) {
      const [x0, y0] = points[i - 1];
      const [x1, y1] = points[i];
      body.quad(lapelPoint(x0 + .005, y0), lapelPoint(x0 - .005, y0),
        lapelPoint(x1 - .005, y1), lapelPoint(x1 + .005, y1));
    }
  };

  body.at(scale(girth, 1, .82), () => {
    draw(body, 'lower-garment', skirt ? bottom : top, () => {
      const hem = skirt ? .048 : .101;
      const width = skirt ? .087 : .065;
      profile(body, [[0, hem], [width, hem], [width - .004, hem + .017],
        [.051, .177]], {segments: 8, crease: .75});
    });
    draw(body, 'jacket', top, () => profile(body, jacket, {segments: 8}));
    draw(body, 'waist-sash', sash, () => profile(body, [[.053, .161], [.054, .179]], {segments: 8}));

    // The overlapping collar is a raised fabric strip with a visible edge at town scale.
    draw(body, 'layered-collar', lining, () => {
      if (wrap) {
        lapel([[.022, .281], [.003, .252], [-.013, .236]]);
        lapel([[-.022, .281], [-.005, .254], [.018, .228], [.037, .204]]);
      } else {
        for (const x of [-.024, .024]) lapel([[x, .281], [x, .252], [x, .218]]);
      }
    });
    if (apron) draw(body, 'work-apron', '#bdad8f', () => {
      body.quad([-.034, .173, .063], [-.048, .09, .077], [.047, .09, .077], [.034, .173, .063]);
    });
    if (skirt) draw(body, 'skirt-pleats', pleatColor(bottom), () => {
      for (const x of [-.05, -.024, .024, .05]) {
        const z = Math.sqrt(.084 ** 2 - x ** 2);
        body.tri([x, .052, z], [x + .006, .052, z - .002], [x * .53, .161, .049]);
      }
    });
  });

  const {headY, head} = rig;
  draw(body, 'head', skin, () => ball(body, 0, headY, 0, head * .93, head, head, 8, 5));
  draw(body, 'hair', hair, () => {
    profile(body, [[head * 1.10, headY + head * .16], [head * .96, headY + head * .62],
      [head * .58, headY + head * .91], [0, headY + head * 1.05]], {segments: 10});
    if (style === 'skirt' || style === 'child-wrap') {
      ball(body, 0, headY + head * .83, -head * .68, head * .37, head * .42, head * .38, 7, 4);
    }
  });
  if (person.hat === 'straw') reedHat(body, profile, headY + head * .5, head * 1.85);
  if (person.hat === 'helmet' || person.hat === 'cap' || winter) draw(body, 'cloth-cap', guard ? ink : person.hatColor, () => profile(body,
    [[head * 1.08, headY + head * .48], [head * 1.04, headY + head],
      [head * .54, headY + head * 1.15], [0, headY + head * 1.15]], {segments: 8}));

  function arm() {
    const mesh = builder();
    const cuff = shortSleeves ? -.063 : -.086;
    draw(mesh, 'sleeve', top, () => profile(mesh, [[.017, cuff], [.021, cuff + .013],
      [.019, -.006], [.013, .012]], {segments: 6}));
    draw(mesh, 'cuff', lining, () => profile(mesh, [[.0175, cuff], [.018, cuff + .008]], {segments: 6}));
    draw(mesh, 'hand', skin, () => ball(mesh, 0, -.093, 0, .012, .02, .012, 6, 4));
    if (shortSleeves) draw(mesh, 'forearm', skin, () => profile(mesh,
      [[.011, -.087], [.014, cuff]], {segments: 6}));
    return mesh.build();
  }

  function leg() {
    const mesh = builder();
    draw(mesh, 'trousers', bottom, () => profile(mesh,
      [[.017, -.101], [.021 * girth, -.072], [.023 * girth, 0]], {segments: 6}));
    draw(mesh, 'cloth-shoe', ink, () => mesh.box([-.019, -rig.leg, -.021], [.019, -.099, .031]));
    return mesh.build();
  }

  const arms = arm();
  const legs = leg();
  return {body: body.build(), armL: arms, armR: arms, legL: legs, legR: legs};
}

function pleatColor(color) {
  const value = Number.parseInt(color.slice(1), 16);
  const rgb = [16, 8, 0].map(shift => Math.round(((value >> shift) & 255) * .78));
  return '#' + rgb.map(channel => channel.toString(16).padStart(2, '0')).join('');
}

export function reedHat(mesh, profile, base, radius) {
  mesh.with({ink: 'bamboo-brim', color: bamboo}, () => profile(mesh,
    [[0, base + .014], [radius, base - .012], [radius, base - .007],
      [radius * .56, base + .016], [radius * .24, base + .039],
      [0, base + .048]], {segments: 10, crease: .55}));
  mesh.with({ink: 'hat-binding', color: '#6d543b'}, () => profile(mesh,
    [[radius * .96, base - .008], [radius * .97, base - .003]], {segments: 10}));
}
