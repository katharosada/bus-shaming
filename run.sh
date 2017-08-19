#!/bin/bash
ROOT=$(cd $(dirname $0); pwd)

if echo "${1}" | egrep -q '\.py$|^-'; then
 COMMAND="${1}"
 shift
else
 COMMAND="${ROOT}/manage.py"
fi
env DJANGO_SETTINGS_MODULE=busshaming.settings PYTHONPATH=. python "${COMMAND}" "${@}"
