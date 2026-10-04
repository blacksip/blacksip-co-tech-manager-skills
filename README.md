# blacksip-co-tech-manager-skills

Marketplace de plugins de Claude Code para los Tech Managers de Blacksip.

## Instalar

```
/plugin marketplace add blacksip/blacksip-co-tech-manager-skills
/plugin install tm-actas@blacksip-co-tech-manager-skills
```

## Actualizar

```
/plugin marketplace update blacksip-co-tech-manager-skills
```

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

`main` está protegida: todo cambio entra por pull request con al menos 1 aprobación.

1. Crea una rama desde `main` (`feat/<skill>` o `fix/<skill>`).
2. Agrega o edita la skill en `plugins/<plugin>/skills/<nombre>/SKILL.md`. Si es un plugin nuevo, regístralo en `.claude-plugin/marketplace.json`.
3. Sube `version` en el `plugin.json` del plugin afectado (si no, nadie recibe el cambio).
4. Revisa que no haya datos reales de clientes (nombres, emails, cifras) y que las rutas usen `${CLAUDE_PLUGIN_ROOT}`.
5. Abre el PR y pide revisión a otro Tech Manager.
6. Tras el merge, cada persona actualiza con `/plugin marketplace update blacksip-co-tech-manager-skills`.
