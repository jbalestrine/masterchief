const puppeteer = require('puppeteer');
(async ()=>{
  const browser = await puppeteer.launch({args:['--no-sandbox','--disable-setuid-sandbox']});
  const page = await browser.newPage();
  await page.goto('http://127.0.0.1:8080', {waitUntil:'networkidle2', timeout:10000});
  await page.screenshot({path:'logs/ui_screenshot.png', fullPage:true});
  console.log('saved logs/ui_screenshot.png');
  await browser.close();
})();
