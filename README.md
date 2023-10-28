# Linear Integer Programming (Operational Research)

This repository contains code for solving worker assignment problems using operational research techniques. The primary problem involves assigning workers to work orders while considering various constraints, such as the number of available workers, maximum days worked, and daily shift limits.

## Problem Description

In many real-world scenarios, it's essential to efficiently allocate workers to different tasks while adhering to specific constraints. The worker assignment problem tackled in this repository deals with:

- **Worker Constraints**: Ensuring that the number of assigned workers meets specific requirements.
- **Workload Limits**: Managing the maximum number of days a worker can be scheduled to work.
- **Shift Scheduling**: Controlling the daily shift limits for workers.
- **Non compatible orders**: Ensuring that no worker completes two non compatible orders in a row.
- **Pipeline orders**: Ensuring orders are made in the correct order.

## Repository Structure

The repository is organized as follows:

- **/data/**: This directory may contain input data files or problem instances that can be used for testing and solving the worker assignment problem.

  - **/output/**: contains json files with the summary of the processes runs

- **/src/**: This directory contains the source code for generating problem instances and solving them. Key files include:

  - `week_generator.py`: Code for generating random problem instances to be solved.
  - `workers_assigner.py`: The main module responsible for modeling and solving the worker assignment problem.

## Usage

To use the code in this repository, follow these general steps:

1. Ensure you have the necessary dependencies and libraries installed. You might need Python and specific libraries like mathematical optimization solvers depending on the techniques used.

2. Use the sample data provided or run the `week_generator.py` module to generate problem instances.

```
python3 week_generator.py 10 5 2 2 new_week_10.txt
```

3. Use the `workers_assigner.py` module to model and solve the worker assignment problem based on the generated instances.

```
python3 workers_assigner.py ../data/new_week_1000.txt 1000_orders_df df
```