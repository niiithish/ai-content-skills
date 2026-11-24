const p = require('puppeteer-core');
(async () => {
  const b = await p.launch({executablePath: '/usr/bin/chromium', headless: true, args: ['--hide-scrollbars']});
  const pg = await b.newPage();
  await pg.setViewport({width: 899, height: 1598, deviceScaleFactor: 1080 / 899});
  for (let i = 2; i < process.argv.length; i += 2) {
    await pg.goto('file://' + process.argv[i], {waitUntil: 'networkidle0'});
    await pg.evaluate(() => document.fonts.ready);
    console.log(process.argv[i], await pg.evaluate(() => [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family + ' ' + f.weight).join(', ')));
    await pg.screenshot({path: process.argv[i + 1], clip: {x: 0, y: 0, width: 899, height: 1598}});
  }
  await b.close();
})();