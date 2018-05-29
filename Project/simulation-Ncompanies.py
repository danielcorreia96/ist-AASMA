import networkx as nx
import matplotlib.pylab as plt
import matplotlib.animation as animation
import copy
from random import *
import numpy as np
import graph_utils
from company import *
from truck import *
from client import *

class Simulation(object):
	def __init__(self, 
		n_nodes, graph_type, graph_param, graph_min_weight, graph_max_weight,
		n_companies, n_trucks, 
		truck_threshold, company_init_money, uni_cost, profit_margin, tax,
		risk, min_offer_val, max_offer_val,
		existence_tax, p_edge_explosion, p_truck_explosion):

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
				p=self.graph_param,
				min_weight=self.graph_min_weight, 
				max_weight=self.graph_max_weight)

	def generate_companies(self, graph):
		company_names = ["A", "B", "C", "D","E","F","G","H","I","J","K"]
		companies = sample(list(graph.nodes()), k=self.n_companies)
		companies = [(x, Company(x, self.company_init_money, 
						company_names[i], graph,
						uni_cost=self.uni_cost,
						truck_threshold=self.truck_threshold,
						profit_margin=self.profit_margin,
						tax=self.tax)) for i,x in enumerate(companies)]
		print(companies)
		# graph_utils.colormap = []
		graph_utils.set_ncompany_nodes(graph, companies)
		return companies

	# def resetCompanies(self, companies):
		

	def generate_trucks(self, graph, companies):
		for c in companies:
			c[1].setTrucks([Truck(i, c[1], graph) for i in range(self.n_trucks)])

	def calculateUtilities(self):
		# pref = np.array([(randint(1,99)/100) for _ in range(self.n_companies)])
		# return list(pref/sum(pref))
		return [1/self.n_companies for _ in range(self.n_companies)]

	def generate_clients(self, graph, companies):
		i=0
		return [Client(n, 
					[c[1] for c in companies],
					risk=self.risk,
					utilities=self.calculateUtilities(),
					min_offer_val=self.min_offer_val, 
					max_offer_val=self.max_offer_val) for n in graph.nodes if "company" not in graph.node[n]]

	def do_edge_explosion(self, t,graph):
		try:
			e = choice(list(graph.edges()))
		except Exception as e:
			print(f"\tall edges removed t= {t}\t")
			exit()
		graph.remove_edge(e[0],e[1])
		print(f"\tedge removed:\t {e[0]} -- {e[1]} (t={t})")

	def do_game_over(self, companies, company, graph,t):
		# print(f"GAME OVER FOR {company[1]} at t={t} -- offers={company[1].completedOffers}")
		companies.remove(company)
		# del graph.node[company[0]]['company']
		# graph_utils.colormap[company[0]]= "#%06x" % 0xDDDDDD
		return company[1]

	def drawPlot(self, y_data, x_data, title, xlabel, ylabel, legend):
		plt.title(title)
		plt.xlabel(xlabel)
		plt.ylabel(ylabel)
		
		for i in range(len(x_data)):
			error = 0.05 * np.array(x_data[i])
			if not i:
				plt.scatter(y_data[i], x_data[i], label=legend[0], color="red")
			else:
				plt.scatter(y_data[i], x_data[i], color="red")
			plt.errorbar(y_data[i], x_data[i], yerr=error, color="red")
		plt.legend()
		plt.show()

	def run(self, g, companies, clients, iterations):
		# print(companies)
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
			print(f"SURVIVOR: {c} -- t={i} -- offers={c[1].completedOffers}")
			self.completedOffers += c[1].getCompletedOffers()

		print(f"OFFERS COMPLETED: {self.completedOffers}")
		return money_per_company

def main():

	s = Simulation(
		n_nodes=30, graph_type="random", graph_param=0.2, 
		graph_min_weight=1, graph_max_weight=10,
		n_companies=5, n_trucks=7, truck_threshold=100, company_init_money=2500,
		uni_cost=1, profit_margin=1.5, tax=0.05,
		risk=(randint(1,99)/100),
		min_offer_val=25, max_offer_val=80,
		existence_tax=0.05, p_edge_explosion=0.000, p_truck_explosion=0.01)
	
	g = s.build_graph()
	money_per_company = []
	all_costs = []
	iterations = 100
	tests = 30
	list_len_companies = list(range(1,11))
	for n_companies in list_len_companies:
		s.n_companies = n_companies
		money_per_company = []
		companies = s.generate_companies(g)
		s.generate_trucks(g, companies)
		cpy_companies = [(c[0], copy.deepcopy(c[1])) for c in companies]
		clients = s.generate_clients(g, cpy_companies)
		# graph_utils.draw_graph(g)
		# graph_utils.show_graphs()
		for _ in range(s.n_companies):
			money_per_company.append([])
		
		for _ in range(iterations):
			for m in money_per_company:
				m.append(0)

		for i in range(tests):
			print(f"\n\n\nITERATION {i}\n\n\n")
			mc = s.run(g, list(cpy_companies), list(clients), iterations)
			for i in range(len(mc)):
				money_per_company[i] = list(np.array(money_per_company[i]) + np.array(mc[i]))
			cpy_companies = [(c[0], copy.deepcopy(c[1])) for c in companies]
			for cli in clients:
				cli.setCompanies([c[1] for c in cpy_companies])

		for c in companies:
			del g.node[c[0]]['company']

		for mc in money_per_company:
			mc = np.array(mc)/tests
		
		maximum = [i[-1] for i in money_per_company]
		all_costs += [max(maximum)]

	legend = ["Company w/ most profit"]
	s.drawPlot(list_len_companies, all_costs, "Number of Companies", "Number of Companies", "Money", legend)

	return g
if __name__ == '__main__':
	g = main()
	
