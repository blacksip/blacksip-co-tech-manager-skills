#!/usr/bin/env bash
# Guía de instalación de requisitos para las skills de tm-actas (macOS).
# Idempotente: puede ejecutarse varias veces; salta lo que ya está listo.
set -u

TEMPLATE_ID="1bZv4FqpYhR4F4p_X2E7ejkG0JiKrlGJwz04rWVHN0-0"
GWS_DIR="$HOME/.config/gws"

ok()   { printf '  \033[32m✔\033[0m %s\n' "$*"; }
warn() { printf '  \033[33m!\033[0m %s\n' "$*"; }
step() { printf '\n\033[1m%s\033[0m\n' "$*"; }
ask()  { read -r -p "  $1 [s/N] " a; [[ "$a" =~ ^[sSyY]$ ]]; }
die()  { printf '  \033[31m✘\033[0m %s\n' "$*"; exit 1; }

[[ "$(uname)" == "Darwin" ]] || die "Este script solo cubre macOS. En Linux o Windows (WSL) sigue la sección Windows del README."

step "1/6 Homebrew"
if command -v brew >/dev/null; then ok "brew instalado"
else
  warn "Falta Homebrew. Instálalo con el comando de https://brew.sh, abre una terminal nueva y vuelve a ejecutar este script."
  exit 1
fi

step "2/6 GitHub CLI (gh)"
if command -v gh >/dev/null; then ok "gh $(gh --version | head -1 | cut -d' ' -f3)"
else ask "Instalar gh con brew?" && brew install gh || die "gh es necesario"; fi

step "3/6 Node.js y Python 3"
command -v node >/dev/null && ok "node $(node --version)" || { ask "Instalar node con brew?" && brew install node || die "node es necesario"; }
command -v python3 >/dev/null && ok "python3 $(python3 --version | cut -d' ' -f2)" || { ask "Instalar python con brew?" && brew install python || die "python3 es necesario"; }

step "4/6 Google Workspace CLI (gws)"
if command -v gws >/dev/null; then ok "gws $(gws --version 2>&1 | head -1 | cut -d' ' -f2)"
else ask "Instalar con 'npm install -g @googleworkspace/cli'?" && npm install -g @googleworkspace/cli || die "gws es necesario"; fi

step "5/6 Sesión de GitHub"
if gh api user >/dev/null 2>&1; then ok "gh ya tiene sesión ($(gh api user --jq .login))"
else
  warn "Se abrirá el flujo de gh: elige GitHub.com, protocolo SSH (sube tu llave pública) y autoriza en el navegador."
  gh auth login || die "No se pudo iniciar sesión en gh"
fi
if gh api repos/blacksip/blacksip-co-tech-manager-skills --jq .name >/dev/null 2>&1; then ok "acceso al repo de skills"
else warn "Sin acceso a blacksip/blacksip-co-tech-manager-skills: pide que te agreguen al equipo tech-managers."; fi
if git ls-remote git@github.com:blacksip/blacksip-co-tech-manager-skills.git HEAD >/dev/null 2>&1; then ok "acceso por SSH (lo usa /plugin marketplace add)"
else warn "Falló git por SSH: ejecuta 'gh auth login' eligiendo SSH, o agrega tu llave en github.com/settings/keys."; fi

step "6/6 Sesión de Google (gws)"
if [[ ! -f "$GWS_DIR/client_secret.json" ]]; then
  warn "Falta $GWS_DIR/client_secret.json (cliente OAuth compartido de Blacksip)."
  echo "     Está en 1Password: bóveda \"Technology - TechManagers\", ítem \"gws – client_secret.json (Blacksip)\". Descarga el archivo adjunto (no está en el repo a propósito)."
  read -r -p "  Ruta del archivo descargado (arrástralo aquí, o Enter para salir): " src
  src="${src//\\ / }"; src="${src%\"}"; src="${src#\"}"; src="${src%\'}"; src="${src#\'}"; src="${src/#\~/$HOME}"
  [[ -f "$src" ]] || die "No encontré el archivo. Descárgalo y vuelve a ejecutar este script."
  grep -q '"installed"' "$src" || die "Ese archivo no parece un client_secret.json de tipo escritorio."
  mkdir -p "$GWS_DIR" && cp "$src" "$GWS_DIR/client_secret.json" && chmod 600 "$GWS_DIR/client_secret.json" && ok "client_secret.json instalado"
fi
if gws auth status 2>/dev/null | grep -q '"has_refresh_token": true'; then ok "gws ya tiene sesión"
else
  warn "Se abrirá el navegador: inicia sesión con tu cuenta @blacksip.com y acepta los permisos."
  gws auth login -s drive,docs || die "gws auth login falló"
fi
if gws drive files get --params "{\"fileId\":\"$TEMPLATE_ID\",\"supportsAllDrives\":true,\"fields\":\"name\"}" >/dev/null 2>&1
then ok "acceso a la plantilla de acta en Drive"
else warn "No se pudo leer la plantilla de acta en Drive: pide acceso a la carpeta 'Template' o reintenta 'gws auth login'."; fi

step "Listo"
echo "  Claude Code: instala el plugin dentro de Claude Code:"
echo "    /plugin marketplace add blacksip/blacksip-co-tech-manager-skills"
echo "    /plugin install tm-actas@blacksip-co-tech-manager-skills"
echo "  opencode (sin Claude Code): bash scripts/install-opencode.sh"
