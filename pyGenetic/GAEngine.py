import Population
import ChromosomeFactory
import random
import numpy as np
import collections

class GAEngine:

	def __init__(self,fitness_func,fitness_threshold,factory,population_size=100,cross_prob=0.8,mut_prob=0.4,adaptive_mutation=False,smart_fitness=False):
		self.fitness_func = fitness_func
		self.fitness_threshold = fitness_threshold
		self.factory = factory
		self.population = Population.Population(factory,population_size)
		self.population_size = population_size
		self.cross_prob = cross_prob
		self.mut_prob = mut_prob
		self.adaptive_mutation = adaptive_mutation
		self.smart_fitness = smart_fitness
		self.crossover_handlers = []
		self.mutation_handlers = []
		self.selection_handler = None
		self.highest_fitness = None, float("-inf")

	def addCrossoverHandler(self,crossover_handler):
		self.crossover_handlers.append(crossover_handler)

	def addMutationHandler(self,mutation_handler):
		self.mutation_handlers.append(mutation_handler)

	def setCrossoverProbability(self,cross_prob):
		self.cross_prob = cross_prob

	def setMutationProbability(self,mut_prob):
		self.mut_prob = mut_prob

	def setSelectionHandler(self,selection_handler):
		self.selection_handler = selection_handler

	def calculateAllFitness(self):
		self.population.fitnessSort(self.fitness_func)

	def calculateFitness(self,chromosome):
		return self.fitness_func(chromosome)

	def generateFitnessDict(self):
		self.fitness_dict = []
		for member in self.population.members:
			self.fitness_dict.append((member,self.fitness_func(member)))
			if self.fitness_func(member) > self.highest_fitness[1]:
				self.highest_fitness = (member,self.fitness_func(member))

	def handle_selection(self):
		self.generateFitnessDict()
		return self.selection_handler(self.population.members,self.fitness_dict)

	def evolve(self,noOfIterations=20):
		print(noOfIterations)
		for i in range(noOfIterations):
			self.population.new_members = self.handle_selection()
			print(self.highest_fitness[1])
			if self.highest_fitness[1] == self.fitness_threshold:
				print('SOLVED')
				break
			iteration_size = len(self.population.new_members)
			if iteration_size%2==1:
				iteration_size -= 1
			for i in range(0,iteration_size,2):
				father, mother = self.population.new_members[i], self.population.new_members[i+1]
				if random.random() <= self.cross_prob:
					child1, child2 = self.crossover_handlers[0](father,mother)
					self.population.new_members.append(child1)
					self.population.new_members.append(child2)
				if random.random() <= self.mut_prob:
					child = self.mutation_handlers[0](father)
					self.population.new_members.append(child)
				if random.random() <= self.mut_prob:
					child = self.mutation_handlers[0](mother)
					self.population.new_members.append(child)

	def execute_selection(self):
		self.calculateAllFitness()
		self.population.new_members = self.population.getPercentOfPopulation(self.cross_prob,self.fitness_func)
		self.max_fitness = self.population.getMaxFitness(fitness_func)
		self.calculateAllFitness()
		print(self.population.new_members)
		print(len(self.population.new_members))


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

	ga = GAEngine(fitness,8,factory,100)
	#print(ga.fitness_func)
	#print(ga.fitness_type)
	#ga.calculateAllFitness()
	def mut(chrom):
		index = random.randint(0,6)
		newchrom = copy.copy(chrom)
		t = newchrom[index]
		newchrom[index] = newchrom[index+1]
		newchrom[index+1] = t
		return newchrom

	def cross(chrom1,chrom2):
		r = random.randint(1,6)
		new_chromosome1 = chrom1[:r]
		for i in chrom2:
			if i not in new_chromosome1:
				new_chromosome1.append(i)
		new_chromosome2 = chrom2[:r]
		for i in chrom1:
			if i not in new_chromosome2:
				new_chromosome2.append(i)
		return new_chromosome1,new_chromosome2

	def selection(pop,fitness_dict):
		pop = sorted(pop,key=lambda x:fitness_dict[1])
		return pop[:20]

	ga.addCrossoverHandler(cross)
	ga.addMutationHandler(mut)
	ga.setSelectionHandler(selection)
	ga.evolve()
