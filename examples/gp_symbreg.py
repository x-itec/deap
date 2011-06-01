#    This file is part of EAP.
#
#    EAP is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of
#    the License, or (at your option) any later version.
#
#    EAP is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with EAP. If not, see <http://www.gnu.org/licenses/>.

import sys
import operator
import math
import logging
import random

from deap import algorithms
from deap import base
from deap import creator
from deap import tools
from deap import gp

# Define new functions
def safeDiv(left, right):
    try:
        return left / right
    except ZeroDivisionError:
        return 0

pset = gp.PrimitiveSet("MAIN", 1)
pset.addPrimitive(operator.add, 2)
pset.addPrimitive(operator.sub, 2)
pset.addPrimitive(operator.mul, 2)
pset.addPrimitive(safeDiv, 2)
pset.addPrimitive(operator.neg, 1)
pset.addPrimitive(math.cos, 1)
pset.addPrimitive(math.sin, 1)
pset.addEphemeralConstant(lambda: random.randint(-1,1))
pset.renameArguments({"ARG0" : "x"})

creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMin, pset=pset)

toolbox = base.Toolbox()
toolbox.register("expr", gp.generateRamped, pset=pset, min_=1, max_=2)
toolbox.register("individual", tools.fillIter, creator.Individual, toolbox.expr)
toolbox.register("population", tools.fillRepeat, list, toolbox.individual)
toolbox.register("lambdify", gp.lambdify, pset=pset)

def evalSymbReg(individual):
    # Transform the tree expression in a callable function
    func = toolbox.lambdify(expr=individual)
    # Evaluate the sum of squared difference between the expression
    # and the real function : x**4 + x**3 + x**2 + x
    values = (x/10. for x in xrange(-10,10))
    diff_func = lambda x: (func(x)-(x**4 + x**3 + x**2 + x))**2
    diff = sum(map(diff_func, values))
    return diff,

toolbox.register("evaluate", evalSymbReg)
toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("mate", gp.cxUniformOnePoint)
toolbox.register("expr_mut", gp.generateFull, min_=0, max_=2)
toolbox.register('mutate', gp.mutUniform, expr=toolbox.expr_mut)

def main():
    random.seed(318)
    
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

    pop = toolbox.population(n=300)
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("Avg", tools.mean)
    stats.register("Std", tools.std_dev)
    stats.register("Min", min)
    stats.register("Max", max)
    
    algorithms.eaSimple(toolbox, pop, 0.5, 0.1, 40, stats, halloffame=hof)
    logging.info("Best individual is %s, %s", gp.evaluate(hof[0]), hof[0].fitness)
    
    return pop, stats, hof

if __name__ == "__main__":
    main()
