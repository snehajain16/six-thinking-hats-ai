#!/bin/sh
set -e

OLLAMA_URL="${OLLAMA_URL:-http://localhost:11434}"
MODEL="${OLLAMA_MODEL:-llama3}"

echo "Waiting for Ollama at $OLLAMA_URL..."
until wget -qO- "$OLLAMA_URL/api/tags" > /dev/null 2>&1; do
  sleep 2
done
echo "Ollama is ready."

echo "Pulling model: $MODEL"
wget -qO- \
  --post-data="{\"name\":\"$MODEL\"}" \
  --header="Content-Type: application/json" \
  "$OLLAMA_URL/api/pull" > /dev/null || {
    echo "ERROR: Failed to pull model $MODEL"
    exit 1
  }
echo "Model $MODEL ready."

echo "Starting API..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
