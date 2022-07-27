#!/bin/bash -e
# Usage: `./dev/lint.sh` before a commit

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
DIR=$(dirname "${DIR}")

if [[ -f "${DIR}/TARGETS" ]]
then
  pyfmt "${DIR}"
else
# run isort externally only
  echo "Running isort..."
  isort  "${DIR}"
fi

#echo "Running black..."
#black "${DIR}"

echo "Running flake..."
flake8 "${DIR}" || true