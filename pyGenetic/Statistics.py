import matplotlib.pyplot as plt

class Statistics:
	"""
	Class to generate Statistics on operation of Genetic Algorithm 
	
	Instance Members:
	-----------------
	max_fitnesses : List containing the maximum fitness scores discovered in each iteration
	iterations : List containing count of each iteration

	"""


	def __init__(self):
		self.max_fitnesses = []
		self.iterations = []
		self.iterationNumber = 1
		self.statistic_dict = {'max':[],'min':[],'avg':[],'diversity':[],'mutation_rate':[]}

	def add_statistic(self,statistic,value):
		"""
		Keeps track of max fitness scores of each iteration and iteration number 

		Parameters :
		------------
		max_fitness : float , fitness score after an iteration

		"""
		if statistic in self.statistic_dict:
			self.statistic_dict[statistic].append(value)
		else:
			raise Exception('Invalid Statistic')

		#self.max_fitnesses.append(max_fitness)
		#print("max fitnesses list = ",self.max_fitnesses)
		#print("iteration number   = ",self.iterations)

	def plot(self):
		"""
		Generates a line graph to display change in fitness values over iterations 

		"""
		for statistic in self.statistic_dict:
			#print(statistic,self.statistic_dict[statistic])
			plt.plot(range(len(self.statistic_dict[statistic])),self.statistic_dict[statistic],label=statistic)
		plt.legend(loc='upper left')
		plt.show()

	def plot_statistics(self,statistics):
		for statistic in statistics:
			#print(statistic,self.statistic_dict[statistic])
			plt.plot(range(len(self.statistic_dict[statistic])),self.statistic_dict[statistic],label=statistic)
		plt.legend(loc='upper left')
		plt.show()

	def plot_statistic(self,statistic):
		plt.plot(range(len(self.statistic_dict[statistic])),self.statistic_dict[statistic],label=statistic)
		plt.legend(loc='upper left')
		plt.show()
