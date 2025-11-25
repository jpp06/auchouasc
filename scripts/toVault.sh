#! /usr/bin/env bash

ROOT_DIR=$(cd $(dirname $0)/..; pwd)
DST_DIR=/mnt/c/Users/zezz0/Documents/Ascension/WoW/Ascension

if [ ! -d ${DST_DIR} ]; then
  DST_DIR=/Volumes/CaseSens/Work/Obsidian/WoW/Ascension
fi

if [ ! -d ${DST_DIR} ]; then
  echo "*** No destination dir found." >&2
  exit 1
fi

rm -rf ${DST_DIR}/index.md ${DST_DIR}/items
cp obsidian/index.md ${DST_DIR}
cp -r obsidian/items ${DST_DIR}

