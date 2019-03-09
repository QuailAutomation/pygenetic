import Population
import ChromosomeFactory
import random
import numpy as np
import collections
import Utils
import Evolution
import Statistics
import bisect

class GAEngine:
	"""This Class is the main driver program which contains and calls the operators used in Genetic algorithm

	GAEngine keeps track of specific type of operators the user has specified for running the algorithm

	Methods
	---------
	addCrossoverHandler(crossover_handler, weight)
		Sets the function to be used for crossover operation

	addMutationHandler(mutation_handler, weight)
		Sets the function to be used for mutation operation

	setCrossoverProbability(cross_prob)
		Sets value for cross_prob instance variable for crossover operation

	setMutationProbability(mut_prob)
		Sets value for mut_prob instance variable

	setSelectionHandler(selection_handler)
		Sets the function to be used for selection operation

	calculateFitness(chromosome)
		Calls fitness function (fitness_func) to compute the fitness score of a chromosome

	generateFitnessDict()
		Generates a  dictionary of (individual, fitness_score) and also stores the dictionary 
		containing fittest chromosome depending on fitness_type(max/min/equal)

	handle_selection()
		Calls generateFitnessDict() and  selection_handler specified 
		SET TO NONE CURRENTLY

	normalizeWeights()
		Normalizes crossover and mutation handler weights, result is a CDF

	chooseCrossoverHandler()
		TO BE DESCRIBED

	chooseMutationHandler()
		TO BE DESCRIBED
		
	evolve()
		Calls evolve method in Evolution module  which Executes the operations of Genetic algorithm till
		a fitness score reaches a threshold or the number of iterations reach max iterations specified by user
	

  	"""

	def __init__(self,fitness_func,fitness_threshold,factory,population_size=100,cross_prob=0.8,mut_prob=0.1,fitness_type='max',adaptive_mutation=True,smart_fitness=False):
		"""
		Parameters
		-----------
		fitness_func : A function argument
					The fitness function to be used, passed as a function argument
		fitness_threshold : int
					Threshold at which a candidate solution is considered optimal solution to the problem
		factory : Instance of any subclass of ChromosomeFactory class 
					Generates and returns the initial population of candidate solutions
		population_size : int
					The number of candidate solutions that can exist after every iteration
		cross_prob : float
					The Crossover probability of crossover operation which determines the extent to which crossover between parents
		mutation_prob : float
					The mutation probability of mutation operation which determines extent to which candidates should be mutated
		fitness_type : string
					Indicates the nature of fitness value (higher/lower/equal) to be considered during selection of candidates
					(default is max)
		adaptive_mutation : boolean
					If set rate of mutation of candidates dynamically changes during execution depending on diversity in population
					(default is true)
		smart_fitness : boolean
					TO BE DESCRIBED  
		"""

		self.fitness_func = fitness_func
		self.fitness_threshold = fitness_threshold
		self.factory = factory
		self.population = Population.Population(factory,population_size)
		self.population_size = population_size
		self.cross_prob = cross_prob
		self.mut_prob = mut_prob
		#self.adaptive_mutation = adaptive_mutation
		self.smart_fitness = smart_fitness
		self.crossover_handlers = []
		self.crossover_handlers_weights = []
		self.mutation_handlers = []
		self.mutation_handlers_weights = []
		self.selection_handler = None
		self.fitness_type = fitness_type
		if self.fitness_type == 'max':
			self.best_fitness = None, float("-inf")
		elif self.fitness_type == 'min':
			self.best_fitness = None, float("inf")
		elif self.fitness_type == 'equal':	# Fitness must be absolute difference between member score and fitness_threshold
			self.best_fitness = None, float("inf")
		if adaptive_mutation == True:
			self.dynamic_mutation = None
		#elif self.fitness_type ==
		self.statistics = Statistics.Statistics()
		self.evolution = Evolution.StandardEvolution(100,adaptive_mutation=adaptive_mutation)

	def addCrossoverHandler(self,crossover_handler, weight = 1):
		"""
		Sets the function to be used for crossover operation



		"""
		self.crossover_handlers.append(crossover_handler)
		self.crossover_handlers_weights.append(weight)

	def addMutationHandler(self,mutation_handler, weight = 1):
		self.mutation_handlers.append(mutation_handler)
		self.mutation_handlers_weights.append(weight)

	def setCrossoverProbability(self,cross_prob):
		self.cross_prob = cross_prob

	def setMutationProbability(self,mut_prob):
		"""
		Sets mutation probability instance variable

		Parameters:
		----------
		Mutation probability

		"""
		self.mut_prob = mut_prob

	def setSelectionHandler(self,selection_handler):
		"""
		Sets function to be used for selection_handler

		Parameters:
		----------
		Function to be used for selection_handler

		"""
		self.selection_handler = selection_handler

	def calculateFitness(self,chromosome):
		"""
		Calls fitness function (fitness_func) to compute the fitness score of a chromosome

		Parameters:
		----------
		chromosome for which fitness is to be calculated

		Returns:
		--------
		Fitness value of chromosome	

		"""
		return self.fitness_func(chromosome)

	def generateFitnessDict(self):
		self.fitness_dict = []
		for member in self.population.members:
			self.fitness_dict.append((member,self.fitness_func(member)))
			if self.fitness_type == 'max' and self.fitness_func(member) > self.best_fitness[1]:
				self.best_fitness = (member,self.fitness_func(member))
			elif self.fitness_type == 'min' and self.fitness_func(member) < self.best_fitness[1]:
				self.best_fitness = (member, self.fitness_func(member))
			elif self.fitness_type == 'equal' and abs(self.fitness_func(member)-self.fitness_threshold) < abs(self.best_fitness[1]-self.fitness_threshold):
				self.best_fitness = (member, self.fitness_func(member))

	def handle_selection(self):
		self.generateFitnessDict()
		return self.selection_handler(self.population.members,self.fitness_dict,self)

	def normalizeWeights(self):
		# Normalizing crossover and mutation handler weights, result is a CDF
		total = sum(self.mutation_handlers_weights)
		cumsum = 0
		for i in range(len(self.mutation_handlers_weights)):
			cumsum += self.mutation_handlers_weights[i]
			self.mutation_handlers_weights[i] = cumsum/total
		print("mutation_handlers_weights = ",self.mutation_handlers_weights)
		total = sum(self.crossover_handlers_weights)
		cumsum = 0
		for i in range(len(self.crossover_handlers_weights)):
			cumsum += self.crossover_handlers_weights[i]
			self.crossover_handlers_weights[i] = cumsum/total
		print("crossover_handlers_weights = ",self.crossover_handlers_weights)

	def chooseCrossoverHandler(self):
		x = random.random()
		idx = bisect.bisect(self.crossover_handlers_weights, x)
		return self.crossover_handlers[idx]

	def chooseMutationHandler(self):
		x = random.random()
		idx = bisect.bisect(self.mutation_handlers_weights, x)
		return self.mutation_handlers[idx]

	def evolve(self,noOfIterations=50):
		self.normalizeWeights()
		for i in range(noOfIterations):
			result = self.evolution.evolve(self)
			self.statistics.compute(ga.best_fitness[1])
			if result:
				print('SOLVED')
				self.statistics.plot()
				break


if __name__ == '__main__':
	#factory = ChromosomeFactory.ChromosomeRegexFactory(int,noOfGenes=4,pattern='0|1')
	#ga = GAEngine(lambda x:sum(x),'MAX',factory,20)
	#print(ga.fitness_func)
	#print(ga.fitness_type)
	#ga.calculateAllFitness()
	import copy
	factory = ChromosomeFactory.ChromosomeRangeFactory(int,8,1,9)
	def fitness(board):
		fitness = 0
		for i in range(len(board)):
			isSafe = True
			for j in range(len(board)):
				if i!=j:
					if (board[i] == board[j]) or (abs(board[i] - board[j]) == abs(i-j)):
						isSafe = False
						break
			if(isSafe==True):
				fitness += 1
		return fitness

	ga = GAEngine(fitness,8,factory,100,fitness_type='equal')
	ga.addCrossoverHandler(Utils.CrossoverHandlers.distinct, 9)
	ga.addCrossoverHandler(Utils.CrossoverHandlers.distinct, 4)
	ga.addCrossoverHandler(Utils.CrossoverHandlers.distinct, 3)
	ga.addMutationHandler(Utils.MutationHandlers.swap)
	ga.setSelectionHandler(Utils.SelectionHandlers.basic)
	ga.evolve(100)
