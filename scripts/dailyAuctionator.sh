#! /usr/bin/env bash

VARS_DIR='/mnt/c/Program Files/Ascension Launcher/resources/client/WTF/Account/zezz06@orange.fr/SavedVariables'
if [ ! -d "${VARS_DIR}" ]; then
    echo "*** Error: VARS_DIR does not exist: ${VARS_DIR}" >&2
    exit 1
fi
ROOT_DIR=$(cd $(dirname $0)/..; pwd)
SAVE_DIR=${ROOT_DIR}/dailies

NOW_DIR=${SAVE_DIR}/$(date -u +"%Y_%m_%dT%H_%M_%S")
mkdir -p ${NOW_DIR}

cd "${VARS_DIR}/"
cp Auctionator_Price_Database.lua ${NOW_DIR}
cp TradeSkillMaster_Accounting.lua TradeSkillMaster_AuctionDB.lua TradeSkillMaster_Shopping.lua ${NOW_DIR}
cp AHScanner.lua ${NOW_DIR}
