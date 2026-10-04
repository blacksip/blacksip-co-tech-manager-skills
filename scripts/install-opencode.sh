#!/usr/bin/env bash
# Instala o actualiza las skills de Blacksip en opencode, sin necesidad de Claude Code.
# Idempotente: volver a ejecutarlo actualiza las skills (git pull + copia).
set -eu

REPO_URL="git@github.com:blacksip/blacksip-co-tech-manager-skills.git"
CLONE_DIR="${CLONE_DIR:-$HOME/.local/share/blacksip-co-tech-manager-skills}"
SKILLS_DIR="${OPENCODE_SKILLS_DIR:-${XDG_CONFIG_HOME:-$HOME/.config}/opencode/skills}"

ok()   { printf '  \033[32m✔\033[0m %s\n' "$*"; }
warn() { printf '  \033[33m!\033[0m %s\n' "$*"; }
die()  { printf '  \033[31m✘\033[0m %s\n' "$*"; exit 1; }

printf '\n\033[1m1/3 Descargando skills\033[0m\n'
command -v git >/dev/null || die "Falta git."
if [[ -d "$CLONE_DIR/.git" ]]; then
  git -C "$CLONE_DIR" pull -q --ff-only || die "No se pudo actualizar $CLONE_DIR"
  ok "repositorio actualizado"
else
  mkdir -p "$(dirname "$CLONE_DIR")"
  git clone -q "$REPO_URL" "$CLONE_DIR" || die "No se pudo clonar. Revisa el acceso por SSH: ejecuta scripts/setup.sh o 'gh auth login' (SSH)."
  ok "repositorio clonado en $CLONE_DIR"
fi

printf '\n\033[1m2/3 Copiando skills a %s\033[0m\n' "$SKILLS_DIR"
mkdir -p "$SKILLS_DIR"
n=0
for d in "$CLONE_DIR"/plugins/*/skills/*/; do
  [[ -f "$d/SKILL.md" ]] || continue
  name="$(basename "$d")"
  rm -rf "${SKILLS_DIR:?}/$name" && cp -R "${d%/}" "$SKILLS_DIR/$name"
  ok "$name"; n=$((n+1))
done
[[ $n -gt 0 ]] || die "No se encontró ninguna skill en el repositorio."

printf '\n\033[1m3/3 Verificación\033[0m\n'
command -v opencode >/dev/null && ok "opencode $(opencode --version 2>/dev/null | head -1)" \
  || warn "opencode no está instalado: curl -fsSL https://opencode.ai/install | bash"

cat <<MSG

Listo: $n skills instaladas. Reinicia opencode para que las detecte.

Pendiente (una sola vez):
  - Requisitos (gh, gws, sesión de Google): bash "$CLONE_DIR/scripts/setup.sh"
  - Para leer notas de Granola, agrega su MCP en opencode.json (sección "mcp").
Para actualizar en el futuro, vuelve a ejecutar este mismo script.
MSG
