// Extrae de hub.blacksip.com/project-updates el reporte de la semana anterior (se reporta jueves/viernes).
// Uso:  node scripts/hub-updates.mjs [--week=YYYY-MM-DD]   (--week = lunes de la semana a leer)
// Primer uso: abre Chrome, inicia sesión tú mismo. La sesión queda en .hub-profile/. No cierres la ventana.
// Salida: scripts/out/hub-<lunes>.json y .md (insumo del bloque 3 del Scrum of Scrum).
// Lee la vista de tarjetas: cada <div data-card> ya trae estado, avance y el texto de la semana.
import { createRequire } from 'node:module';
import { mkdirSync, writeFileSync } from 'node:fs';
// playwright se resuelve desde la carpeta de trabajo (npm i playwright ahí), no desde la del skill.
const { chromium } = createRequire(`${process.cwd()}/`)('playwright');

const URL = 'https://hub.blacksip.com/project-updates';
const ESTADO = { on_track: 'Según lo planeado', at_risk: 'En riesgo', deviated: 'Con desviación', suspended: 'Suspendido', completed: 'Completado', '': 'Sin reporte' };

// Lunes de la semana anterior, o --week=YYYY-MM-DD.
const arg = process.argv.find((a) => a.startsWith('--week='))?.slice(7);
const prev = arg ? new Date(arg + 'T12:00:00') : (() => {
  const d = new Date(); d.setHours(12, 0, 0, 0);
  d.setDate(d.getDate() - ((d.getDay() + 6) % 7) - 7);
  return d;
})();
const wkIso = prev.toISOString().slice(0, 10);

const ctx = await chromium.launchPersistentContext('.hub-profile', {
  channel: 'chrome', headless: false,
  ignoreDefaultArgs: ['--enable-automation'],
  args: ['--disable-blink-features=AutomationControlled'],
});
const page = ctx.pages()[0] ?? await ctx.newPage();
await page.goto(`${URL}?week=${wkIso}`);
// Si redirige a /login, espera hasta 5 min a que inicies sesión a mano.
await page.waitForURL('**/project-updates*', { timeout: 300_000 });
await page.getByTitle('Vista de tarjetas').click();
// Visibles = no ocultas por el filtro (los proyectos finalizados sin reporte vienen con display:none).
const tarjetas = page.locator('div[x-ref="grid"] > div[data-card]:visible');
await tarjetas.first().waitFor({ timeout: 60_000 });

const lista = await tarjetas.evaluateAll((cards) => cards.map((c) => {
  const txt = (sel) => c.querySelector(sel)?.textContent.replace(/\s+/g, ' ').trim() ?? '';
  const pres = [...c.querySelectorAll('pre')];
  return {
    id: c.getAttribute('wire:click')?.match(/project:\s*(\d+)/)?.[1],
    cliente: txt('p.truncate'),
    proyecto: c.querySelector('h3')?.title ?? txt('h3'),
    pm: txt('p.inline-flex'),
    estado: c.dataset.status,
    avance: txt('span.text-gray-600'),
    reporta: txt('p.mt-1.text-xs.text-gray-400:not(.inline-flex)'), // "Quién · 01 oct. 2026"
    texto: pres[0]?.textContent.trim() ?? '',
    proximos: pres.find((p) => p.className.includes('mt-0.5'))?.textContent.trim() ?? '',
  };
}));
for (const r of lista) r.estado = ESTADO[r.estado] ?? r.estado;
await ctx.close();

mkdirSync('scripts/out', { recursive: true });
writeFileSync(`scripts/out/hub-${wkIso}.json`, JSON.stringify(lista, null, 2));

const groupBy = (a, f) => a.reduce((o, x) => ((o[f(x)] ??= []).push(x), o), {}); // Node 20 no trae Object.groupBy
const cut = (s, n) => s.replace(/\s+/g, ' ').replace(/\|/g, '/').slice(0, n);
const alerta = lista.filter((r) => /desviaci|riesgo/i.test(r.estado));
const sin = lista.filter((r) => r.estado === 'Sin reporte');
const conteo = Object.entries(groupBy(lista, (r) => r.estado)).map(([k, v]) => `${k}: ${v.length}`).join(' · ');
const md = [`# Hub · semana ${wkIso}`, '', conteo, '',
  '## En alerta', '', '| Cliente · Proyecto | PM | Estado | Avance | Reporte de la semana | Próximos pasos |', '|---|---|---|---|---|---|',
  ...alerta.map((r) => `| ${r.cliente} · ${r.proyecto} | ${r.pm} | ${r.estado} | ${r.avance} | ${cut(r.texto, 400)} | ${cut(r.proximos, 250)} |`),
  '', `## Sin reporte (${sin.length})`, '',
  ...Object.entries(groupBy(sin, (r) => r.pm)).map(([pm, v]) => `- **${pm}**: ${v.map((r) => `${r.cliente} · ${r.proyecto}`).join('; ')}`)];
writeFileSync(`scripts/out/hub-${wkIso}.md`, md.join('\n') + '\n');
console.log(`Semana ${wkIso}: ${lista.length} tarjetas. ${conteo}\nListo: scripts/out/hub-${wkIso}.{json,md}`);
