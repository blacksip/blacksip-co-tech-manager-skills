# blacksip-co-tech-manager-skills

Marketplace de plugins de Claude Code para los Tech Managers de Blacksip.

## Antes de instalar (una sola vez)

El marketplace es privado y se clona por SSH, así que `gh` (GitHub CLI) debe estar instalado y con sesión **antes** de `/plugin marketplace add`. En una terminal (macOS), copia y pega:

```bash
brew install gh && { gh api user >/dev/null 2>&1 || gh auth login; } && bash <(gh api repos/blacksip/blacksip-co-tech-manager-skills/contents/scripts/setup.sh -H "Accept: application/vnd.github.raw")
```

Si no tienes Homebrew, instálalo primero desde https://brew.sh. En `gh auth login` elige **GitHub.com → SSH**. El script `scripts/setup.sh` te guía para dejar listos `gh`, Node.js, Python 3 y `gws` (con tu sesión de Google y el `client_secret.json` compartido del equipo, que no está en este repo: descárgalo de 1Password, bóveda `Technology - TechManagers`, ítem `gws – client_secret.json (Blacksip)`) y verifica el acceso al repo y a la plantilla de acta; puedes volver a ejecutarlo cuando quieras (no repite lo ya instalado).

## Instalar

```
/plugin marketplace add blacksip/blacksip-co-tech-manager-skills
/plugin install tm-actas@blacksip-co-tech-manager-skills
```

## Actualizar

```
/plugin marketplace update blacksip-co-tech-manager-skills
```

## Instalar en opencode (sin Claude Code)

Para quien usa opencode en lugar de Claude Code (o además de él). Solo macOS/Linux.

**1. Requisitos previos (una sola vez).** `gh` con sesión y SSH, igual que en "Antes de instalar" (si ya ejecutaste ese comando, salta al paso 2). Necesitas además opencode instalado: `curl -fsSL https://opencode.ai/install | bash`.

**2. Instalar.** En una terminal:

```bash
bash <(gh api repos/blacksip/blacksip-co-tech-manager-skills/contents/scripts/install-opencode.sh -H "Accept: application/vnd.github.raw")
```

Clona este repo en `~/.local/share/blacksip-co-tech-manager-skills`, copia las skills a `~/.config/opencode/skills/` y crea un comando por skill en `~/.config/opencode/commands/`.

**3. Reiniciar opencode** y escribir `/tm-actas:` para ver los comandos:

| Comando | Qué hace |
| :-- | :-- |
| `/tm-actas:crear-acta-md <notas o enlace>` | Crea el acta en Markdown (`actas/YYYYMMDD-acta-<tema>.md`) |
| `/tm-actas:acta-md-to-google-docs <acta.md>` | Pasa el acta a Google Docs con la plantilla de BlackSip |

**4. Requisitos de las skills (una sola vez).** Ejecuta `bash ~/.local/share/blacksip-co-tech-manager-skills/scripts/setup.sh` para dejar listos `gws`, la sesión de Google y el `client_secret.json` (1Password, bóveda `Technology - TechManagers`).

**5. MCP de Granola** (para leer notas de reunión). Agrégalo en `~/.config/opencode/opencode.json` (o `.jsonc`) y autoriza con `opencode mcp auth granola`:

```json
{
  "mcp": {
    "granola": { "type": "remote", "url": "https://mcp.granola.ai/mcp" }
  }
}
```

Si no lo configuras, `crear-acta-md` funciona pegándole el texto de las notas.

**Actualizar:** vuelve a ejecutar el comando del paso 2 y reinicia opencode. **Desinstalar:** borra `~/.config/opencode/skills/{crear-acta-md,acta-md-to-google-docs}`, `~/.config/opencode/commands/tm-actas:*.md` y `~/.local/share/blacksip-co-tech-manager-skills`.

Los dos puntos de `tm-actas:` no son válidos en nombres de archivo de Windows, por eso el script es solo para macOS/Linux.

## Plugins

| Plugin | Skills |
| :-- | :-- |
| `tm-actas` | `crear-acta-md`, `acta-md-to-google-docs` |

## Requisitos (cada persona con su propia cuenta)

- **Granola** conectado como MCP (para leer notas de reunión).
- **Google Drive** conectado y el CLI **`gws`** autenticado (`gws auth login`).
- Acceso a la plantilla de Drive "Template/Plantilla - Acta de seguimiento de proyecto".
- Python 3 (para `md_to_gdoc.py`).
- Las actas se escriben en `actas/` del proyecto donde se ejecute la skill.

## Mantener

- Cada cambio en una skill: subir `version` en `plugins/<plugin>/.claude-plugin/plugin.json`, si no los usuarios no ven la actualización.
- Skill nueva: carpeta en `plugins/<plugin>/skills/<nombre>/SKILL.md`, o plugin nuevo registrado en `.claude-plugin/marketplace.json`.
- No incluir datos reales de clientes en las skills ni en sus referencias.

## Cómo contribuir

`main` está protegida: todo cambio entra por pull request con al menos 1 aprobación de un code owner. `.github/CODEOWNERS` asigna todo el repo a `@blacksip/tech-managers`, así que cualquier Tech Manager (distinto del autor del PR) puede aprobar. Para que una skill requiera un revisor específico, agrega una línea en `CODEOWNERS` (`/plugins/<plugin>/ @usuario`).

1. Crea una rama desde `main` (`feat/<skill>` o `fix/<skill>`).
2. Agrega o edita la skill en `plugins/<plugin>/skills/<nombre>/SKILL.md`. Si es un plugin nuevo, regístralo en `.claude-plugin/marketplace.json`.
3. Sube `version` en el `plugin.json` del plugin afectado (si no, nadie recibe el cambio).
4. Revisa que no haya datos reales de clientes (nombres, emails, cifras) y que las rutas usen `${CLAUDE_PLUGIN_ROOT}`.
5. Abre el PR y pide revisión a otro Tech Manager.
6. Tras el merge, cada persona actualiza con `/plugin marketplace update blacksip-co-tech-manager-skills`.

## Rotar el client_secret.json

Si el archivo se filtra o alguien sale del equipo: en Google Cloud Console (proyecto `jochoa-gclod-claude`, Google Auth Platform → Clients) crea un secreto nuevo, desactiva el anterior, actualiza el adjunto en 1Password y avisa al equipo para que vuelva a ejecutar `scripts/setup.sh`.
