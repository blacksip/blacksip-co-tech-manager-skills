// Cruza scripts/out/hub-<lunes>.json con asignacion-proyectos-tm.md.
// Uso:  node scripts/cruce-hub.mjs --info              (semana actual y anterior)
//       node scripts/cruce-hub.mjs [--week=YYYY-MM-DD]  (por defecto, la semana anterior)
// Salida: scripts/out/cruce-<lunes>.{md,json}
import { existsSync, readFileSync, writeFileSync } from 'node:fs';

const arg = (k) => process.argv.find((a) => a.startsWith(`--${k}=`))?.slice(k.length + 3);
const monday = (d) => { d = new Date(d); d.setHours(12, 0, 0, 0); d.setDate(d.getDate() - ((d.getDay() + 6) % 7)); return d; };
const addDays = (d, n) => { d = new Date(d); d.setDate(d.getDate() + n); return d; };
const iso = (d) => d.toISOString().slice(0, 10);
const isoWeek = (d) => {
  const t = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
  t.setUTCDate(t.getUTCDate() + 4 - (t.getUTCDay() || 7));
  return Math.ceil(((t - Date.UTC(t.getUTCFullYear(), 0, 1)) / 864e5 + 1) / 7);
};
const semana = (m) => `semana ${isoWeek(m)} (${iso(m)} a ${iso(addDays(m, 6))})`;

const hoy = new Date(); hoy.setHours(12, 0, 0, 0);
const estaSemana = monday(hoy), pasada = addDays(estaSemana, -7);
if (process.argv.includes('--info')) {
  console.log(`Hoy: ${iso(hoy)}\nEsta semana: ${semana(estaSemana)}\nSemana pasada: ${semana(pasada)}`);
  process.exit(0);
}

const wk = arg('week') ?? iso(pasada);
const hub = JSON.parse(readFileSync(`scripts/out/hub-${wk}.json`, 'utf8'));

const norm = (s) => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();

// --- parseo de asignacion-proyectos-tm.md ---
const ASIG = ['agendas/asignacion-proyectos-tm.md', 'asignacion-proyectos-tm.md'].find((f) => existsSync(f)); // agendas/ (repo reorganizado) o la raíz (estructura anterior)
if (!ASIG) { console.error('No encuentro asignacion-proyectos-tm.md (ni en agendas/ ni en la raíz). Ejecuta desde la carpeta de trabajo del Scrum of Scrum.'); process.exit(1); }
const md = readFileSync(ASIG, 'utf8');
const sec = (t) => md.split('\n## ').find((s) => s.startsWith(t)) ?? '';
const asignados = [];
for (const l of sec('Tech Managers').split('\n').filter((l) => l.startsWith('| **'))) {
  const c = l.split('|').map((x) => x.trim());
  const tm = c[1].replace(/\*\*/g, '').replace(/\(.*?\)/g, '').trim();
  [[c[2], 'Proyecto'], [c[3], 'Evolución']].forEach(([cell, tipo]) => {
    if (cell === '—') return;
    for (const raw of cell.split('<br>')) {
      const nombre = raw.replace(/\*\(.*?\)\*/g, '').trim();
      if (nombre) asignados.push({ tm, tipo, nombre, porConfirmar: /por confirmar/.test(raw), fueraHub: /fuera del Hub/.test(raw), k: norm(nombre) });
    }
  });
}
const conocidos = norm(sec('Pendientes') + ' ' + sec('Excluidos'));
const tmsConsiderados = ['leonardo villamil', 'lucia diaz', 'victor guevara', 'raul oidor', 'heidy romero', 'jorge de la cruz', 'cristian calderon', 'juan manuel viveros', 'miguel castellanos'];
const esTM = (pm) => { const p = norm(pm); return tmsConsiderados.some((t) => t.split(' ').filter((w) => w.length > 2).every((w) => p.includes(w))); };

// --- cruce ---
const hubPorK = new Map(hub.map((r) => [norm(`${r.cliente} · ${r.proyecto}`), r]));
const asigK = new Set(asignados.map((a) => a.k));
const porTM = {};
const alertas = [], noEnHub = [];
for (const a of asignados) {
  const r = hubPorK.get(a.k);
  const t = (porTM[a.tm] ??= { alerta: [], sinReporte: [], ok: 0 });
  if (!r) { noEnHub.push(a); continue; }
  if (r.estado === 'Sin reporte') t.sinReporte.push({ ...a, ultimo: r.reporta });
  else if (r.estado === 'Según lo planeado') t.ok++;
  else { t.alerta.push({ ...a, estado: r.estado, avance: r.avance }); alertas.push({ ...a, ...r }); }
}
const nuevos = hub.filter((r) => { const k = norm(`${r.cliente} · ${r.proyecto}`); return !asigK.has(k) && !conocidos.includes(k); })
  .map((r) => ({ nombre: `${r.cliente} · ${r.proyecto}`, pm: r.pm, estado: r.estado, pmEsTM: esTM(r.pm) }));

// --- salida ---
const L = [`# Cruce Hub ↔ asignación · semana ${wk}`, '', `Hub: ${hub.length} tarjetas · asignados en el .md: ${asignados.length}`, ''];
for (const [tm, t] of Object.entries(porTM)) {
  L.push(`## ${tm}`, `- Según lo planeado: ${t.ok}`);
  if (t.alerta.length) L.push('- En alerta:', ...t.alerta.map((a) => `  - [${a.tipo}] ${a.nombre} · ${a.estado}${a.avance ? ' · ' + a.avance : ''}`));
  if (t.sinReporte.length) L.push('- Sin reporte:', ...t.sinReporte.map((a) => `  - [${a.tipo}] ${a.nombre}${a.porConfirmar ? ' (por confirmar)' : ''}${a.ultimo ? ' · último: ' + a.ultimo : ''}`));
  L.push('');
}
L.push(`## En el Hub y no en asignacion-proyectos-tm.md (${nuevos.length})`, '',
  ...(nuevos.length ? nuevos.map((n) => `- ${n.nombre} · PM Hub: ${n.pm}${n.pmEsTM ? ' (TM considerado)' : ''} · ${n.estado}`) : ['Ninguno.']), '',
  `## En el .md y no en el Hub (${noEnHub.length})`, '',
  ...(noEnHub.length ? noEnHub.map((a) => `- ${a.tm} · [${a.tipo}] ${a.nombre}${a.fueraHub ? ' (marcado fuera del Hub)' : ''}`) : ['Ninguno.']), '');
writeFileSync(`scripts/out/cruce-${wk}.md`, L.join('\n'));
writeFileSync(`scripts/out/cruce-${wk}.json`, JSON.stringify({ wk, porTM, alertas, nuevos, noEnHub }, null, 2));
console.log(L.join('\n'));
