from abc import ABC, abstractmethod
import random
import math
import numpy as np
import Utils
#import pyspark

class BaseEvolution(ABC):
	"""
	Abstract class to be inherited to implement the specific evolution procedure

	Instance Members :
	------------------
	max_iterations ; int

	Methods :
	---------
	evolve() : abstract method to be implemeted by derived classes

	"""

	def __init__(self):
		pass

	@abstractmethod
	def evolve(self,ga):
		"""
		Abstract method to be implemeted by derived classes
		
		Parameters :
		-------------
		ga : reference to the GAEngine object

		"""

		pass

class StandardEvolution(BaseEvolution):
	"""
	Class inherits from BaseEvolution and contain implementations of abstract 
	evolution method in  BaseEvolution

	Instance Members :
	------------------

	max_iterations : int
	adaptive_mutation : boolean to indicated if rate of mutation should 
						change dynamically during each iteration
	pyspark : boolean to indicated if parallelization should be supported by using pyspark

	"""
	def __init__(self,adaptive_mutation=True,pyspark=False):
		self.adaptive_mutation = adaptive_mutation
		self.pyspark = pyspark

	def __evolve_normal(self,ga):

		"""
		Private method which performs an iteration

		Outline of Algorithm :
		---------------------
		Selection : fittest members of population are selected by invoking 
					selection handler in Utils.py module
		Crossover : A probability score is generated from fitness value of each chromosome
					Chromosomes for crossover are selected based on this probablity score 
					of each chromosome
					Crossover is performed by invoking a crossover handler from Utils.py
		Mutation : If adaptive mutation is set then average square deviation of fitness values
					is used for determining (the indexes of chromosome)/genes to be mutated 
					If false then genes to be mutated are chosen randomly
					Once indexes of Chromomsome / genes to be mutated are determined, a mutation
					handler from Utils.py module is invoked 

		Each iteration consists of repeating the above operations until an optimal solution 
		determined by fitness threshold is reached  or number of iterations specified are complete

		"""

		# get (1-r) * cross_prob new members
		ga.population.new_members = ga.handle_selection()
		print("*** Members left after selection = ",len(ga.population.members))
		print("Best member = ",ga.best_fitness[0])
		print("Best fitness = ",ga.best_fitness[1])
		if ga.fitness_type[0] == 'equal':
			if ga.best_fitness[1] == ga.fitness_type[1]:
				return 1

		fitnesses = []
		total = 0 #This is not being used
		for chromosome in ga.fitness_dict:
			fitness = chromosome[1]
			if fitness == 0:
				fitness = random.uniform(0.01, 0.02)
			total += fitness
			fitnesses.append(fitness)

		p = [ elem/total for elem in fitnesses]
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
			child1, child2 = ga.doCrossover(crossoverHandler,father,mother)
			print('here')
			print(child1)
			print(child2)
			ga.population.new_members.extend([child1,child2])
		print("adaptive_mutation value passed = ",self.adaptive_mutation)

		if self.adaptive_mutation == True and ga.dynamic_mutation:
			mutation_indexes = np.random.choice(len(ga.population.new_members),int(ga.dynamic_mutation*len(p)), replace=False)
		else:
			mutation_indexes = np.random.choice(len(ga.population.new_members),int(ga.mut_prob*len(p)), replace=False)
		for index in mutation_indexes:
			mutationHandler = ga.chooseMutationHandler()
			ga.population.new_members[index] = ga.doMutation(mutationHandler,ga.population.new_members[index])
		ga.population.members = ga.population.new_members
		print("New members = ",ga.population.members)
		print(len(ga.population.members))
		ga.population.new_members = []
		return 0

	def __evolve_pyspark(self,ga):
		from pyspark import SparkContext
		sc = SparkContext.getOrCreate()
		#print(ga.population.members)
		chromosomes_rdd = sc.parallelize(ga.population.members)
		# Fitness Value Mapping and making selection
		mapped_chromosomes_rdd = chromosomes_rdd.map(lambda x: (x,ga.calculateFitness(x)))
		#print(mapped_chromosomes_rdd.collect())
		if ga.selection_handler == Utils.SelectionHandlers.best:
			if type(ga.fitness_type) == str:
				if ga.fitness_type == 'max':
					selected_chromosomes = mapped_chromosomes_rdd.top(len(ga.population.members)-math.ceil(ga.cross_prob * len(ga.population.members)),key=lambda x: x[1])
				elif ga.fitness_type == 'min':
					selected_chromosomes = mapped_chromosomes_rdd.takeOrdered(len(ga.population.members)-math.ceil(ga.cross_prob * len(ga.population.members)),key=lambda x: x[1])
			elif type(ga.fitness_type) == tuple or type(ga.fitness_type) == list:
				if ga.fitness_type[0] == 'equal':
					selected_chromosomes = mapped_chromosomes_rdd.takeOrdered(len(ga.population.members)-math.ceil(ga.cross_prob * len(ga.population.members)),key=lambda x: abs(x[1]-ga.fitness_type[1]))
		else:
			print('HERE MATE')
			selected_chromosomes = ga.handle_selection()
		#selected_chromosomes = mapped_chromosomes_rdd.top(len(ga.population.members)-math.ceil(ga.cross_prob * len(ga.population.members)),key=lambda x: x[1])
		print('SELECTED CHROMOSOMES')
		print(selected_chromosomes)
		ga.best_fitness = selected_chromosomes[0]
		print('BEST', ga.best_fitness[1])
		ga.population.new_members = selected_chromosomes

		#print(ga.population.new_members)
		#exit()
		n = math.ceil(ga.cross_prob * len(ga.population.members))
		if n %2 == 1:
			n -= 1
			ga.population.members.append(ga.population.members[0])

		total_fitness = mapped_chromosomes_rdd.map(lambda x: (x[0],x[1]) if x[1] > 0 else (x[0],random.uniform(0.01, 0.02))).values().sum()
		print(total_fitness)

		#print(type(total_fitness))
		p = mapped_chromosomes_rdd.map(lambda x: (x[0],x[1]/total_fitness)).values().collect()
		#p = [random.uniform(0.01, 0.02) if prob<=0 else prob for prob in p]
		#p = [  prob/sum(p)   for prob in p] 
		print(sum(p))
		p[random.randint(0,len(p)-1)] += (1-sum(p))
		print(p)
		print(sum(p))
		#print(type(p))
		#print(sum(p))

		# Crossover Mapping
		crossover_indexes = np.random.choice(len(ga.population.members),n,p=p, replace=False)
		#print("crossover_indices = ",crossover_indexes)
		crossover_chromosomes = [ ga.population.members[index] for index in crossover_indexes]

		crossover_pair_indexes = [(crossover_indexes[i],crossover_indexes[i+1]) for i in range(0,len(crossover_indexes),2)]
		#print(crossover_indexes)
		#print(crossover_pair_indexes)
		
		crossover_pair_indexes_rdd = sc.parallelize(crossover_pair_indexes)
		crossover_before = crossover_pair_indexes_rdd.map(lambda x: (ga.population.members[0],ga.population.members[1]))
		#print(crossover_before.collect())
		crossover_results = crossover_before.map(lambda x:(x,ga.chooseCrossoverHandler()(x[0],x[1])))#.flatmap
		#print(crossover_results.collect())
		result_test = crossover_results.flatMap(lambda x:x[1]).collect()
		print('population after crossover',result_test)
		#print(type(result_test))

		ga.population.new_members.extend(result_test)

		#print(len(ga.population.members))
		#print(len(ga.population.new_members))
		print('now',ga.population.new_members)

		# Mutation Handling
		mutation_indexes = np.random.choice(len(ga.population.new_members),int(ga.mut_prob*len(p)), replace=False)
		print(mutation_indexes)
		mutation_indexes_rdd = sc.parallelize(mutation_indexes)
		print(ga.population.new_members)
		mutation_results = mutation_indexes_rdd.map(lambda x:(x,ga.population.new_members[x]))
		print(mutation_results.collect())
		mutation_results = mutation_results.map(lambda x:(x[0],x[1],ga.chooseMutationHandler()(list(x[1])))).collect()
		#print(mutation_results)
		#print('BEFORE')
		#print(ga.population.new_members)
		for entry in mutation_results:
			ga.population.new_members[entry[0]] = entry[2]

		#print('AFTER')
		#print(ga.population.new_members)
		ga.population.members = ga.population.new_members 
		ga.population.new_members = []
		ga.generateFitnessDict()

	def evolve(self,ga):
		"""
		Invokes the private method __evolve_normal to perform an iteration Genetic Algorithm

		Returns : 1 if optimal solution was found

		"""
		#print(self.max_iterations)
		if self.pyspark == False:
			return self.__evolve_normal(ga)
		else:
			if self.__evolve_pyspark(ga):
				return 1
