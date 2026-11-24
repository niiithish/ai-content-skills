const p = require('puppeteer-core'); const fs = require('fs');
const tpl = fs.readFileSync(require('path').join(__dirname, 'address-bar.html'), 'utf8'); const url = 'trymysa.store';
const rows = ['qwertyuiop', 'asdfghjkl', 'zxcvbnm.'];
const N = +process.argv[2] || 43, T0 = 2, T1 = 30;      // typed over frames 2-30, then hold
(async () => {
  const b = await p.launch({executablePath: '/usr/bin/chromium', headless: true, args: ['--hide-scrollbars']});
  const pg = await b.newPage(); await pg.setViewport({width: 1080, height: 1920});
  await pg.setContent(tpl.replace(/TYPED|SUGOP|CARETOP|KROW\d/g, ''), {waitUntil: 'networkidle0'});
  for (let f = 0; f < N; f++) {
    const n = Math.max(0, Math.min(url.length, Math.floor((f - T0) * url.length / (T1 - T0)) + 1));
    const last = f >= T0 && f <= T1 ? url[n - 1] : '';
    const kr = rows.map(r => [...r].map(c => `<div class="k${c === last ? ' on' : ''}">${c}</div>`).join(''));
    const h = tpl.replace('TYPED', url.slice(0, n)).replace('SUGOP', n >= 4 ? '1' : '0')
      .replace('CARETOP', (f > T1 && Math.floor(f / 8) % 2) ? '0' : '1')
      .replace('KROW1', kr[0]).replace('KROW2', kr[1]).replace('KROW3', kr[2]);
    await pg.setContent(h, {waitUntil: 'networkidle0'}); await pg.evaluate(() => document.fonts.ready);
    await pg.screenshot({path: `f218v2/${String(f).padStart(3, '0')}.png`});
  }
  await b.close();
})();