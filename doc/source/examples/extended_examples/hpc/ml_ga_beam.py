# Copyright (C) 2024 ANSYS, Inc. and/or its affiliates.
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
Genetic Algorithms and PyMAPDL
==============================

This example aims also to show how to use PyMAPDL in an HPC cluster, to
take advantage of multiple MAPDL instances to calculate each of the
genetic algorithm population solution.
To manage multiple MAPDL instances, it is recommended to use the
MapdlPool class which allows you to run multiple jobs on the background.

"""

# Problem definition
# ==================


def calculate_beam(mapdl, force):
    # Initializing
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

    # Setting FEM model
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

    # constrain just nodes 1 and 23 in the Z direction
    mapdl.d(1, "UZ")
    mapdl.d(23, "UZ")

    # apply a -Z force at node 12
    mapdl.f(12, "FZ", force[0])

    # run the static analysis
    mapdl.run("/solu")
    mapdl.antype("static")
    mapdl.solve()

    # Extracting data
    UZ = mapdl.post_processing.nodal_displacement("Z")
    UZ_node_12 = UZ[12]

    return UZ_node_12


# Setting MAPDL pool
# ==================

from ansys.mapdl.core import MapdlPool

# Starting pool
# Number of instances should be equal to number of CPUs
# as set later in the ``sbatch`` command
pool = MapdlPool(n_instances=10)
print(pool)


## Define deflection target
# Calculate target displacement
mapdl = pool[0]
force = 22840  # N/cm2
target_displacement = calculate_beam(pool[0], [force])
print(f"Setting target to {target_displacement} for force {force}")

# Setting genetic algorithm
# =========================

# Setting GA model
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


# To calculate the error in the model solution with respect to the target displacement.
def calculate_error(model_output):
    # Just for visualization purposes.
    return 100.0 * (model_output - target_displacement) / target_displacement


# This function is executed at the end of the fitness stage (all chromosomes are calculated),
# and it is used to do some pretty printing.
def on_fitness(pyga_instance, solution):
    # This attribute does not exist. It will be created after the GA class has been initialized.
    pyga_instance.igen += 1
    print(f"\nGENERATION {pyga_instance.igen}")
    print("=============")


# Fitness function


def fitness_func(ga_instance, solution, solution_idx):
    # Querying a free MAPDL instance
    mapdl, i = pool.next_available(return_index=True)
    mapdl.locked = True
    mapdl._busy = True

    # Perform chromosome simulation
    model_output = calculate_beam(mapdl, solution)

    # Releasing MAPDL instance
    mapdl.locked = False
    mapdl._busy = False

    # Calculate errors and criteria
    error_ = calculate_error(model_output)
    fitness_criteria = calculate_fitness_criteria(model_output)

    # Pretty print at each chromosome solution
    # The 'port' is printed so it can be observed how the GA is using all MAPDL instances
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
)

ga_instance.igen = 0  # To count the number of generations


# Run simulation
# ==============

import time

t0 = time.perf_counter()

ga_instance.run()

t1 = time.perf_counter()
print(f"Time spent (minutes): {(t1-t0)/60}")


# Plot convergence
# ================

ga_instance.plot_fitness(label=["Applied force"], save_dir=os.getcwd())

solution, solution_fitness, solution_idx = ga_instance.best_solution(
    ga_instance.last_generation_fitness
)

print(f"Parameters of the best solution : {solution[0]}")
print(f"Fitness value of the best solution = {solution_fitness}")


# Storing the model result
# ========================

from datetime import datetime

# Saving the GA instance.
# The filename to which the instance is saved. The name is without extension.
formatted_date = datetime.now().strftime("%d-%m-%y")
filename = f"ml_ga_beam_{formatted_date}"
ga_instance.save(filename=filename)

# Loading the saved GA instance.
loaded_ga_instance = pygad.load(filename=filename)

# Plot fitness function again
loaded_ga_instance.plot_fitness()
