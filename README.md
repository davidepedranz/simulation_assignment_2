# Python Simulator Extension
This repository contains the solution of the Assignment 2 of [Simulation and Performance Evaluation](http://disi.unitn.it/locigno/teaching-duties/spe/),
winter 2016 - 2017, University of Trento.

The current version of the simulator is Simple Carrier Sensing with Realistic Propagation.
You can checkout the Aloha and Trivial Carrier Sensing using the git tags `aloha`, `trivial` (or even `simple` for the latest version).

## Assignment
We started from a Python simulator (provided by Michele Segata - teaching assistant) for the Aloha MAC access protocol and extend it to implement some other protocol.
The complete text of the assignment can be found in the [assignment.pdf](assignment.pdf) file.

## Simulator
The simulator is written in plain Python 2, so nothing special is required to run it.
The run parameter are described with a JSON configuration file. By default, the simulator tries to load the file `config.json` from the `simulator` folder.
An example JSON file is provided in the `run` folder.

Instruction to run the simulator can be obtained using:
```bash
python simulator/main.py -h
```

Multiple simulations can be executed at the same time using the amazing GNU Parallel utility:
```bash
python simulator/main.py -l | parallel -j 7 --no-notice
```

### Processing
Each simulation produces a log file. Log files are processed to compute some metrics to evaluate the performances of the various protocols (see [report.pdf](report.pdf)).
We use [Pandas](http://pandas.pydata.org/) for data processing and [Matplotlib](http://matplotlib.org/) to plot the results.
Make sure to install all the needed Python [packages](utils/requirments.txt) before running the processing script.
After running the simulations, you can run the `process.py` script to process the data.
The results will be available in the `results` folder.
```bash
python utils/process.py
```

### Results
The `run` folder contains the configuration file used to run the simulations and the computed metrics.
You can run the following commands to process the results of the simulations without running them:

```bash
mkdir results
cp run/statistics.h5 results/statistics.h5
python utils/process.py
```

To run all the simulations, you can use the `all_simulations.sh` bash file.
Please note that the script will checkout old versions of the simulators using git tags.
If you interrupt the script for some reason, make sure to checkout the master branch.

```bash
cp run/config.json utils/config.json
bash all_simulations.sh
```

## Report
The simulator logic and all results are discussed in details in the report.
The `report` folder contains the LaTeX sources, plots and diagrams.

## License
The simulator code and the processing scripts are licenced under the [GNU General Public Licence](https://www.gnu.org/licenses/gpl-3.0.en.html).
The report and its LaTeX code are licenced under the Creative Commons [Attribution-ShareAlike 4.0 International](https://creativecommons.org/licenses/by-sa/4.0/) License.
