#!/usr/bin/env bash

simulate() {
	echo "Running simulations in parallel..."
	python simulator/main.py -l | shuf | parallel -j 7 --no-notice
}

do_simulator_no_p() {
	echo " -> original propagation..."
	python ./utils/configure.py "original" "$1" > simulator/config.json
	simulate >> debug.log

	echo " -> realistic propagation..."
	python ./utils/configure.py "realistic" "$1" > simulator/config.json
	simulate >> debug.log
}

do_simulator_p() {
	echo " -> original propagation..."
	python ./utils/configure.py "original" "$1" "$2" > simulator/config.json
	make >> debug.log

	echo " -> realistic propagation..."
	python ./utils/configure.py "realistic" "$1" "$2" > simulator/config.json
	make >> debug.log
}

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

echo ""
echo "Aloha"
git checkout aloha 2>> debug.log
do_simulator_no_p "aloha"


################################################################
# TRIVIAL CARRIER SENSING
################################################################

echo ""
echo "Trivial"
git checkout trivial 2>> debug.log
do_simulator_no_p "trivial"


################################################################
# SIMPLE CARRIER SENSING
################################################################

echo ""
echo "Simple Carrier Sensing (p = 0.0)"
git checkout simple 2>> debug.log
do_simulator_p "simple" "0.0"

echo ""
echo "Simple Carrier Sensing (p = 0.25)"
git checkout simple 2>> debug.log
do_simulator_p "simple" "0.25"

echo ""
echo "Simple Carrier Sensing (p = 0.5)"
git checkout simple 2>> debug.log
do_simulator_p "simple" "0.5"

echo ""
echo "Simple Carrier Sensing (p = 0.75)"
git checkout simple 2>> debug.log
do_simulator_p "simple" "0.75"

echo ""
echo "Simple Carrier Sensing (p = 1.0)"
git checkout simple 2>> debug.log
do_simulator_p "simple" "1.0"


################################################################
# PROCESS
################################################################

git checkout master 2>> debug.log
python utils/process.py


################################################################
# CLEANUP
################################################################

echo ""
echo "Restoring original configuration file..."
echo ""
mv simulator/config.json.original simulator/config.json
git checkout master 2>> debug.log
rm debug.log
