const esbuild = require('esbuild');

esbuild.build({
  entryPoints: ['src/chapter-list.tsx'],
  bundle: true,
  outfile: 'dist/chapter-list.js',
  format: 'esm',
  target: 'es2020',
  loader: {
    '.tsx': 'tsx'
  },
  jsx: 'automatic',
  minify: true,
  sourcemap: true
}).catch(() => process.exit(1));
