#!/usr/bin/env bash
set -eu

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo"

if [[ ! -d .git ]]; then
  echo '[FAIL] Not at a git repository'
  exit 1
fi

printf '\n[1] Working tree (review any results)\n'
git status --short

printf '\n[2] Remote\n'
git remote -v || true

printf '\n[3] Required files\n'
for file in \
  ros2_ws/pixi.toml \
  ros2_ws/pixi.lock \
  ros2_ws/src/so101_bringup/launch/simulation_multi.launch.py \
  scripts/mac/start-so101-multi.sh \
  third_party_licenses/ros2_so_arm/LICENSE \
  third_party_licenses/SO-ARM100/LICENSE; do
  if [[ -f "$file" ]]; then
    printf 'OK   %s\n' "$file"
  else
    printf 'MISS %s\n' "$file"
  fi
done

printf '\n[4] Sensitive-looking tracked filenames (manual review)\n'
tracked="$(git ls-files | grep -Ei '(^|/)(id_rsa|id_ed25519|\.env|[^/]+\.pem|[^/]+\.key|[^/]+\.mcap|[^/]+\.db3|[^/]+\.bag)(/|$)|calibration' || true)"
if [[ -n "$tracked" ]]; then
  printf '%s\n' "$tracked"
else
  echo '(none matched)'
fi

printf '\n[5] Potential credentials in tracked text files (manual review)\n'
# Only paths are shown, not any matched secret strings.
if git grep -IlE -- '-----BEGIN (RSA|OPENSSH|EC) PRIVATE KEY-----|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|hf_[A-Za-z0-9]{30,}' 2>/dev/null; then
  echo 'Review the above files before pushing.'
else
  echo '(none matched by limited patterns)'
fi

printf '\n[6] Content origins requiring explicit human approval\n'
echo '- collision/*.stl derivation/license: NOT verified automatically'
echo '- own source-code license: NOT selected automatically'
echo '- full Git history review: NOT performed automatically'
echo '- cross-account clean-clone reproducibility: NOT tested automatically'
printf '\nIMPORTANT: This script cannot certify public-release readiness.\n'
