# ED7 paused at 18:49 UTC 2026-11-11

Stopped by request after two of six conditions (none-8, none-16), so the machine could run a test of larger
adapters first. none-32 had run for about two minutes and saved no fit. Nothing frozen changes. To resume:

    python3 poc/tools/lora_trade.py run poc/results/ed7/run/config.json poc/results/ed7/run 2>&1 \
      | grep -v "^\[transformers\]" >> poc/results/ed7/run/run.log

(append, `>>`, so the first part of the log is kept). The pause will be named in the results as a departure.
