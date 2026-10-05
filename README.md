# blacksip-co-tech-manager-skills

Skills compartidas de los Tech Managers de Blacksip. Funcionan en **Claude Code** (como plugin de un marketplace) y en **opencode** (con un script de instalación).

| Plugin | Skills | Comandos |
| :-- | :-- | :-- |
| `tm-actas` | `crear-acta-md`: crea el acta de una reunión en Markdown desde notas de Granola, Gemini o texto pegado | `/tm-actas:crear-acta-md` |
| | `acta-md-to-google-docs`: pasa un acta `.md` a Google Docs con la plantilla de BlackSip | `/tm-actas:acta-md-to-google-docs` |

## Elige tu camino

La instalación tiene 3 pasos. Los pasos 1 y 3 son comunes; el paso 2 depende de qué cliente usas.

| | Claude Code | opencode (sin Claude Code) |
| :-- | :-- | :-- |
| **macOS** | Paso 1 macOS → Paso 2A | Paso 1 macOS → Paso 2B |
| **Windows** | Paso 1 Windows (WSL2) → Paso 2A dentro de WSL | Paso 1 Windows (WSL2) → Paso 2B dentro de WSL |

Si usas **los dos clientes**, haz el paso 1 una sola vez y luego el 2A y el 2B.

> **Windows:** los scripts son de bash y solo están probados en macOS. En Windows todo se ejecuta dentro de **WSL2 (Ubuntu)**, incluido Claude Code u opencode.

---

## Paso 1. Requisitos previos (una sola vez)

Necesitas, antes de empezar:

- **Pertenecer al equipo `tech-managers`** de la organización `blacksip` en GitHub. El repo es privado; sin acceso, la instalación falla con `404` o `Permission denied`.
- **Acceso a 1Password**, bóveda `Technology - TechManagers`, para descargar el ítem `gws – client_secret.json (Blacksip)`. Es el cliente OAuth compartido de Google y no está en este repo a propósito.
- **Acceso a la plantilla de Drive** "Template/Plantilla - Acta de seguimiento de proyecto".

En `gh auth login` elige siempre **GitHub.com → SSH**: el marketplace y el instalador clonan este repo por SSH.

### macOS

Si no tienes Homebrew, instálalo desde https://brew.sh. Luego, en una terminal:

```bash
brew install gh && { gh api user >/dev/null 2>&1 || gh auth login; } && bash <(gh api repos/blacksip/blacksip-co-tech-manager-skills/contents/scripts/setup.sh -H "Accept: application/vnd.github.raw")
```

Ese comando instala `gh` y ejecuta `scripts/setup.sh`, que revisa e instala (pidiendo confirmación en cada caso) lo siguiente:

| Herramienta | Para qué sirve | Cómo la instala |
| :-- | :-- | :-- |
| `gh` (GitHub CLI) | Descargar este repo privado y autenticarte por SSH | `brew install gh` |
| Node.js | Instalar `gws` | `brew install node` |
| Python 3 | Ejecutar `md_to_gdoc.py` | `brew install python` |
| `gws` (Google Workspace CLI) | Leer y escribir en Drive y Docs desde las skills | `npm install -g @googleworkspace/cli` |

Después inicia sesión en Google (`gws auth login -s drive,docs`, con tu cuenta `@blacksip.com`). Cuando el script pida el `client_secret.json`, descárgalo de 1Password y arrastra el archivo a la terminal. Al final verifica el acceso al repo, por SSH y a la plantilla de acta. **No instala el plugin ni las skills:** eso es el paso 2. Puedes volver a ejecutarlo cuando quieras: no repite lo ya instalado.

**Instalar `gws` a mano** (si prefieres no usar el script):

```bash
npm install -g @googleworkspace/cli
mkdir -p ~/.config/gws && cp ~/Downloads/client_secret.json ~/.config/gws/ && chmod 600 ~/.config/gws/client_secret.json
gws auth login -s drive,docs
```

Comprueba que quedó bien con `gws --version` y `gws auth status` (debe mostrar `"has_refresh_token": true`).

### Windows (WSL2)

1. En PowerShell como administrador: `wsl --install -d Ubuntu`. Reinicia y crea tu usuario de Ubuntu.
2. Abre **Ubuntu** (no PowerShell). Todo lo que sigue se ejecuta allí:

   ```bash
   sudo apt update && sudo apt install -y git python3 curl
   ```

3. Instala **Node.js 20 o superior** (https://github.com/nvm-sh/nvm) y **GitHub CLI** (https://github.com/cli/cli/blob/trunk/docs/install_linux.md).
4. Instala `gws` e inicia sesión en GitHub:

   ```bash
   npm install -g @googleworkspace/cli
   gh auth login        # GitHub.com → SSH
   ```

5. Descarga el `client_secret.json` de 1Password a `Descargas` de Windows y cópialo desde Ubuntu:

   ```bash
   mkdir -p ~/.config/gws && cp "/mnt/c/Users/<tu-usuario>/Downloads/client_secret.json" ~/.config/gws/ && chmod 600 ~/.config/gws/client_secret.json
   gws auth login -s drive,docs
   ```

   Si el navegador no se abre solo, copia la URL que imprime `gws` y ábrela en Windows.

Alternativa sin WSL (PowerShell nativo): `winget install GitHub.cli Python.Python.3.12 OpenJS.NodeJS`, luego `npm install -g @googleworkspace/cli` y `gh auth login`. **No está verificada:** `md_to_gdoc.py` invoca `python3` y `gws`, que en Windows nativo pueden no resolverse igual. Si la usas, repórtalo para ajustar los scripts.

---

## Paso 2A. Instalar en Claude Code

Abre Claude Code y ejecuta:

```
/plugin marketplace add blacksip/blacksip-co-tech-manager-skills
/plugin install tm-actas@blacksip-co-tech-manager-skills
```

Reinicia Claude Code. Las skills quedan disponibles en todos tus proyectos (instalación a nivel de usuario).

**Actualizar:**

```
/plugin marketplace update blacksip-co-tech-manager-skills
```

También puedes activar la actualización automática del marketplace desde `/plugin`.

**Desinstalar:**

```
/plugin uninstall tm-actas@blacksip-co-tech-manager-skills
/plugin marketplace remove blacksip-co-tech-manager-skills
```

---

## Paso 2B. Instalar en opencode (sin Claude Code)

En macOS, en una terminal. En Windows, dentro de Ubuntu (WSL). Necesitas opencode instalado: `curl -fsSL https://opencode.ai/install | bash`. Luego:

```bash
bash <(gh api repos/blacksip/blacksip-co-tech-manager-skills/contents/scripts/install-opencode.sh -H "Accept: application/vnd.github.raw")
```

El script:

- clona este repo en `~/.local/share/blacksip-co-tech-manager-skills`;
- copia las skills a `~/.config/opencode/skills/`;
- crea un comando por skill en `~/.config/opencode/commands/` con el prefijo `tm-actas:` (los dos puntos no son válidos en nombres de archivo de Windows nativo, por eso es para macOS/Linux/WSL).

Reinicia opencode.

**Actualizar:** vuelve a ejecutar el mismo comando y reinicia opencode.

**Desinstalar:** borra `~/.config/opencode/skills/{crear-acta-md,acta-md-to-google-docs}`, `~/.config/opencode/commands/tm-actas:*.md` y `~/.local/share/blacksip-co-tech-manager-skills`.

---

## Paso 3. Conectar Granola y verificar

**Granola** (para leer las notas de reunión). Sin él, `crear-acta-md` funciona igual si le pegas el texto de las notas.

- **Claude Code:** conéctalo desde los conectores de la app de Claude, o con `claude mcp add --scope user --transport http granola https://mcp.granola.ai/mcp` (`--scope user` lo deja disponible en todos tus proyectos; sin él solo queda en el proyecto actual).
- **opencode:** agrégalo en `~/.config/opencode/opencode.json` (o `.jsonc`) y autoriza con `opencode mcp auth granola`:

  ```json
  {
    "mcp": {
      "granola": { "type": "remote", "url": "https://mcp.granola.ai/mcp" }
    }
  }
  ```

**Verifica la instalación** abriendo una sesión nueva:

- **Claude Code:** escribe `/tm-actas` y debes ver `tm-actas:crear-acta-md` y `tm-actas:acta-md-to-google-docs`.
- **opencode:** escribe `/tm-actas:` y debes ver los dos comandos.

---

## Usar

Desde la carpeta del proyecto cuyo acta quieres escribir (las actas se guardan en `actas/`):

```
/tm-actas:crear-acta-md <enlace de Granola o texto de las notas>
```

La skill te muestra primero la tabla de compromisos (tarea y responsable) y espera tu confirmación antes de escribir `actas/YYYYMMDD-acta-<tema>.md`. Luego, para generar el Google Doc con la plantilla:

```
/tm-actas:acta-md-to-google-docs actas/YYYYMMDD-acta-<tema>.md
```

Imprime la URL del documento. Cada ejecución crea un documento nuevo en Drive.

## Problemas frecuentes

| Síntoma | Causa y solución |
| :-- | :-- |
| `gh: Not Found (HTTP 404)` al ejecutar un comando de este README | No tienes acceso al repo (pide que te agreguen a `tech-managers`), no tienes sesión en `gh` (`gh auth login`), o el archivo aún no está en `main`. |
| `Permission denied (publickey)` al instalar o clonar | `gh` se configuró con HTTPS. Ejecuta `gh auth login` y elige SSH, o agrega tu llave en https://github.com/settings/keys. |
| `invalid_grant` o `invalid_rapt` en `gws` | El token de Google venció. Ejecuta `gws auth login`. |
| No aparecen las skills o los comandos | Reinicia el cliente. En opencode, comprueba que existan `~/.config/opencode/skills/crear-acta-md` y `~/.config/opencode/commands/tm-actas:*.md`. |
| `gws auth login` pide `client_secret.json` | Descárgalo de 1Password (ver paso 1) y colócalo en `~/.config/gws/client_secret.json`. |
| Se ven comandos `tm-actas-…` antiguos en opencode | Vuelve a ejecutar el instalador de opencode: borra los nombres antiguos. |

## Requisitos de las skills

- **Granola** conectado como MCP (opcional, ver paso 3).
- **`gws`** (Google Workspace CLI) autenticado con tu cuenta `@blacksip.com`.
- **Python 3**, para `md_to_gdoc.py`.
- Acceso a la plantilla de acta en Drive.

## Mantener

- Cada cambio en una skill: sube `version` en `plugins/<plugin>/.claude-plugin/plugin.json`; si no, quienes usan Claude Code no ven la actualización.
- Skill nueva: carpeta en `plugins/<plugin>/skills/<nombre>/SKILL.md`, o plugin nuevo registrado en `.claude-plugin/marketplace.json`. El instalador de opencode crea su comando `tm-actas:<nombre>` automáticamente.
- No incluir datos reales de clientes en las skills ni en sus referencias.
- Las skills deben funcionar en ambos clientes: no uses `${CLAUDE_PLUGIN_ROOT}` ni nombres de herramientas propios de Claude. Referencia los archivos de la skill con rutas relativas a su carpeta.

## Cómo contribuir

`main` está protegida: todo cambio entra por pull request con al menos 1 aprobación de un code owner. `.github/CODEOWNERS` asigna todo el repo a `@blacksip/tech-managers`, así que cualquier Tech Manager (distinto del autor del PR) puede aprobar. Para que una skill requiera un revisor específico, agrega una línea en `CODEOWNERS` (`/plugins/<plugin>/ @usuario`).

1. Crea una rama desde `main` (`feat/<skill>` o `fix/<skill>`).
2. Agrega o edita la skill en `plugins/<plugin>/skills/<nombre>/SKILL.md`. Si es un plugin nuevo, regístralo en `.claude-plugin/marketplace.json`.
3. Sube `version` en el `plugin.json` del plugin afectado.
4. Revisa que no haya datos reales de clientes (nombres, emails, cifras) y que las rutas sean relativas a la carpeta de la skill.
5. Abre el PR y pide revisión a otro Tech Manager.
6. Tras el merge, cada persona actualiza: Claude Code con `/plugin marketplace update blacksip-co-tech-manager-skills`, opencode volviendo a ejecutar el instalador.

## Rotar el client_secret.json

Si el archivo se filtra o alguien sale del equipo: en Google Cloud Console (proyecto `jochoa-gclod-claude`, Google Auth Platform → Clients) crea un secreto nuevo, desactiva el anterior, actualiza el adjunto en 1Password y avisa al equipo para que vuelva a ejecutar `scripts/setup.sh` (macOS) o repita el paso 5 de Windows.
