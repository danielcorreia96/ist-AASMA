#!/usr/bin/python
import networkx as nx
from company import *
from item import *
import math

map_status = ["ocupado", "livre"]
# status
#  0 - ocupado
#  1 - livre 

class Truck:
	def __init__(self, id, owner, g, capacity = 300):
		self.id = id
		self.owner = owner
		self.status = 1
		self.items = []
		self.capacity = capacity
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

	def getCapacity(self):
		return self.capacity - self.totalValue 

	def updateGraph(self, g):
		self.graph = g

	def addItem(self, item): # atribuir um pedido a um camiao
		self.items.append(item)
		self.totalValue += item.getValue()

	def go(self, g):
		if self.getStatus() == "livre":
			return
		print(self)
		self.calculate_path()
		# calcular o caminho mais curto entre todos os vertices de destino
		# calcular preco da viagem
		# notificar

	def calculate_path(self):
		print(self.items)

	def getPrice(self, item): # devolver o melhor custo se adicionar o item ao truck
		if self.getCapacity() < item.getValue() or self.getStatus() == "ocupado":
			return math.inf

		costs = [nx.shortest_path_length(self.graph,source=self.owner.pos,target=item.getTarget())]
		costs += [nx.shortest_path_length(self.graph,source=i.getTarget(),target=item.getTarget()) for i in self.items]
		return min(costs)

