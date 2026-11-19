#!/bin/bash
D=$1
for p in $(seq 1 88); do
  f=$D/p$p.html
  [ -s $f ] && grep -q link-to-software $f && continue
  for try in 1 2 3 4; do
    curl -sS -A "Mozilla/5.0 (research)" -o $f "https://start-developer-competition-26.devpost.com/project-gallery?page=$p" && grep -q link-to-software $f && break
    sleep $((try*5))
  done
  sleep 1.5
done
echo done
