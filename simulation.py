import networkx as nx
import matplotlib.pylab as plt
from random import *
import numpy as np
import copy
import gc
import graph_utils
from company import *
from truck import *
from client import *

class Simulation(object):
				
	def __init__(self, 
		n_nodes=15, graph_type="random", graph_param=0.2, graph_min_weight=1, graph_max_weight=10,
		n_companies=5, n_trucks=7, 
		truck_threshold=100, company_init_money=2500, uni_cost=1, profit_margin=1.5, tax=0.05,
		risk=(randint(1,99)/100), min_offer_val=25, max_offer_val=80,
		existence_tax=0.05, p_edge_explosion=0.0, p_truck_explosion=0.0):

		# network params
		self.n_nodes = n_nodes
		self.graph_type = graph_type
		self.graph_param = graph_param
		self.graph_min_weight = graph_min_weight
		self.graph_max_weight = graph_max_weight
		
		# agents params
		self.n_companies = n_companies
		self.n_trucks = n_trucks

		# company params
		self.truck_threshold = truck_threshold
		self.company_init_money = company_init_money
		self.uni_cost = uni_cost
		self.profit_margin = profit_margin
		self.tax = tax

		# client params
		self.risk = risk
		# self.utilities = utilities
		self.min_offer_val = min_offer_val
		self.max_offer_val = max_offer_val

		# events params
		self.existence_tax = existence_tax
		self.p_edge_explosion = p_edge_explosion
		self.p_truck_explosion = p_truck_explosion		

		self.completedOffers = 0

	def build_graph(self):
		if self.graph_type == "random":
			return graph_utils.generate_weighted_random_graph(
				n=self.n_nodes, 
				p=self.graph_param,
				min_weight=self.graph_min_weight, 
				max_weight=self.graph_max_weight)
		elif self.graph_type == "scale-free":
			return graph_utils.generate_weighted_barabasi_graph(
				n=self.n_nodes, 
				m=self.graph_param,
				min_weight=self.graph_min_weight, 
				max_weight=self.graph_max_weight)

	def generate_companies(self, graph, numCompanies=False):
		company_names = ["A", "B", "C", "D","E","F","G","H","I","J","K"]
		companies = sample(list(graph.nodes()), k=self.n_companies)
		companies = [(x, Company(x, self.company_init_money, 
						company_names[i], graph,
						uni_cost=self.uni_cost,
						truck_threshold=self.truck_threshold,
						profit_margin=self.profit_margin,
						tax=self.tax)) for i,x in enumerate(companies)]
		if numCompanies:
			graph_utils.set_ncompany_nodes(graph, companies)
		else:
			graph_utils.set_company_nodes(graph, companies)
		return companies

	def generate_trucks(self, graph, companies):
		for c in companies:
			c[1].setTrucks([Truck(i, c[1], graph) for i in range(self.n_trucks)])

	def calculateUtilities(self):
		pref = np.array([(randint(1,99)/100) for _ in range(self.n_companies)])
		return list(pref/sum(pref))

	def generate_clients(self, graph, companies):
		return [Client(n, 
					[c[1] for c in companies],
					risk=self.risk,
					utilities=self.calculateUtilities(),
					min_offer_val=self.min_offer_val, 
					max_offer_val=self.max_offer_val) for n in graph.nodes if "company" not in graph.node[n]]

	def do_edge_explosion(self, t, graph):
		try:
			e = choice(list(graph.edges()))
			graph.remove_edge(e[0],e[1])
		except Exception as e:
			if verbosity_events:
				print(f"\tall edges removed t= {t}\t")
			return
		if verbosity_events:	
			print(f"\tedge removed:\t {e[0]} -- {e[1]} (t={t})")

	def do_truck_explosion(self, t, graph, companies):
		try:
			c = choice(companies)
			c[1].truckExplosion()
		except Exception as e:
			if verbosity_events:
				print(f"\tNo more trucks t= {t}\t")
			return
		if verbosity_events:	
			print(f"\tTruck from \t {c[1].pos} exploded (t={t})")

	def do_game_over(self, companies, company, graph,t):
		if verbosity_companies:
			print(f"GAME OVER FOR {company[1]} at t={t} -- offers={company[1].completedOffers}")
		companies.remove(company)
		# del graph.node[company[0]]['company']
		# graph_utils.colormap[company[0]]= "#%06x" % 0xDDDDDD
		return company[1]

	def generateMoneyPerCompany(self):
		# generates a list of lists (a list per company) to keep track of all companies' money
		money_per_company = []
		for _ in range(self.n_companies):
			money_per_company.append([])
			
		for _ in range(iterations):
			for m in money_per_company:
				m.append(0)
		return money_per_company

	def drawPlot(self, y_data, x_data, title, xlabel, ylabel, legend, per=0.2, color="red"):
		# Draws the basic plot
		plt.figure()
		plt.title(title)
		plt.xlabel(xlabel)
		plt.ylabel(ylabel)
		error = per * np.array(x_data)
		plt.errorbar(x=y_data, y=x_data, yerr=error, color=color)
		plt.legend(legend[0])
		plt.show()

	def testCicle(self, g, money_per_company, companies, cpy_companies, clients, truckExp=False):
		# cicle for "tests" times, and does the mean for all the values
		for cli in clients:
				cli.setCompanies([c[1] for c in cpy_companies])
		for i in range(tests):
			if verbosity:
				print(f"\n\n\nITERATION {i}\n\n\n")
			mc = self.run(g.copy(), list(cpy_companies), list(clients), iterations)
			for i in range(len(mc)):
				money_per_company[i] = list(np.array(money_per_company[i]) + np.array(mc[i]))
			if truckExp:
				self.generate_trucks(g, companies)
			cpy_companies = [(c[0], copy.deepcopy(c[1])) for c in companies]
			for cli in clients:
				cli.setCompanies([c[1] for c in cpy_companies])
		for mc in money_per_company:
			mc = np.array(mc)/tests
		return money_per_company

	def run(self, g, companies, clients, iterations):
		money_per_company = []
		self.completedOffers = 0
		dict_companies = dict([])
		for i in range(len(companies)):
			money_per_company.append([])
			dict_companies[companies[i][1]] = i

		for _ in range(iterations):
			for m in money_per_company:
				m.append(0)

		for i in range(iterations):
			if len(companies) == 0:
				return money_per_company

			if (randint(1,99)/100) < self.p_edge_explosion:
				self.do_edge_explosion(i, g)
			
			if (randint(1,99)/100) < self.p_truck_explosion:
				self.do_truck_explosion(i, g, companies)

			for cli in clients:
				cli.go(i)

			for c in companies:
				if c[1].money <= 0:
					self.completedOffers += c[1].getCompletedOffers()
					company_gameover = self.do_game_over(companies, c, g, i)
					for cli in clients:
						cli.removeCompany(company_gameover)
					continue

				c[1].money -= self.company_init_money*self.existence_tax # impostos por existencia
				c[1].go(g, i)
				money_per_company[dict_companies[c[1]]][i] = c[1].money

		for c in companies:
			if verbosity_companies:
				print(f"SURVIVOR: {c} -- t={i} -- offers={c[1].completedOffers}")
			self.completedOffers += c[1].getCompletedOffers()

		if verbosity_companies:
			print(f"OFFERS COMPLETED: {self.completedOffers}")
		return money_per_company

class SimulationObject(object):
	def __init__(self, type):
		self.type = type
		self.graph_param = 0.2 if self.type=="random" else 2
		
class MoneyTime(SimulationObject):
	def drawPlot(self, x_data, title, xlabel, ylabel, legend):
		plt.figure()
		plt.title(title)
		plt.xlabel(xlabel)
		plt.ylabel(ylabel)
		for i in range(len(x_data)):
			error = 0.05 * np.array(x_data[i])
			plt.errorbar(list(range(len(x_data[i]))), x_data[i], yerr=error, label="Company "+legend[i][1]+" pos:"+str(legend[i][2]), color=legend[i][0])
		plt.legend()
		plt.show()

	def run(self):
		s = Simulation(graph_type=self.type, graph_param=self.graph_param)	
		g = s.build_graph()
		companies = s.generate_companies(g)
		s.generate_trucks(g, companies)
		graph_utils.draw_graph(g)
		#graph_utils.show_graphs()
		cpy_companies = [(c[0], copy.deepcopy(c[1])) for c in companies]
		clients = s.generate_clients(g, cpy_companies)
		money_per_company = s.testCicle(g, s.generateMoneyPerCompany(), companies, cpy_companies, clients)
		gc.collect()
		legend = [(graph_utils.colormap[c[0]], c[1].name, c[1].pos) for c in companies]
		self.drawPlot(money_per_company, "Money vs Time", "Time", "Money", legend)

class GraphTypes(SimulationObject):
	def drawPlot(self, y_data, random_type, scale_free_type, title, xlabel, ylabel, legend):
		plt.title(title)
		plt.xlabel(xlabel)
		plt.ylabel(ylabel)
		error_random = 0.05 * np.array(random_type)
		error_scale_free = 0.05 * np.array(scale_free_type)
		plt.errorbar(y_data, random_type, yerr=error_random, label=legend[0], color="red")
		plt.errorbar(y_data, scale_free_type, yerr=error_scale_free, label=legend[1], color="blue")
		plt.legend()
		plt.show()

	def run(self):
		s = Simulation(graph_type=self.type, graph_param=self.graph_param)
		all_costs = []
		for tipo in range(2):
			if tipo==1:
				s.graph_type = "scale-free"
				s.graph_param = 2
			g = s.build_graph()
			companies = s.generate_companies(g)
			s.generate_trucks(g, companies)
			cpy_companies = [(c[0], copy.deepcopy(c[1])) for c in companies]
			clients = s.generate_clients(g, cpy_companies)
			money_per_company = s.testCicle(g, s.generateMoneyPerCompany(), companies, cpy_companies, clients)
			maximum = [i[-1] for i in money_per_company]
			all_costs.append(money_per_company[maximum.index(max(maximum))])
			gc.collect()
		legend = ["Random Network", "Scale-Free Network"]
		self.drawPlot(list(range(iterations)), all_costs[0], all_costs[1], "Graph Types", "Time", "Money", legend)

class NumCompanies(SimulationObject):
	def run(self):
		s = Simulation(n_nodes=30, graph_type=self.type, graph_param=self.graph_param)
		g = s.build_graph()
		values_ncomps = []
		list_len_companies = list(range(1,11))
		for n_companies in list_len_companies:
			s.n_companies = n_companies
			companies = s.generate_companies(g, True)
			s.generate_trucks(g, companies)
			cpy_companies = [(c[0], copy.deepcopy(c[1])) for c in companies]
			clients = s.generate_clients(g, cpy_companies)
			money_per_company = s.testCicle(g, s.generateMoneyPerCompany(), companies, cpy_companies, clients)
			for c in companies:
				del g.node[c[0]]['company']
			maximum = [i[-1] for i in money_per_company]
			values_ncomps.append(max(maximum))
			gc.collect()

		legend = [["Company w/ most profit"]]
		s.drawPlot(list_len_companies, values_ncomps, "Number of Companies", "Number of Companies", "Money", legend, per=0.05)

class NumNodes(SimulationObject):
	def drawPlot(self, y_data, trucks8, trucks16, title, xlabel, ylabel, legend):
		plt.title(title)
		plt.xlabel(xlabel)
		plt.ylabel(ylabel)
		error_truck8 = 0.05 * np.array(trucks8)
		error_truck16 = 0.05 * np.array(trucks16)
		plt.errorbar(y_data, trucks8, yerr=error_truck8, label=legend[0], color="red")
		plt.errorbar(y_data, trucks16, yerr=error_truck16, label=legend[1], color="blue")
		plt.legend()
		plt.show()

	def run(self):
		s = Simulation(graph_type=self.type, graph_param=self.graph_param)
		list_nodes = list(range(10,205,5))
		for trucks in range(8,17,8):
			s.n_trucks = trucks
			all_costs = []
			for nodes in list_nodes:
				s.n_nodes = nodes
				g = s.build_graph()
				companies = s.generate_companies(g, True)
				s.generate_trucks(g, companies)
				cpy_companies = [(c[0], copy.deepcopy(c[1])) for c in companies]
				clients = s.generate_clients(g, cpy_companies)
				money_per_company = s.testCicle(g, s.generateMoneyPerCompany(), companies, cpy_companies, clients)
				maximum = [i[-1] for i in money_per_company]
				all_costs.append(max(maximum))
				gc.collect()
			if trucks==8:
				trucks8 = all_costs
			else:
				trucks16 = all_costs
		legend = ["Number of Trucks: 8", "Number of Trucks: 16"]
		self.drawPlot(list_nodes, trucks8, trucks16, "Number of Nodes/Number of trucks", "Number of Nodes", "Money", legend)

class Threshold(SimulationObject):
	def run(self):
		s = Simulation(graph_type=self.type, graph_param=self.graph_param)
		g = s.build_graph()
		companies = s.generate_companies(g)
		s.generate_trucks(g, companies)
		cpy_companies = [(c[0], copy.deepcopy(c[1])) for c in companies]
		clients = s.generate_clients(g, cpy_companies)
		values_per_threshold = []	
		limits = list(range(0,325,25))		
		for threshold in limits:
			s.truck_threshold = threshold
			graph_utils.colormap = []
			for c in companies:
				c[1].setTruckThreshold(threshold)
			money_per_company = s.testCicle(g, s.generateMoneyPerCompany(), companies, cpy_companies, clients)
			maximum = [i[-1] for i in money_per_company]
			values_per_threshold.append(money_per_company[maximum.index(max(maximum))][-1])
			gc.collect()
		legend = [["Company w/ most profit"]]
		s.drawPlot(limits, values_per_threshold, "Threshold", "Threshold", "Money", legend, per=0.05)

class Explosion(SimulationObject):
	def __init__(self,  type, edge=False):
		self.edge = edge
		super().__init__(graphType)

	def run(self):
		s = Simulation(graph_type=self.type, graph_param=self.graph_param)
		g = s.build_graph()
		companies = s.generate_companies(g)
		s.generate_trucks(g, companies)
		cpy_companies = [(c[0], copy.deepcopy(c[1])) for c in companies]
		clients = s.generate_clients(g, cpy_companies)
		values_per_exp = []
		range_per_edge_exp = list(np.array(list(range(0,500,10)))/1000)
		for per_exp in range_per_edge_exp:	
			if self.edge:
				s.p_edge_explosion = per_exp
			else:
				s.p_truck_explosion = per_exp	
			if self.edge:
				money_per_company = s.testCicle(g, s.generateMoneyPerCompany(), companies, cpy_companies, clients)
			else:
				money_per_company = s.testCicle(g, s.generateMoneyPerCompany(), companies, cpy_companies, clients, truckExp=True)
			maximum = [i[-1] for i in money_per_company]
			values_per_exp.append(money_per_company[maximum.index(max(maximum))][-1])
			gc.collect()
		legend = [["Company w/ most profit"]]
		if self.edge:
			s.drawPlot(range_per_edge_exp, values_per_exp, "Edge Explosion", "% Edge Explosion", "Money", legend, per=0.05)
		else:
			s.drawPlot(range_per_edge_exp, values_per_exp, "Truck Explosion", "% Truck Explosion", "Money", legend, per=0.05)

class TruckExplosion(Explosion):
	def __init__(self, graphType):
		super().__init__(graphType)

class EdgeExplosion(Explosion):
	def __init__(self, graphType):
		super().__init__(graphType, edge=True)

class ProfitMargin(SimulationObject):
	def run(self):
		s = Simulation(graph_type=self.type, graph_param=self.graph_param)
		g = s.build_graph()
		companies = s.generate_companies(g)
		graph_utils.draw_graph(g)
		s.generate_trucks(g, companies)
		cpy_companies = [(c[0], copy.deepcopy(c[1])) for c in companies]
		clients = s.generate_clients(g, cpy_companies)
		money_per_company = s.testCicle(g, s.generateMoneyPerCompany(), companies, cpy_companies, clients)
		minimum = [m[-1] for m in money_per_company]
		index_company = minimum.index(min(minimum))
		# values for index_company for different values of profit margin
		values_pm_company = []
		profitMaring_values = list(np.array(list(range(10,50,1)))/10)		
		for pm in profitMaring_values:
			companies[index_company][1].setProfitMargin(pm)
			money_per_company = s.testCicle(g, s.generateMoneyPerCompany(), companies, cpy_companies, clients)
			values_pm_company.append(money_per_company[index_company][-1])
			gc.collect()
		legend = [["Company w/ worst profit: "+str(companies[index_company][1].pos)]]
		s.drawPlot(profitMaring_values, values_pm_company, "Profit Margin", "Profit Margin", "Money", legend, per=0.05, color=graph_utils.colormap[companies[index_company][0]])

class Preferences(SimulationObject):
	def __init__(self, graphType, legend, last=False):
		super().__init__(graphType)
		self.last = last
		self.legend = legend

	def drawPlot(self, pref_values, second_company, best_company, title, xlabel, ylabel, legend, color):
		plt.figure()
		plt.title(title)
		plt.xlabel(xlabel)
		plt.ylabel(ylabel)
		sec_error = 0.05 * np.array(second_company)
		best_error = 0.05 * np.array(best_company)
		plt.errorbar(pref_values, second_company, yerr=sec_error, label=legend[0], color=color[0])
		plt.errorbar(pref_values, best_company, yerr=best_error, label=legend[1], color=color[1])
		plt.legend()
		plt.show()

	def run(self):
		s = Simulation(graph_type=self.type, graph_param=self.graph_param)
		g = s.build_graph()
		while not nx.is_connected(g):
			g = s.build_graph()
		companies = s.generate_companies(g)
		s.generate_trucks(g, companies)
		graph_utils.draw_graph(g)
		cpy_companies = [(c[0], copy.deepcopy(c[1])) for c in companies]
		clients = s.generate_clients(g, cpy_companies)
		basic_preferences = [1/s.n_companies for _ in range(s.n_companies)]
		for cli in clients:
			cli.setUtilities(basic_preferences)
			cli.risk=1
		money_per_company = s.testCicle(g, s.generateMoneyPerCompany(), companies, cpy_companies, clients)
		if not self.last:
			maximum = [m[-1] for m in money_per_company]
			index_best_company = maximum.index(max(maximum))
			maximum[index_best_company] = 0
			index_company = maximum.index(max(maximum))
		else:
			minimum = [m[-1] for m in money_per_company]
			index_company = minimum.index(min(minimum))
		# values for index_company for different values of preferences
		values_company_preferences = []
		values_best_company = []
		preferences_values = list(np.array(list(range(20,101,1)))/100)
		for pref in preferences_values:
			for cli in clients:
				cli.utilities[index_company]=pref
			money_per_company = s.testCicle(g, s.generateMoneyPerCompany(), companies, cpy_companies, clients)
			values_company_preferences.append(money_per_company[index_company][-1])
			if not self.last:
				values_best_company.append(money_per_company[index_best_company][-1])
			gc.collect()
		
		if not self.last:
			self.legend[0] = self.legend[0] + str(companies[index_company][1].pos)
			self.legend[1] = self.legend[1] + str(companies[index_best_company][1].pos)
			self.drawPlot(preferences_values, values_company_preferences, values_best_company, "Preferences", "Preferences (%)", "Money", self.legend, color=[graph_utils.colormap[companies[index_company][0]], graph_utils.colormap[companies[index_best_company][0]]])
		else:
			self.legend[0] = [self.legend[0][0] + str(companies[index_company][1].pos)]
			s.drawPlot(preferences_values, values_company_preferences, "Preferences", "Preferences (%)", "Money", self.legend, per=0.05, color=graph_utils.colormap[companies[index_company][0]])

class LastPreferences(Preferences):
	def __init__(self, graphType):
		super().__init__(graphType, legend=[["Company w/ worst profit: "]], last=True)

class SecondAndBestPreferences(Preferences):
	def __init__(self, graphType):
		super().__init__(graphType, legend=["2nd Company w/ best profit: ","1st Company w/ best profit: "])
		
class Menu(object):
	def clearWindow(self):
		print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
		print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
		print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
		print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
		print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
		# print("\n-------------------------------------------------------------")

	def levelVerbosity(self):
		if verbosity and verbosity_events and verbosity_companies:
			return 4
		elif verbosity and verbosity_companies:
			return 3
		elif verbosity and verbosity_events:
			return 2
		elif verbosity:
			return 1
		else:
			return 5

	def changeVerbosity(self):
		global verbosity, verbosity_events, verbosity_companies, simulating
		while(True):
			print(f"\nCurrent level of verbosity: {self.levelVerbosity()}")
			print("\nType number to choose verbosity level:")
			print("1 - Only number of iterations")
			print("2 - Iterations and Events (Explosions)")
			print("3 - Iterations and Companies' Failures and Winnings")
			print("4 - All above")
			print("5 - None")
			print("0 - Terminate\n")
			try:
				verbosity_level = int(input("Option:  "))
			except Exception as e:
				self.clearWindow()
				print("\nPlease enter a valid integer\n")
				continue
			if verbosity_level == 1:
				verbosity = True
				return
			elif verbosity_level == 2:
				verbosity = True
				verbosity_events = True
				return
			elif verbosity_level == 3:
				verbosity = True
				verbosity_companies = True
				return
			elif verbosity_level == 4:
				verbosity = True
				verbosity_events = True
				verbosity_companies = True
				return
			elif verbosity_level == 5:
				verbosity = False
				verbosity_level = False
				verbosity_companies = False
				return
			elif verbosity_level == 0:
				simulating = False
				return
			else:
				self.clearWindow()
				print(f"\n{verbosity_level} is not a valid verbosity level\n")
				continue

	def changeGraphType(self):
		global graphType
		graphType = "scale-free" if graphType == "random" else "random"

	def changeIterations(self):
		global iterations
		while True:
			try:
				print(f"\nCurrent number of iterations per test: {iterations}")
				iters = int(input("New number:  "))
				iterations = iters if iters > 0 else tests
				return
			except Exception as e:
				print("\nPlease enter a valid integer\n")

	def changeTests(self):
		global tests
		while True:
			try:
				print(f"\nCurrent number of tests per simulation: {tests}")
				num_tests = int(input("New number:  "))
				tests = num_tests if num_tests > 0 else tests
				return
			except Exception as e:
				print("\nPlease enter a valid integer\n")

	def defaultValues(self):
		global graphType, tests, iterations, verbosity, verbosity_events, verbosity_companies
		graphType = "random"
		tests = 30
		iterations = 100
		verbosity = False
		verbosity_events = False 
		verbosity_companies = False

	def options(self):
		global simulating
		while True:
			print("\nType number to choose option:")
			print("1 - Choose verbosity")
			print("2 - Change type of the graph (Random or Scale Free)")
			print("3 - Change number of iterations per test")
			print("4 - Change number of tests per simulation")
			print("5 - Restore default values")
			print("6 - None")
			print("0 - Terminate\n")
			try:
				option = int(input("Option:  "))
			except Exception as e:
				self.clearWindow()
				print("\nPlease enter a valid integer\n")
				continue
			if option == 1:
				self.clearWindow()
				self.changeVerbosity()
				return
			elif option == 2:
				self.changeGraphType()
				return
			elif option == 3:
				self.changeIterations()
				return
			elif option == 4:
				self.changeTests()
				return
			elif option == 5:
				self.defaultValues()
				return
			elif option == 6:
				return
			elif option == 0:
				simulating = False
				return
			else:
				self.clearWindow()
				print(f"\n{option} in not a valid option...\n")
				continue

	def choosePreference(self):
		global simulating
		while True:
			print("\nType number to choose which preferences to vary:")
			print("1 - Varying the clients' preferences for the worst company")
			print("2 - Varying the clients' preferences for the second best company")
			print("3 - None")
			print("0 - Terminate\n")
			try:
				option = int(input("Option:  "))
			except Exception as e:
				self.clearWindow()
				print("\nPlease enter a valid integer\n")
				continue
			if option == 1:
				preferences = LastPreferences(graphType)
				try:
					preferences.run()
				except Warning as e:
					print("error")
					return		
				return
			elif option == 2:
				preferences = SecondAndBestPreferences(graphType)
				try:
					preferences.run()
				except Warning as e:
					print("error")
					return
				return
			elif option == 3:
				return
			elif option == 0:
				simulating = False
				return
			else:
				self.clearWindow()
				print(f"\n{option} in not a valid option...\n")
				continue

	def start(self):
		global simulating
		self.clearWindow()
		while simulating:
			print(f"\nCurrent graph type: {graphType}")
			print("\nType number to choose simulation:")
			print("1 - Money through time")
			print("2 - Varying the Graph's Type (Random and Scale-free)")
			print("3 - Varying the Number of Companies")
			print("4 - Varying the Number of Nodes w/ Number of trucks 8 and 16 (takes a lot of time)")
			print("5 - Varying the Trucks' Threshold")
			print("6 - Varying the Percentage of Trucks' Explosion")
			print("7 - Varying the Percentage of Edges' Explosion")
			print("8 - Varying the Most Profit Company's Profit Margin")
			print("9 - Varying the clients' preferences for a company")
			print("-1 - Options")
			
			print("0 - Terminate\n")
			try:
				simulation = int(input("Option:  "))
			except Exception as e:
				self.clearWindow()
				print("\nPlease enter a valid integer\n")
				continue
			
			graph_utils.colormap = []
			if simulation == 0:
				simulating = False
			elif simulation == -1:
				self.clearWindow()
				self.options()
			elif simulation == 1:
				moneyTime = MoneyTime(graphType)
				moneyTime.run()
			elif simulation == 2:
				graphTypes = GraphTypes(graphType)
				graphTypes.run()
			elif simulation == 3:
				numCompanies = NumCompanies(graphType)
				numCompanies.run()
			elif simulation == 4:
				numNodes = NumNodes(graphType)
				numNodes.run()
			elif simulation == 5:
				threshold = Threshold(graphType)
				threshold.run()
			elif simulation == 6:
				truckExplosion = TruckExplosion(graphType)
				truckExplosion.run()
			elif simulation == 7:
				edgeExplosion = EdgeExplosion(graphType)
				edgeExplosion.run()
			elif simulation == 8:
				profitMargin = ProfitMargin(graphType)
				profitMargin.run()
			elif simulation == 9:
				self.clearWindow()
				self.choosePreference()
			else:
				self.clearWindow()
				print(f"\n{simulation} is not a valid simulation...\n")
				continue
			self.clearWindow()
	
# initial type of the graphs
graphType = "random"
# initial number of tests per simulation
tests = 30
# initial number os iterations per test
iterations = 100
# verbosity levels
verbosity = False
verbosity_events = False 
verbosity_companies = False
# simulation flag
simulating = True

menu = Menu()
menu.start()


