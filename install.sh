#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "=========================================================="
echo " Installing Investment Tools Suite for Antigravity"
echo "=========================================================="
echo "Repository Root: ${REPO_ROOT}"

# 1. Global Plugin Registration
PLUGINS_DIR="${HOME}/.gemini/config/plugins"
mkdir -p "${PLUGINS_DIR}"
PLUGIN_TARGET="${PLUGINS_DIR}/investment-tools"

if [ -e "${PLUGIN_TARGET}" ] || [ -L "${PLUGIN_TARGET}" ]; then
    echo "[OK] Plugin link already exists at: ${PLUGIN_TARGET}"
else
    echo "[*] Creating plugin symlink: ${PLUGIN_TARGET} -> ${REPO_ROOT}"
    ln -s "${REPO_ROOT}" "${PLUGIN_TARGET}"
    echo "[OK] Plugin registered successfully!"
fi

# 2. Individual Skills Registration
SKILLS_DIR="${HOME}/.gemini/config/skills"
mkdir -p "${SKILLS_DIR}"

for skill in "portfolio-tracker" "stock-deep-dive" "deep-value-hunter"; do
    src="${REPO_ROOT}/skills/${skill}"
    dest="${SKILLS_DIR}/${skill}"
    if [ -e "${dest}" ] || [ -L "${dest}" ]; then
        echo "[OK] Skill '${skill}' already linked at: ${dest}"
    else
        if [ -d "${src}" ]; then
            echo "[*] Linking skill '${skill}' -> ${dest}"
            ln -s "${src}" "${dest}"
            echo "[OK] Skill '${skill}' linked successfully!"
        fi
    fi
done

echo ""
echo "[SUCCESS] Investment Tools installation complete!"
echo "Note: Antigravity caches the global skill catalog at IDE startup."
echo "If running inside an active Antigravity session, restart the IDE to reload."
