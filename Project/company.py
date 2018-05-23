#!/usr/bin/python
from truck import *
from offer import *
import math
from random import *

class Company:
	def __init__(self, pos, money, name, g, uni_cost=1, truck_threshold=100, profit_margin=1.5, tax=0.05):
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
			return False
		else:
			costs = [t.getPrice(item) for t in free_trucks]
			minimum = min(costs)
		return minimum

	def chooseTruck(self, item):
		free_trucks = [t for t in self.trucks if t.getStatus() == "livre"]
		if free_trucks == []:
			return 
		else:
			costs = [t.getPrice(item) for t in free_trucks]
			minimum = min(costs)
		if not minimum:
			return False
		truck = free_trucks[costs.index(minimum)]
		truck.addItem(item)
		return True

	def updateTrucks(self):
		free_trucks = [t for t in self.trucks if t.getStatus() == "livre"]
		for t in free_trucks:
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
		if self.money <=0:
			offer.setValue(math.inf)
			return offer

		offer.setValue(offer.getQuantity()*self.uniCost)
		minimum = self.getBestPrice(offer)
		if not minimum:
			offer.setValue(math.inf)
			return offer

		val = (offer.getValue()+minimum)*self.profit_margin
		offer.setValue(val*self.tax + val)
		return offer

	def setOffer(self, offer):
		self.offers.append(offer)
		self.money -= self.tax*offer.getValue()

	def cleanOldOffers(self, i):
		for o in self.offers:
			if i - o.getTimestamp() > 5:
				self.offers.remove(o)

	def go(self, g, i):
		# print(f"{self} -- {offers}")
		self.graph = g
		
		for t in self.trucks:
			t.go(g)
		
		self.cleanOldOffers(i)

		for o in self.offers:
			success = self.chooseTruck(o)
			self.offers.remove(o)
		
		# if not not self.offers:
			# print(len(self.offers), " not empty and num free trucks ", len([t for t in self.trucks if t.getStatus() == "livre"]), "   ", self)

		self.updateTrucks()

