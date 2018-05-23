#!/usr/bin/python
import networkx as nx
from company import *
from offer import *
from itertools import tee
import math

map_status = ["ocupado", "livre"]
# status
#  0 - ocupado
#  1 - livre 

class Truck:
	def __init__(self, id, owner, g, capacity = 300):
		self.id = id
		self.pos = owner.pos
		self.owner = owner
		self.status = 1
		self.items = []
		self.totalCapacity = capacity
		self.capacity = 0
		self.totalValue = 0
		self.graph = g

	def __repr__(self):
		return f"Truck {self.id} from company {self.owner} with {len(self.items)} items, with total value {self.totalValue}"

	def getStatus(self):
		return map_status[self.status]

	def setStatus(self, status):
		self.status = map_status.index(status)

	def getId(self):
		return self.id

	def getCapacity(self): # o espaco que o truck ainda tem
		return self.totalCapacity - self.capacity 

	def updateGraph(self, g):
		self.graph = g

	def addItem(self, item): # atribuir um pedido a um camiao
		# print(f"item added to company: {self.owner}")
		for curr_item in self.items:
			if curr_item.target == item.target:
				curr_item.value += item.value
				self.totalValue += item.value
				self.capacity += item.getQuantity()
				return
		self.items.append(item)
		self.totalValue += item.getValue()
		self.capacity += item.getQuantity()

	def go(self, g):
		# atualizar grafo
		self.updateGraph(g)

		if self.getStatus() == "livre":
			return		

		for item in self.items:
			if self.pos == item.getTarget():
				# print("deliver item to client")
				self.items.remove(item)
				# print(self.items)
				if self.items == []:
					# print(f"no more items. teleport to {self.owner}")
					self.finalStep(1)
					return

		# 1. Get next position to move truck
		try:
			next_node = self.get_next_node_in_path()
		except Exception as e:
			self.finalStep(-1)
			return
		
		# 2. Move truck and update profit
		next = next_node[1][1]
		self.totalValue -= self.graph[self.pos][next]["weight"]
		self.pos = next
		# calcular preco da viagem
		# notificar

	def get_next_node_in_path(self):
		def pairwise(iterable):
			a, b = tee(iterable)
			next(b, None)
			return zip(a, b)

		all_sps = [(item, nx.shortest_path(self.graph, self.pos, item.target)) for item in self.items]
		all_sps_costs = [(sum([self.graph[u][v]["weight"] for (u,v) in pairwise(sp)]), sp, item) for (item, sp) in all_sps]
		# print(all_sps_costs)
		return min(all_sps_costs, key=lambda x: x[0])

	def finalStep(self, signal):
		self.pos = self.owner.pos
		self.owner.money = self.owner.money + signal*self.totalValue
		self.totalValue = 0
		self.capacity = 0
		self.setStatus("livre")
		# print(f"updated company: {self.owner}")

	def getPrice(self, item): # devolver o melhor custo se adicionar o item ao truck
		if self.getCapacity() < item.getQuantity() or self.getStatus() == "ocupado":
			return math.inf
		try:
			costs = [nx.shortest_path_length(self.graph,source=self.owner.pos,target=item.getTarget())]
			costs += [nx.shortest_path_length(self.graph,source=i.getTarget(),target=item.getTarget()) for i in self.items]
		except Exception as e:
			return math.inf
		
		return min(costs)

