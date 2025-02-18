# Copyright (C) 2016 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
==============================
Genetic algorithms and PyMAPDL
==============================

This example shows how to use PyMAPDL in an HPC cluster to
take advantage of multiple MAPDL instances to calculate each of the
genetic algorithm population solutions.
To manage multiple MAPDL instances, you should use the
``MapdlPool`` class, which lets you run multiple jobs in the background.

"""

# Problem definition
# ==================


# Calculate beam function
def calculate_beam(mapdl, force):
    # Initialize
    mapdl.clear()
    mapdl.prep7()

    # Define an I-beam
    mapdl.et(1, "BEAM188")
    mapdl.keyopt(1, 4, 1)  # transverse shear stress output

    # Material properties
    mapdl.mp("EX", 1, 2e7)  # N/cm2
    mapdl.mp("PRXY", 1, 0.27)  # Poisson's ratio

    # Beam properties in centimeters
    sec_num = 1
    mapdl.sectype(sec_num, "BEAM", "I", "ISection", 3)
    mapdl.secoffset("CENT")
    mapdl.secdata(15, 15, 29, 2, 2, 1)  # dimensions are in centimeters

    # Set FEM model
    mapdl.n(1, 0, 0, 0)
    mapdl.n(12, 110, 0, 0)
    mapdl.n(23, 220, 0, 0)
    mapdl.fill(1, 12, 10)
    mapdl.fill(12, 23, 10)

    for node in mapdl.mesh.nnum[:-1]:
        mapdl.e(node, node + 1)

    # Define the boundary conditions
    # Allow movement only in the X and Z direction
    for const in ["UX", "UY", "ROTX", "ROTZ"]:
        mapdl.d("all", const)

    # Constrain only nodes 1 and 23 in the Z direction
    mapdl.d(1, "UZ")
    mapdl.d(23, "UZ")

    # Apply a -Z force at node 12
    mapdl.f(12, "FZ", force[0])

    # Run the static analysis
    mapdl.run("/solu")
    mapdl.antype("static")
    mapdl.solve()

    # Extract data
    UZ = mapdl.post_processing.nodal_displacement("Z")
    UZ_node_12 = UZ[12]

    return UZ_node_12


# MAPDL pool setup
# =================
# Importing packages
from ansys.mapdl.core import MapdlPool

# Start pool
# Number of instances should be equal to number of CPUs
# as set later in the ``sbatch`` command
pool = MapdlPool(n_instances=10)
print(pool)

## Define deflection target
mapdl = pool[0]  # Getting the first MAPDL instance in the pool
force = 22840  # N/cm2
target_displacement = calculate_beam(pool[0], [force])
print(f"Setting target to {target_displacement} for force {force}")

# Genetic algorithm setup
# =======================

# Set GA model
sol_per_pop = 20
num_generations = 10
num_parents_mating = 20
num_genes = 1  # equal to the size of inputs/outputs.
parallel_processing = ["thread", len(pool)]  # Number of parallel workers

# Initial guess limits
init_range_low = 10000
init_range_high = 30000
gene_type = int  # limit to ints

# Extra configuration
# https://blog.derlin.ch/genetic-algorithms-with-pygad
parent_selection_type = "rws"
keep_parents = 0  # No keeping parents.
mutation_percent_genes = 30
mutation_probability = 0.5

# Helper functions
import numpy as np


# To calculate the fitness criteria model solution and target displacement
def calculate_fitness_criteria(model_output):
    # we add a constant (target/1E8) here to avoid dividing by zero
    return 1.0 / (
        1 * (np.abs(model_output - target_displacement) + target_displacement / 1e10)
    )


# To calculate the error in the model solution with respect to the target displacement
def calculate_error(model_output):
    # Only for visualization purposes
    return 100.0 * (model_output - target_displacement) / target_displacement


# This function is executed at the end of the fitness stage (all chromosomes are calculated),
# and it is used to do some printing.
def on_fitness(pyga_instance, solution):
    # This attribute does not exist. It is created after the GA class has been initialized.
    pyga_instance.igen += 1
    print(f"\nGENERATION {pyga_instance.igen}")
    print("=============")


# Fitness function


def fitness_func(ga_instance, solution, solution_idx):
    # Query a free MAPDL instance

    with pool.next(return_index=True) as (mapdl, i):

        # Perform chromosome simulation
        model_output = calculate_beam(mapdl, solution)

        # Calculate errors and criteria
        error_ = calculate_error(model_output)
        fitness_criteria = calculate_fitness_criteria(model_output)

        # Print at each chromosome solution
        # Print the port to observe how the GA is using all MAPDL instances
        print(
            f"MAPDL instance {i}(port: {mapdl.port})\tInput: {solution[0]:0.1f}\tOutputs: {model_output:0.7f}\tError: {error_:0.3f}%\tFitness criteria: {fitness_criteria:0.6f}"
        )

    return fitness_criteria


def mutation_func(offspring, ga_instance):
    average = offspring.mean()
    max_value = offspring.max() - average
    min_value = offspring.min() - average

    min_value = min([min_value, max_value, -1])
    max_value = max([min_value, max_value, +1])

    offspring[:, 0] += np.random.randint(min_value, high=max_value, size=offspring.size)

    for i in range(2):
        random_spring_idx = np.random.choice(range(offspring.shape[1]))
        sign = np.random.choice([-1, 1])
        offspring[random_spring_idx, 0] += sign * average * (0.1 * np.random.random())

    return offspring


import pygad

ga_instance = pygad.GA(
    # Main options
    sol_per_pop=sol_per_pop,
    num_generations=num_generations,
    num_parents_mating=num_parents_mating,
    num_genes=num_genes,
    fitness_func=fitness_func,
    parallel_processing=parallel_processing,
    random_seed=2,  # to get reproducible results
    #
    # Mutation
    mutation_percent_genes=mutation_percent_genes,
    mutation_type=mutation_func,
    mutation_probability=mutation_probability,
    #
    # Parents
    keep_parents=keep_parents,
    parent_selection_type=parent_selection_type,
    #
    # Helpers
    on_fitness=on_fitness,
    gene_type=gene_type,
    init_range_low=init_range_low,
    init_range_high=init_range_high,
    save_solutions=True,
)

ga_instance.igen = 0  # To count the number of generations


# Simulation
# ==========
# Measuring time
import time

t0 = time.perf_counter()

ga_instance.run()

t1 = time.perf_counter()
print(f"Time spent (minutes): {(t1-t0)/60}")


# Convergence plot
# ================
# To plot the convergence:
import os

ga_instance.plot_fitness(label=["Applied force"], save_dir=os.getcwd())

ga_instance.plot_genes(solutions="all")

solution, solution_fitness, solution_idx = ga_instance.best_solution(
    ga_instance.last_generation_fitness
)

print(f"Parameters of the best solution : {solution[0]}")
print(f"Fitness value of the best solution = {solution_fitness}")


# Model storage
# =============

# To save the model data:
from datetime import datetime

# Save the GA instance
# In the filename to save the instance to, do not specify the extension.
formatted_date = datetime.now().strftime("%d-%m-%y")
filename = f"ml_ga_beam_{formatted_date}"
ga_instance.save(filename=filename)

# Load the saved GA instance
loaded_ga_instance = pygad.load(filename=filename)

# Plot fitness function again
loaded_ga_instance.plot_fitness()
