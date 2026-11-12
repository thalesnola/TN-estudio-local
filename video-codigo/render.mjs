import { chromium } from 'playwright-core';
import { spawn } from 'node:child_process';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
const a = process.argv.slice(2), pos = a.filter(x => !x.startsWith('--') && !(a[a.indexOf(x)-1]||'').startsWith('--'));
const opt = (k, d) => { const i = a.indexOf('--' + k); return i >= 0 ? a[i+1] : d; };
const [html, out] = pos;
if (!html || !out) { console.error('uso: render.mjs anim.html saida.mp4 [--fps 30] [--audio f] [--w 1920 --h 1080]'); process.exit(1); }
const fps = +opt('fps', 30), W = +opt('w', 1920), H = +opt('h', 1080), audio = opt('audio');
const br = await chromium.launch({ channel: 'msedge' });
const pg = await br.newPage({ viewport: { width: W, height: H } });
await pg.goto(pathToFileURL(resolve(html)).href);
await pg.evaluate(() => document.fonts.ready);
await pg.waitForFunction(() => typeof window.__seek === 'function' && window.__duration > 0, null, { timeout: 30000 });
const dur = await pg.evaluate(() => window.__duration), n = Math.round(dur * fps);
const args = ['-y', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-'];
if (audio) args.push('-i', audio, '-af', `afade=t=out:st=${Math.max(0, dur-1)}:d=1`, '-t', String(dur));
args.push('-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-movflags', '+faststart', ...(audio ? ['-c:a', 'aac'] : []), out);
const ff = spawn('ffmpeg', args, { stdio: ['pipe', 'ignore', 'inherit'] });
for (let i = 0; i < n; i++) {
  await pg.evaluate(async t => { const r = window.__seek(t); if (r instanceof Promise) await r; }, i / fps);
  await pg.evaluate(() => new Promise(r => requestAnimationFrame(() => r())));
  const png = await pg.screenshot({ type: 'png' });
  if (!ff.stdin.write(png)) await new Promise(r => ff.stdin.once('drain', r));
}
ff.stdin.end(); await new Promise(r => ff.on('close', r)); await br.close();
console.log(`ok: ${out} (${n} quadros, ${dur}s)`);
