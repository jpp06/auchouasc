#! /usr/bin/env bash

PYTHON_VERSION=3.12
trap 'die' INT TERM
#trap 'kill -PIPE 0' EXIT

ROOT_DIR=$(cd `dirname $0`/..; pwd)
VENV_DIR=${ROOT_DIR}/venv
VENDOR_DIR=${ROOT_DIR}/vendor

install_venv=

if [ "$ROOT_DIR/requirements.txt" -nt "${VENDOR_DIR}" ]; then
  python${PYTHON_VERSION} -m pip download -r requirements.txt --no-binary=:none: -d "${VENDOR_DIR}"
  install_venv=1
fi

if [ ! -d "${VENV_DIR}" ]; then
  mkdir "${VENV_DIR}"
  python${PYTHON_VERSION} -m venv "${VENV_DIR}"
  install_venv=1
fi

if [ ! -z "${install_venv}" ]; then
  ${ROOT_DIR}/venv/bin/pip3 install \
                  -r "${ROOT_DIR}"/requirements.txt \
                  --no-index --find-links file://"${VENDOR_DIR}"
fi

die() {
    echo "error: $*" >&2b
    exit 255
}
#export REQUESTS_CA_BUNDLE=${ROOT_DIR}/ca-certificates.crt
if [ -z "$1" ]; then
  exec ${ROOT_DIR}/venv/bin/python3 ${ROOT_DIR}/pptxExtractor/main.py --help || die "$0 failed"
else
  #PROF="-m cProfile"
  exec ${ROOT_DIR}/venv/bin/python3 ${PROF} "$@" || die "$0 failed"
fi
