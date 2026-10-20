#!/usr/bin/env python3
"""Convierte un acta .md de BlackSip en un Google Doc copiando la plantilla.

Uso: md_to_gdoc.py actas/YYYYMMDD-acta-tema.md [--template ID] [--folder ID] [--name TXT]
                   [--imagenes incrustar|enlaces|ninguna]
Ejecutar desde la raíz del proyecto (`gws --upload` solo acepta archivos dentro del
directorio actual). Requiere `gws` autenticado (gws auth login). Solo stdlib.
"""
import argparse, json, os, re, subprocess, sys

TEMP_FOLDER = "adjuntos-actas-temp"
LINK_RE = re.compile(r"\[([^\]]+)\]\((#[\w-]+)\)")
IMG_RE = re.compile(r"!\[(.*?)\]\((.*?)\)")

TEMPLATE_ID = "1bZv4FqpYhR4F4p_X2E7ejkG0JiKrlGJwz04rWVHN0-0"


def gws(*args):
    r = subprocess.run(["gws", *args], capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"gws falló: {r.stderr.strip() or r.stdout.strip()}\n(¿token vencido? ejecuta `gws auth login`)")
    return json.loads(r.stdout)


# ---------------------------------------------------------------- parser md
def table_rows(lines):
    rows = []
    for l in lines:
        if not l.strip().startswith("|"):
            continue
        cells = [c.strip() for c in l.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-+:?", c) for c in cells if c):
            continue
        rows.append(cells)
    return rows


def tables_in(lines):
    out, cur = [], []
    for l in lines:
        if l.strip().startswith("|"):
            cur.append(l)
        elif cur:
            out.append(table_rows(cur)); cur = []
    if cur:
        out.append(table_rows(cur))
    return out


def plain(s):
    return re.sub(r"\*\*|(?<!\w)_(?=\()|(?<=\))_(?!\w)", "", s).replace("&nbsp;", "").strip()


def blocks(lines):
    """Líneas -> lista de (tipo, dato): p|ol|ul (texto), img ((alt, ruta)), tbl (filas)."""
    out, para, tbl = [], [], []
    def flush():
        if para:
            out.append(("p", " ".join(para))); para.clear()
        if tbl:
            out.append(("tbl", table_rows(tbl))); tbl.clear()
    for l in lines:
        s = l.strip()
        if s.startswith("|"):
            if para:
                flush()
            tbl.append(l); continue
        if tbl:
            flush()
        if not s:
            flush()
        elif IMG_RE.search(s):
            pos = 0
            for mo in IMG_RE.finditer(s):
                if s[pos:mo.start()].strip():
                    para.append(s[pos:mo.start()].strip())
                flush(); out.append(("img", (mo.group(1), mo.group(2)))); pos = mo.end()
            if s[pos:].strip():
                para.append(s[pos:].strip())
        elif re.match(r"\d+\.\s", s):
            flush(); out.append(("ol", re.sub(r"^\d+\.\s*", "", s)))
        elif s.startswith("- "):
            flush(); out.append(("ul", s[2:]))
        else:
            para.append(s)
    flush()
    return out


def parse_annexes(lines):
    """Sección ANEXOS -> [(letra, título, filas)] con `### Anexo X. Título` + tabla."""
    out, cur = [], None
    for l in lines:
        m = re.match(r"^### Anexo (\w+)\.\s*(.+?)\s*$", l)
        if m:
            cur = [m.group(1).upper(), m.group(2), []]; out.append(cur)
        elif cur and l.strip().startswith("|"):
            cur[2].append(l)
    return [(x, t, table_rows(r)) for x, t, r in out]


def promote_tables(sections, annexes):
    """Tablas sueltas del desarrollo -> anexo nuevo + enlace en su lugar (con aviso)."""
    out = []
    for title, bl in sections:
        nb = []
        for k, d in bl:
            if k == "tbl" and d:
                used = {x for x, _, _ in annexes}
                letter = next(c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if c not in used)
                annexes.append((letter, f"Tabla de {plain(title)}", d))
                print(f"aviso: tabla suelta en «{plain(title)}» movida al Anexo {letter}", file=sys.stderr)
                nb.append(("p", f"Ver [Anexo {letter}](#anexo-{letter.lower()})."))
            elif k != "tbl":
                nb.append((k, d))
        out.append((title, nb))
    return out


def parse(md):
    lines = md.splitlines()
    secs, key = {}, None
    for l in lines:
        m = re.match(r"^## ([A-ZÁÉÍÓÚÑ ]+)\s*$", l)
        if m:
            key = m.group(1).strip(); secs[key] = []
        elif key:
            secs[key].append(l)
    g = lambda prefix: next(v for k, v in secs.items() if k.startswith(prefix))

    info = {plain(r[0]): r for r in table_rows(g("INFORMACI"))}
    att = [r for r in table_rows(g("ASISTENTES"))[1:]]
    dev = g("DESARROLLO")
    i_obj = next(i for i, l in enumerate(dev) if "Objetivo de la reuni" in l)
    i_ag = next(i for i, l in enumerate(dev) if l.startswith("## **Agenda"))
    i_des = next(i for i, l in enumerate(dev) if l.startswith("### Desarrollo de la Agenda"))
    objetivo = " ".join(s.strip() for s in dev[i_obj + 1:i_ag] if s.strip())
    agenda = [re.sub(r"^\d+\.\s*", "", s.strip()) for s in dev[i_ag + 1:i_des] if s.strip()]
    sections, cur = [], None
    for l in dev[i_des + 1:]:
        m = re.match(r"^### \*\*(.+?)\*\*\s*$", l)
        if m:
            cur = (m.group(1), []); sections.append(cur)
        elif cur:
            cur[1].append(l)
    firma = tables_in(g("FIRMA"))
    annexes = parse_annexes(secs.get("ANEXOS", []))
    sign = []
    for c in firma[0][-1]:
        parts = c.split("<br>")
        sign.append((plain(parts[0]), plain(parts[1]) if len(parts) > 1 else ""))
    return dict(
        info=info, att=att, objetivo=objetivo, agenda=agenda,
        annexes=annexes, sections=promote_tables([(t, blocks(b)) for t, b in sections], annexes),
        concl=[l.strip()[2:] for l in g("CONCLUSIONES") if l.strip().startswith("- ")],
        comp=table_rows(g("COMPROMISOS"))[1:], sign=sign, autor=firma[1][-1],
    )


# ------------------------------------------------- contenido rico por celda
def runs(text):
    """'a **b** _(c)_' -> [(texto, bold, italic)]."""
    out = []
    for part in re.split(r"(\*\*.+?\*\*|(?<!\w)_.+?_(?!\w))", text):
        if not part:
            continue
        if part.startswith("**"):
            out.append((part[2:-2], True, False))
        elif part.startswith("_") and part.endswith("_") and len(part) > 2:
            out.append((part[1:-1], False, True))
        else:
            out.append((part, False, False))
    return out


def P(text, bullet=None, bold=False):
    r = runs(text)
    if bold:
        r = [(t, True, i) for t, _, i in r]
    return dict(runs=r, bullet=bullet)


def clean(s):  # texto de celda de tabla md
    return s.replace("&nbsp;", "").strip()


# --------------------------------------------------------------- Docs API
def cell_job(cell, paras, replace):
    """Peticiones para escribir `paras` en una celda. Índices válidos mientras
    se procesen las celdas de mayor a menor índice."""
    start = cell["content"][0]["startIndex"]
    end = cell["content"][-1]["endIndex"] - 1
    reqs = []
    if replace:
        if end > start:
            reqs.append({"deleteContentRange": {"range": {"startIndex": start, "endIndex": end}}})
        pos, lead = start, ""
    else:
        pos, lead = end, "\n"
    text = lead + "\n".join("".join(t for t, _, _ in p["runs"]) for p in paras)
    reqs.append({"insertText": {"location": {"index": pos}, "text": text}})
    a, b = pos, pos + len(text)
    rng = lambda s, e: {"startIndex": s, "endIndex": e}
    reqs.append({"updateTextStyle": {"range": rng(a, b), "fields": "bold,italic",
                                      "textStyle": {"bold": False, "italic": False}}})
    reqs.append({"updateParagraphStyle": {"range": rng(a, b), "fields": "namedStyleType,spaceBelow",
                                           "paragraphStyle": {"namedStyleType": "NORMAL_TEXT",
                                                              "spaceBelow": {"magnitude": 4, "unit": "PT"}}}})
    cur = pos + len(lead)
    groups = []  # (inicio, fin, tipo) de listas consecutivas
    for p in paras:
        n = sum(len(t) for t, _, _ in p["runs"])
        o = cur
        for t, bold, ital in p["runs"]:
            if bold or ital:
                reqs.append({"updateTextStyle": {"range": rng(o, o + len(t)), "fields": "bold,italic",
                                                  "textStyle": {"bold": bold, "italic": ital}}})
            o += len(t)
        if p["bullet"]:
            if groups and groups[-1][2] == p["bullet"] and groups[-1][1] == cur - 1:
                groups[-1][1] = cur + n
            else:
                groups.append([cur, cur + n, p["bullet"]])
        cur += n + 1
    for s, e, kind in groups:
        preset = "NUMBERED_DECIMAL_NESTED" if kind == "ol" else "BULLET_DISC_CIRCLE_SQUARE"
        reqs.append({"createParagraphBullets": {"range": rng(s, e), "bulletPreset": preset}})
    return start, reqs


def get_doc(doc_id):
    d = gws("docs", "documents", "get", "--params",
            json.dumps({"documentId": doc_id, "includeTabsContent": True}))
    return d["tabs"][0]["documentTab"]["body"]["content"]


def tables(content):
    return [e for e in content if "table" in e]


def cell_at(tbl, row, col):
    return tbl["table"]["tableRows"][row]["tableCells"][col]


def batch(doc_id, reqs):
    if reqs:
        gws("docs", "documents", "batchUpdate", "--params", json.dumps({"documentId": doc_id}),
            "--json", json.dumps({"requests": reqs}))


def build(doc_id, a):
    # 1) filas extra (tablas de abajo hacia arriba para no mover índices)
    tbls = tables(get_doc(doc_id))
    extra = [(3, 7, len(a["comp"]) - 6), (0, 12, len(a["att"]) - 4)]  # (tabla, última fila original, n)
    add = []
    for t, last, n in extra:  # tabla 3 antes que la 0: no mueve índices de la 0
        for _ in range(max(n, 0)):
            add.append({"insertTableRow": {"insertBelow": True, "tableCellLocation": {
                "tableStartLocation": {"index": tbls[t]["startIndex"]},
                "rowIndex": last, "columnIndex": 0}}})
    batch(doc_id, add)

    # 2) rellenar celdas (índices de mayor a menor)
    tb = tables(get_doc(doc_id))
    info, jobs = a["info"], []
    def put(t, r, c, paras, replace=True):
        jobs.append(cell_job(cell_at(tb[t], r, c), paras, replace))
    one = lambda s, **k: [P(s, **k)]
    val = lambda k: clean(info[k][1]) if k in info else ""
    if val("Número de acta"): put(0, 1, 1, one(val("Número de acta")))
    put(0, 2, 1, one(val("Proyecto")))
    put(0, 3, 1, one(val("Lugar de la reunión")))
    for r, k in ((4, "Fecha de inicio"), (5, "Fecha de finalización")):
        row = [clean(x) for x in info[k]]
        for c, s, kw in ((1, row[1], dict(bold=True)), (3, row[2], {}), (5, row[3], dict(bold=True)), (6, row[4], {})):
            put(0, r, c, one(plain(s), **kw))
    put(0, 6, 1, one(val("Asunto")))
    for i, row in enumerate(a["att"]):
        r = 9 + i
        bold = row[0].startswith("**")
        for c, s in ((0, row[0]), (2, row[1]), (4, row[2])):
            if clean(s):
                put(0, r, c, one(clean(s), bold=bold))
    # desarrollo
    top = [P("Objetivo de la reunión", bold=True), P(a["objetivo"]), P("Agenda", bold=True)]
    top += [P(x, "ol") for x in a["agenda"]]
    put(1, 2, 0, top)
    dev = []
    def mark(t):  # [texto](#anexo-x) -> marcador, resuelto en la segunda pasada
        def r(mo):
            a["links"].append((mo.group(2).lstrip("#"), mo.group(1)))
            return f"[[LNK:{len(a['links'])}]]"
        return LINK_RE.sub(r, t)
    a["links"], a["imgs"] = [], []
    for title, bl in a["sections"]:
        dev.append(P(title, bold=True))
        for k, t in bl:
            if k == "img":
                a["imgs"].append(t); dev.append(P(f"[[IMG:{len(a['imgs'])}]]"))
            else:
                dev.append(P(mark(t), k if k != "p" else None))
    put(1, 4, 0, dev)
    put(2, 1, 0, [P(x, "ul") for x in a["concl"]])
    for i, row in enumerate(a["comp"]):
        put(3, 2 + i, 0, one(clean(row[0]))); put(3, 2 + i, 1, one(clean(row[1])))
    for c, (name, role) in zip((0, 3), a["sign"]):
        put(4, 3, c, [P(name, bold=True), P(role)], replace=False)
    ver, nom, fecha, obs = [clean(x) for x in a["autor"][:4]]
    for c, s in ((0, ver), (1, nom), (2, fecha), (4, obs)):
        put(4, 6, c, one(s))
    reqs = []
    for _, rq in sorted(jobs, key=lambda j: -j[0]):
        reqs += rq
    batch(doc_id, reqs)


# ------------------------------------------- segunda pasada: anexos e imágenes
def body_of(d):
    return d["tabs"][0]["documentTab"]["body"]["content"]


def full_doc(doc_id):
    return gws("docs", "documents", "get", "--params",
               json.dumps({"documentId": doc_id, "includeTabsContent": True}))


def ptext(p):
    return "".join(x.get("textRun", {}).get("content", "") for x in p["elements"]).strip()


def add_annexes(doc_id, annexes):
    """Salto de página, «ANEXOS» y por anexo: título (HEADING_2) + tabla real."""
    batch(doc_id, [{"insertPageBreak": {"endOfSegmentLocation": {}}},
                   {"insertText": {"endOfSegmentLocation": {}, "text": "ANEXOS\n"}}])
    titles = [f"Anexo {x}. {t}" for x, t, _ in annexes]
    for (x, t, rows), title in zip(annexes, titles):
        cols = max(len(r) for r in rows)
        batch(doc_id, [{"insertText": {"endOfSegmentLocation": {}, "text": title + "\n"}},
                       {"insertTable": {"endOfSegmentLocation": {}, "rows": len(rows), "columns": cols}}])
    rq = []
    for e in body_of(full_doc(doc_id)):
        p = e.get("paragraph")
        if not p:
            continue
        t = ptext(p)
        rng = {"startIndex": e["startIndex"], "endIndex": e["endIndex"] - 1}
        if t == "ANEXOS":
            rq.append({"updateTextStyle": {"range": rng, "fields": "bold", "textStyle": {"bold": True}}})
        elif t in titles:
            rq.append({"updateParagraphStyle": {"range": {"startIndex": e["startIndex"], "endIndex": e["endIndex"]},
                                                 "fields": "namedStyleType", "paragraphStyle": {"namedStyleType": "HEADING_2"}}})
            rq.append({"updateTextStyle": {"range": rng, "fields": "bold,fontSize",
                                           "textStyle": {"bold": True, "fontSize": {"magnitude": 12, "unit": "PT"}}}})
    batch(doc_id, rq)
    tb = tables(body_of(full_doc(doc_id)))[-len(annexes):]
    fill = []
    for t, (_, _, rows) in zip(tb, annexes):
        for ri, row in enumerate(rows):
            for ci, val in enumerate(row):
                if clean(plain(val)):
                    idx = t["table"]["tableRows"][ri]["tableCells"][ci]["content"][0]["startIndex"]
                    fill.append((idx, plain(val), ri == 0))
    rq = []
    for idx, val, hd in sorted(fill, reverse=True):  # de abajo hacia arriba
        rq.append({"insertText": {"location": {"index": idx}, "text": val}})
        if hd:
            rq.append({"updateTextStyle": {"range": {"startIndex": idx, "endIndex": idx + len(val)},
                                           "fields": "bold", "textStyle": {"bold": True}}})
    batch(doc_id, rq)


def temp_folder():
    q = f"name='{TEMP_FOLDER}' and mimeType='application/vnd.google-apps.folder' and 'root' in parents and trashed=false"
    f = gws("drive", "files", "list", "--params", json.dumps({"q": q})).get("files", [])
    if f:
        return f[0]["id"]
    return gws("drive", "files", "create", "--json", json.dumps(
        {"name": TEMP_FOLDER, "mimeType": "application/vnd.google-apps.folder"}))["id"]


def finish(doc_id, a, mode, md_dir, stem):
    """Anexos al final y, en una segunda pasada de abajo hacia arriba, imágenes y enlaces."""
    annexes, imgs, links = a["annexes"], a["imgs"], a["links"]
    if annexes:
        add_annexes(doc_id, annexes)
    if not (imgs or links):
        return
    uri, files, perms = {}, [], []
    try:
        if mode == "incrustar":
            folder = None
            for n, (alt, path) in enumerate(imgs, 1):
                full = os.path.normpath(os.path.join(md_dir, path))
                rel = os.path.relpath(full)
                if rel.startswith("..") or not os.path.isfile(full):
                    print(f"aviso: imagen fuera del directorio actual o inexistente, queda como texto: {path}", file=sys.stderr)
                    continue
                try:
                    folder = folder or temp_folder()
                    ctype = "image/png" if full.lower().endswith(".png") else "image/jpeg"
                    f = gws("drive", "files", "create", "--json", json.dumps(
                        {"name": f"{stem}-{os.path.basename(full)}", "parents": [folder]}),
                        "--upload", rel, "--upload-content-type", ctype)
                    files.append(f["id"])
                    perms.append((f["id"], gws("drive", "permissions", "create", "--params",
                                              json.dumps({"fileId": f["id"]}), "--json",
                                              json.dumps({"type": "anyone", "role": "reader"}))["id"]))
                except SystemExit as e:
                    print(f"aviso: no se pudo compartir/subir la imagen ({e.code}); el resto queda como texto", file=sys.stderr)
                    break
                uri[n] = f"https://drive.google.com/uc?export=download&id={f['id']}"
        d = full_doc(doc_id)
        hid = {}
        for e in body_of(d):
            p = e.get("paragraph")
            if p and p["paragraphStyle"].get("headingId"):
                hid[ptext(p)] = p["paragraphStyle"]["headingId"]
        hid = {f"anexo-{x.lower()}": hid.get(f"Anexo {x}. {t}") for x, t, _ in annexes}
        marks = []
        for e in body_of(d):
            for r in e.get("table", {}).get("tableRows", []):
                for c in r["tableCells"]:
                    for p in c["content"]:
                        for el in p.get("paragraph", {}).get("elements", []):
                            t = el.get("textRun", {}).get("content", "")
                            for mo in re.finditer(r"\[\[(IMG|LNK):(\d+)\]\]", t):
                                marks.append((el["startIndex"] + mo.start(), mo.group(1), int(mo.group(2)), mo.group(0)))
        rq = []
        for pos, kind, n, txt in sorted(marks, reverse=True):
            rq.append({"deleteContentRange": {"range": {"startIndex": pos, "endIndex": pos + len(txt)}}})
            if kind == "IMG":
                if n in uri:
                    rq.append({"insertInlineImage": {"location": {"index": pos}, "uri": uri[n],
                                                     "objectSize": {"width": {"magnitude": 440, "unit": "PT"}}}})
                elif mode != "ninguna":
                    alt, path = imgs[n - 1]
                    rq.append({"insertText": {"location": {"index": pos}, "text": f"[Imagen: {alt} ({path})]"}})
            else:
                slug, texto = links[n - 1]
                rq.append({"insertText": {"location": {"index": pos}, "text": texto}})
                if hid.get(slug):
                    rq.append({"updateTextStyle": {"range": {"startIndex": pos, "endIndex": pos + len(texto)},
                                                   "fields": "link", "textStyle": {"link": {"headingId": hid[slug]}}}})
                else:
                    print(f"aviso: la referencia «{texto}» (#{slug}) no tiene anexo; queda como texto", file=sys.stderr)
        batch(doc_id, rq)
    finally:  # el Doc ya guarda su copia: cerrar permiso y borrar el temporal siempre
        for fid, pid in perms:
            try:
                gws("drive", "permissions", "delete", "--params", json.dumps({"fileId": fid, "permissionId": pid}))
            except SystemExit:
                print(f"aviso: no se pudo cerrar el permiso de {fid}; búscalo en {TEMP_FOLDER}", file=sys.stderr)
        for fid in files:
            try:
                gws("drive", "files", "delete", "--params", json.dumps({"fileId": fid}))
            except SystemExit:
                print(f"aviso: no se pudo borrar {fid}; búscalo en {TEMP_FOLDER}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("md"); ap.add_argument("--template", default=TEMPLATE_ID)
    ap.add_argument("--folder"); ap.add_argument("--name")
    ap.add_argument("--imagenes", choices=["incrustar", "enlaces", "ninguna"], default="incrustar")
    o = ap.parse_args()
    a = parse(open(o.md, encoding="utf-8").read())
    m = re.search(r"(\d{4})(\d{2})(\d{2})", o.md.split("/")[-1])
    fecha = "-".join(m.groups()) if m else ""
    asunto = plain(a["info"]["Asunto"][1]).split(":")[0]
    num = clean(a["info"].get("Número de acta", ["", ""])[1])
    name = o.name or f"{fecha} - Acta{' ' + num if num else ''} - {asunto}"
    body = {"name": name, **({"parents": [o.folder]} if o.folder else {})}
    new = gws("drive", "files", "copy", "--params", json.dumps({"fileId": o.template}), "--json", json.dumps(body))
    build(new["id"], a)
    finish(new["id"], a, o.imagenes, os.path.dirname(o.md), os.path.splitext(os.path.basename(o.md))[0])
    print(f"https://docs.google.com/document/d/{new['id']}/edit")


if __name__ == "__main__":
    main()
