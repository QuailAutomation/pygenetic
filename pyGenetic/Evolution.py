from abc import ABC, abstractmethod
import random
import math
import numpy as np
#import pyspark

class BaseEvolution(ABC):

	def __init__(self,max_iterations):
		self.max_iterations = max_iterations

	@abstractmethod
	def evolve(self,ga):
		pass

class StandardEvolution(BaseEvolution):

	def __init__(self,max_iterations=100,adaptive_mutation=True,pyspark=False):
		BaseEvolution.__init__(self,max_iterations)
		self.adaptive_mutation = adaptive_mutation
		self.pyspark = pyspark

	def __evolve_normal(self,ga):
		# get (1-r) * cross_prob new members
		ga.population.new_members = ga.handle_selection()

		print("Best fitness = ",ga.best_fitness[1])
		if ga.best_fitness[1] == ga.fitness_threshold:
			return 1

		fitnesses = []
		total = 0 #This is not being used
		for chromosome in ga.population.members:
			fitness = ga.calculateFitness(chromosome)
			if fitness == 0:
				fitness = random.uniform(0.01, 0.02)
			total += fitness
			fitnesses.append(fitness)

		p = [ elem/sum(fitnesses) for elem in fitnesses]
		#print("p = ",p)
		n = math.ceil(ga.cross_prob * len(p))
		if n %2 == 1:
			n -= 1
			ga.population.members.append(ga.population.members[0])

		crossover_indexes = np.random.choice(len(p),n,p=p, replace=False)
		print("crossover_indices = ",crossover_indexes)

		crossover_chromosomes = [ ga.population.members[index] for index in crossover_indexes]

		for i in range(0,len(crossover_chromosomes)-1,2):
			father,mother = crossover_chromosomes[i], crossover_chromosomes[i+1]
			crossoverHandler = ga.chooseCrossoverHandler()
			child1, child2 = crossoverHandler(father,mother)
			ga.population.new_members.extend([child1,child2])
		print("adaptive_mutation value passed = ",self.adaptive_mutation)
		if self.adaptive_mutation == True:
			mean_fitness = sum(fitnesses)/len(fitnesses)
			average_square_deviation = math.sqrt(sum((fitness - mean_fitness)**2 for fitness in fitnesses)) / len(fitnesses)
			ga.dynamic_mutation = ga.mut_prob * ( 1 + ( (ga.best_fitness[1]-average_square_deviation) / (ga.best_fitness[1]+average_square_deviation) ) )
			print('Adaptive mutation value = ',ga.dynamic_mutation)
			mutation_indexes = np.random.choice(len(ga.population.new_members),int(ga.dynamic_mutation*len(p)), replace=False)
		else:
			mutation_indexes = np.random.choice(len(ga.population.new_members),int(ga.mut_prob*len(p)), replace=False)
		for index in mutation_indexes:
			mutationHandler = ga.chooseMutationHandler()
			ga.population.new_members[index] = mutationHandler(ga.population.new_members[index])
		ga.population.members = ga.population.new_members
		#print("New members = ",ga.population.members)
		ga.population.new_members = []

	def __evolve_pyspark(self,ga):
		from pyspark import SparkContext
		sc = SparkContext.getOrCreate()
		print(ga.population.members)
		chromosomes_rdd = sc.parallelize(ga.population.members)
		# Fitness Value Mapping and making selection
		mapped_chromosomes_rdd = chromosomes_rdd.map(lambda x: (x,ga.fitness_func(x)))
		print(mapped_chromosomes_rdd.collect())
		selected_chromosomes = mapped_chromosomes_rdd.takeOrdered(len(ga.population.members)-math.ceil(ga.cross_prob * len(ga.population.members)),key=lambda x: -x[1])
		print(selected_chromosomes)
		ga.population.new_members = selected_chromosomes

		#n = math.ceil(ga.cross_prob * len(ga.population.members))
		#if n %2 == 1:
		#	n -= 1
		#	ga.population.members.append(ga.population.members[0])
		# Crossover Mapping
		#crossover_indexes = np.random.choice(len(ga.population.members),n,p=p, replace=False)
		#print("crossover_indices = ",crossover_indexes)
		#crossover_chromosomes = [ ga.population.members[index] for index in crossover_indexes]








	def evolve(self,ga):
		#print(self.max_iterations)
		if self.pyspark == False:
			if self.__evolve_normal(ga):
				return 1
		else:
			if self.__evolve_pyspark(ga):
				return 1
