import { build } from 'esbuild';
import fs from 'node:fs';
await build({
  entryPoints: ['ev3_entry.js'], bundle: true, minify: true, format: 'iife', globalName: 'EVTHREE', target: 'es2020',
  outfile: 'three-ev.min.js', legalComments: 'none', logLevel: 'info',
});
const lic = fs.readFileSync('node_modules/three/LICENSE', 'utf8');
fs.writeFileSync('LICENSE-three.txt', 'three.js (https://threejs.org), version 0.170.0, bundled with esbuild (tree-shaken: renderer, geometries, materials, OrbitControls, RoundedBoxGeometry, RoomEnvironment).\n\n' + lic);
console.log('size', fs.statSync('three-ev.min.js').size);
