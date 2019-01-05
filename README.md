# artificial_pancreas_project: 
This project simulates a closed loop system with a patient model and an artificial pancreas simulator. The main scripts in this directory those are necessary to run the simulation are 
initialize_system.py, run_simulation.py and collect_result.py. These scripts are writen to run the open source artificial pancrease controller called "OpenAPS" with 
another open soure patient simulator called glucosym. However this controller can be integrated to any other patient simulator. In that case, 
the scripts should be modified accordingly. To run the system, one must have openaps and glucosym installed in his/her machine.
