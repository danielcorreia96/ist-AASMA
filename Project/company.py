#!/usr/bin/python
from truck import *
import math
import random

class Company:
	def __init__(self, pos, money, name, g):
		self.pos = pos
		self.money = money
		self.name = name
		self.offers = []
		self.trucks = []
		self.graph = g

	def __repr__(self):
		return f"Company {self.name} with {self.money} euros"

	def setTrucks(self, trucks):
		self.trucks = trucks

	def chooseTruck(self, item):
		free_trucks = [t for t in self.trucks if t.getStatus() == "livre"]
		if free_trucks == []:
			return
		else:
			costs = [t.getPrice(item) for t in free_trucks]
			minimum = min(costs)
			truck = free_trucks[costs.index(minimum)]
			truck.addItem(item)

	def updateTrucks(self):
		for t in self.trucks:
			if t.getCapacity() <= 25: # muito baixo trucks não vão distribuir
				t.setStatus("ocupado")

	def receiveMoney(self, value, truck):
		self.money += value
		truck.setStatus("livre")

	def truckExplosion(self):
		truck = random.choice(self.trucks)
		self.trucks.remove(truck)
		# vai-se subtrair o custo do caminho feito até agora
		
	def go(self, g, offers):
		# print(f"{self} -- {offers}")
		self.graph = g
		
		for t in self.trucks:
			t.go(g)
		
		self.offers += offers

		for o in self.offers:
			self.chooseTruck(o)
			self.offers.remove(o)

		self.updateTrucks()

