#!/usr/bin/python
from truck import *
from offer import *
import math
from random import *

class Company:
	def __init__(self, pos, money, name, g, uni_cost=1, truck_threshold=25, profit_margin=1.5, tax=0.05):
		self.pos = pos
		self.money = money
		self.name = name
		self.offers = []
		self.trucks = []
		self.graph = g
		self.uniCost = uni_cost
		self.truck_threshold = truck_threshold
		self.profit_margin = profit_margin
		self.tax = tax

	def __repr__(self):
		return f"Company {self.name} with {self.money} euros"

	def setTrucks(self, trucks):
		self.trucks = trucks

	def getBestPrice(self, item):
		free_trucks = [t for t in self.trucks if t.getStatus() == "livre"]
		if free_trucks == []:
			return
		else:
			costs = [t.getPrice(item) for t in free_trucks]
			minimum = min(costs)
		return minimum, costs, free_trucks

	def chooseTruck(self, item):
		minimum, costs, free_trucks = self.getBestPrice(item)
		if not minimum:
			return
		truck = free_trucks[costs.index(minimum)]
		truck.addItem(item)

	def updateTrucks(self):
		for t in self.trucks:
			if t.getCapacity() <= self.truck_threshold: # muito baixo trucks não vão distribuir
				t.setStatus("ocupado")

	def receiveMoney(self, value, truck):
		self.money += value
		truck.setStatus("livre")

	def truckExplosion(self):
		truck = random.choice(self.trucks)
		self.trucks.remove(truck)
		# vai-se subtrair o custo do caminho feito até agora
		
	def getBid(self, offer):
		offer.setValue(offer.getQuantity()*self.uniCost)
		minimum = self.getBestPrice(offer)
		if not minimum:
			offer.setValue(math.inf)
			return offer
		offer.setValue((offer.getValue()+minimum[0])*self.profit_margin)
		return offer

	def setOffer(self, offer):
		self.offers += [offer]
		self.money -= self.tax*offer.getValue()

	def go(self, g):
		# print(f"{self} -- {offers}")
		# print(self.offers)
		self.graph = g
		
		for t in self.trucks:
			t.go(g)
		
		# self.offers += offers

		for o in self.offers:
			self.chooseTruck(o)
			self.offers.remove(o)

		self.updateTrucks()

