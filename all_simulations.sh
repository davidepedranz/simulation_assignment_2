#!/usr/bin/env bash

################################################################
# SETUP
################################################################

echo -e "\nClean output folder..."
rm -rf output
mkdir output

echo "Create log file, for debug purpose..."
rm -f debug.log
touch debug.log

echo "Backup original configuration file..."
mv simulator/config.json simulator/config.json.original


################################################################
# ALOHA
################################################################

echo -e "\nAloha"
git checkout aloha 2>> debug.log

echo " -> original propagation..."
sed -e '/"propagation":/s/\([a-z:]*\)/original/7' \
    -e '/"simulator":/s/\([a-z:]*\)/aloha/7' \
    -e '/"output":/s/\.{persistence}//1' \
    simulator/config.json.original > simulator/config.json
git checkout aloha 2> debug.log
make >> debug.log

echo " -> realistic propagation..."
sed -e '/"propagation":/s/\([a-z:]*\)/realistic/7' \
    -e '/"simulator":/s/\([a-z:]*\)/aloha/7' \
    -e '/"output":/s/\.{persistence}//1' \
    simulator/config.json.original > simulator/config.json
make >> debug.log

sleep 10


################################################################
# TRIVIAL CARRIER SENSING
################################################################

echo -e "\nTrivial Carrier Sensing"
git checkout trivial 2>> debug.log

echo " -> original propagation..."
sed -e '/"propagation":/s/\([a-z:]*\)/original/7' \
    -e '/"simulator":/s/\([a-z:]*\)/trivial/7' \
    -e '/"output":/s/\.{persistence}//1' \
    simulator/config.json.original > simulator/config.json
make >> debug.log

echo " -> realistic propagation..."
sed -e '/"propagation":/s/\([a-z:]*\)/realistic/7' \
    -e '/"simulator":/s/\([a-z:]*\)/trivial/7' \
    -e '/"output":/s/\.{persistence}//1' \
    simulator/config.json.original > simulator/config.json
make >> debug.log

sleep 10


################################################################
# SIMPLE CARRIER SENSING
################################################################

echo -e "\nSimple Carrier Sensing (p = 0.5)"
git checkout simple 2>> debug.log

echo " -> original propagation..."
sed -e '/"propagation":/s/\([a-z:]*\)/original/7' \
    -e '/"simulator":/s/\([a-z:]*\)/simple/7' \
    -e '/"persistence":/s/\([0-9].[0-9]\)/0.5/1' \
    simulator/config.json.original > simulator/config.json
make >> debug.log

echo " -> realistic propagation..."
sed -e '/"propagation":/s/\([a-z:]*\)/realistic/7' \
    -e '/"simulator":/s/\([a-z:]*\)/simple/7' \
    -e '/"persistence":/s/\([0-9].[0-9]\)/0.5/1' \
    simulator/config.json.original > simulator/config.json
make >> debug.log

sleep 10


################################################################
# PROCESS
################################################################

python process/process.py


################################################################
# CLEANUP
################################################################

echo -e "\nRestoring original configuration file...\n"
mv simulator/config.json.original simulator/config.json
git checkout master 2>> debug.log
rm debug.log
