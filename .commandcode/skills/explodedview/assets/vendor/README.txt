three.js 0.170.0 (MIT), tree-shaken and bundled with esbuild into three-ev.min.js (global EVTHREE).
Used pieces: WebGLRenderer, geometries, materials, OrbitControls, RoundedBoxGeometry, RoomEnvironment.
Rebuild: npm i three@0.170.0 esbuild; node build.mjs   (entry: ev3_entry.js). The page build inlines three-ev.min.js: the pages make no network requests.
