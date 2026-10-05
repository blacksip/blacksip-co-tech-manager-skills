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

## Usar en opencode (sin Claude Code)

Opcional si ya usas el plugin en Claude Code. Para instalar las skills en opencode sin tener Claude Code, primero deja listo `gh` con SSH (ver "Antes de instalar") y luego ejecuta:

```bash
bash <(gh api repos/blacksip/blacksip-co-tech-manager-skills/contents/scripts/install-opencode.sh -H "Accept: application/vnd.github.raw")
```

Clona este repo en `~/.local/share/blacksip-co-tech-manager-skills` y copia las skills a `~/.config/opencode/skills/`. Además crea un comando por skill en `~/.config/opencode/commands/`, todos con el prefijo `tm-actas:` (los dos puntos no son válidos en nombres de archivo de Windows; el script es para macOS/Linux): `/tm-actas:crear-acta-md` y `/tm-actas:acta-md-to-google-docs` (acepta argumentos, p. ej. `/tm-actas:crear-acta-md <enlace de Granola>`). Para actualizar, vuelve a ejecutar el mismo comando y reinicia opencode. Después ejecuta `scripts/setup.sh` desde esa carpeta para los requisitos (`gws`, sesión de Google) y configura el MCP de Granola en `opencode.json`.

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
