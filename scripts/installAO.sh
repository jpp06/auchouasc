#! /usr/bin/env bash

AO_DIR='/mnt/c/Program Files/Ascension Launcher/resources/client/Interface/AddOns/AHScanner/'
if [ ! -d "${AO_DIR}" ]; then
    echo "*** Error: AO_DIR does not exist: ${AO_DIR}" >&2
    exit 1
fi
ROOT_DIR=$(cd $(dirname $0)/..; pwd)

cp "${ROOT_DIR}/AHScanner/"* "${AO_DIR}"
