#!/bin/bash
set -e

echo "🔧 Instalando dependências Python..."
pip install --upgrade pip
pip install -r requirements_api.txt

echo "✅ Build completo!"
