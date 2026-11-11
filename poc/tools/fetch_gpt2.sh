#!/usr/bin/env bash
# Fetch GPT-2 base (124M) from Hugging Face into DIR (default: $GPT2_HF_DIR or ./gpt2_hf), the four files
# poc/tools/lora_knee.py:load_model reads. Needs huggingface.co and its download hosts on the network allowlist.
set -euo pipefail
DIR="${1:-${GPT2_HF_DIR:-gpt2_hf}}"; mkdir -p "$DIR"
for f in config.json pytorch_model.bin vocab.json merges.txt; do
  [ -s "$DIR/$f" ] || curl -fL --retry 4 -o "$DIR/$f" "https://huggingface.co/openai-community/gpt2/resolve/main/$f"
done
ls -l "$DIR"
