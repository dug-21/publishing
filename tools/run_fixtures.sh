#!/usr/bin/env bash
# Runs every failure fixture in tests/fixtures. A fixture passes when its make
# target FAILS and the output matches the expected message. The "valid" fixture
# is the baseline and must pass.
set -u
failed=0
for dir in tests/fixtures/*/; do
  name=$(basename "$dir")
  TARGET= EXPECT= VARS=
  # shellcheck disable=SC1090
  source "$dir/fixture.conf"
  src_args=()
  [[ -f "$dir/standard.adoc" ]] && src_args=(SRC="${dir%/}")
  # shellcheck disable=SC2086
  output=$(make --no-print-directory $TARGET "${src_args[@]}" BUILD="build/fixtures/$name" LANGS=en $VARS 2>&1)
  status=$?
  if [[ "$EXPECT" == PASS ]]; then
    if [[ $status -eq 0 ]]; then echo "ok    $name (passes, as a valid baseline should)"
    else echo "FAIL  $name: the valid baseline did not pass"; echo "$output" | tail -5 | sed 's/^/        /'; failed=1; fi
  elif [[ $status -eq 0 ]]; then
    echo "FAIL  $name: '$TARGET' passed but should have failed"; failed=1
  elif ! grep -Eq -- "$EXPECT" <<<"$output"; then
    echo "FAIL  $name: '$TARGET' failed, but not with the expected message /$EXPECT/"
    echo "$output" | tail -5 | sed 's/^/        /'; failed=1
  else
    echo "ok    $name ('$TARGET' fails: $(grep -E -m1 -- "$EXPECT" <<<"$output" | cut -c1-110))"
  fi
done
[[ $failed -eq 0 ]] && echo "All fixtures behaved as expected." || echo "Some fixtures did not behave as expected."
exit $failed
