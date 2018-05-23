import networkx as nx
import matplotlib.pylab as plt
from random import randint, sample
import graph_utils
from company import *
from truck import *

class Simulation(object):
	def __init__(self, 
		n_nodes, graph_type, graph_param, graph_min_weight, graph_max_weight,
		n_companies, n_trucks, truck_threshold, company_init_money,
		tax, p_edge_explosion, p_truck_explosion):

		# network params
		self.n_nodes = n_nodes
		self.graph_type = graph_type
		self.graph_param = graph_param
		self.graph_min_weight = graph_min_weight
		self.graph_max_weight = graph_max_weight
		
		# agents params
		self.n_companies = n_companies
		self.n_trucks = n_trucks
		self.truck_threshold = truck_threshold
		self.company_init_money = company_init_money

		# events params
		self.tax = tax
		self.p_edge_explosion = p_edge_explosion
		self.p_truck_explosion = p_truck_explosion

		# offers params
		# -> profit margin
		# -> number of offers
		# -> offers preferences
		

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
		companies = [(x, Company(x, self.company_init_money, company_names[i], graph)) for i,x in enumerate(companies)]
		print(companies)
		graph_utils.set_company_nodes(graph, companies)
		return companies

	def generate_trucks(self, graph, companies):
		for c in companies:
			c[1].setTrucks([Truck(i, c[1], graph) for i in range(self.n_trucks)])

	def generate_clients(self, graph, companies):
		return [Client(n, 
					[c[1] for c in companies], 
					min_offer_val=self.min_offer_val, 
					max_offer_val=self.max_offer_val) for n in g.nodes if "company" not in g.node[n]]

	def do_edge_explosion(self, t,graph):
		try:
			e = random.choice(list(graph.edges()))
		except Exception as e:
			print(f"\tall edges removed t= {t}\t")
			exit()
		graph.remove_edge(e[0],e[1])
		print(f"\tedge removed:\t {e[0]} -- {e[1]} (t={t})")

	def do_game_over(self, companies, company, graph,t):
		print(f"GAME OVER FOR {company[1]} at t={t}")
		companies.remove(company)
		del graph.node[company[0]]['company']
		graph_utils.colormap[company[0]]= "#%06x" % 0xDDDDDD

	def run(self):
		g = self.build_graph()
		companies = self.generate_companies(g)
		self.generate_trucks(g, companies)
	    clients = self.generate_clients(g, companies)

		for i in range(10000):
			if not len(companies):
				print("NO MORE COMPANIES")
				break
			if random() < p_remove:
				do_edge_explosion(i,g)

			for cli in clients:
				cli.go()

			for c in companies:
				if c[1].money <= 0:
					do_game_over(companies, c, g,i)
					continue

				# offers = generate_offers(clients)
				# c[1].money -= c[1].money*0.05
				c[1].go(g)

		for c in companies:
			print(f"SURVIVOR: {c} -- t={i}")


def main():
	s = Simulation(
		n_nodes=15, graph_type="random", graph_param=0.2, 
		graph_min_weight=1, graph_max_weight=10,
		n_companies=5, n_trucks=7, truck_threshold=25, company_init_money=1000,
		tax=0.05, p_edge_explosion=0.0002, p_truck_explosion=0.01)
	
	s.run()

if __name__ == '__main__':
	main()
	
