# Viper CFD Workflow Automation

This repository provides a set of Python scripts and Tecplot macros to automate the process of running CFD simulations using Viper, generating visualizations, analyzing results, and collecting data for frequency response analysis.

This is a highly specific set of code for an analysis of a specific fluidic amplifier as part of an assignment completed for MEC5881 at Monash University. Some of it may be useful for your own Viper spectral sims, but it will likely require a notable amount of work to apply it to your own application.

## Use Case

This workflow is specifically designed for studying the frequency response of a fluidic amplifier.  It enables you to run multiple simulations with varying parameters (e.g., Reynolds number, control frequency, mesh resolution), automatically visualize the flow fields in Tecplot, analyze the time-dependent data, calculate system gain, and consolidate the results into a single CSV file for further processing.


## Setup

1. **Prerequisites:**
   - **Viper:** Install the [Viper CFD solver](https://sheardlab.org/research/viper.php) and ensure `viper.exe` is in the root directory.
   - **Tecplot:** Install Tecplot 360 EX with the Python library (`tecplot`).
   - **Python:**  Python 3.x with the following packages: `csv`, `os`, `shutil`, `subprocess`, `time`, `math`, `sys`, `re`, `numpy`, `pandas`, `matplotlib`.  You can install them using `pip install -r requirements.txt` (create a `requirements.txt` file listing these packages).


2. **Directory Structure:**
   - Place all the provided Python scripts (`run_viper_simulations.py`, `tecplot_export.py`, `batch_tecplot_export.py`, `analyse_static_data.py`, `analyse_static_data_freq.py`, `batch_data_analyse.py`, `batch_data_analyse_freq.py`, `copy_sim_folders.py`, `data_collect.py`) in your root directory.
   - Create a file named `parameters.csv` in the root directory.  This file should contain the simulation parameters, with the first row specifying the parameter names (see the example below).
   - Place your Viper configuration file (`viper.cfg`) and the Tecplot macro files (`macro.txt`, `macro_animation.txt`) in the root directory.
   - Place the required mesh files (e.g., `fluidic_amplifier_res_1.msh`, `fluidic_amplifier_res_2.msh`, etc.) in the root directory.

3. **`parameters.csv` Format:**
   - The first row must contain the parameter names. Include a description row as a comment if needed.
   - Each subsequent row represents a simulation run with a specific set of parameters.

   ```csv
   # Index,Reynolds number,mesh_file,Polynomial order,Control amplitude,Control frequency,Control up-down balance,Time step,Animation loops,End time,Verbose,Convergence criteria,Override
   1,100,1,3,0.001,1,0,0.0001,50,0.5,y,,n
   2,100,2,3,0.002,1,0,0.0001,50,0.5,y,,n
   # ... more simulation parameters ...