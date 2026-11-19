#!/bin/bash
u=$1; D=$2; slug=$(basename "$u"); f=$D/$slug.html
[ -s "$f" ] && grep -q app-title "$f" && exit 0
for t in 1 2 3 4 5; do
  code=$(curl -sS -A "Mozilla/5.0 (research)" -o "$f" -w "%{http_code}" "$u")
  [ "$code" = 200 ] && grep -q app-title "$f" && { sleep 0.4; exit 0; }
  sleep $((t*6))
done
echo "FAIL $u $code" >> $D/../fail.log
