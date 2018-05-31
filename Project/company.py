#!/usr/bin/python
from truck import *
from offer import *
import math
from random import *

class Company:
	def __init__(self, pos, money, name, g, uni_cost=1, truck_threshold=280, profit_margin=1.5, tax=0.05):
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
		self.completedOffers = 0
		
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
			# print(costs)
			minimum = min(costs)
		return minimum

	def chooseTruck(self, item):
		free_trucks = [t for t in self.trucks if t.getStatus() == "livre"]
		if free_trucks == []:
			return False
		else:
			costs = [t.getPrice(item) for t in free_trucks]
			minimum = min(costs)

		if minimum == math.inf:
			return False

		truck = free_trucks[costs.index(minimum)]
		truck.addItem(item)
		return True

	def updateTrucks(self):
		free_trucks = [t for t in self.trucks if t.getStatus() == "livre"]
		for t in free_trucks:
			if t.getCapacity() < self.truck_threshold: # muito baixo trucks não vão distribuir
				t.setStatus("ocupado")

	def receiveMoney(self, value, truck):
		self.money += value
		truck.setStatus("livre")

	def truckExplosion(self):
		truck = choice(self.trucks)
		self.trucks.remove(truck)
		# vai-se subtrair o custo do caminho feito até agora
		
	def getBid(self, offer):
		if self.money <=0:
			return math.inf

		minimum = self.getBestPrice(offer)

		if minimum is False or minimum == math.inf:
			return math.inf

		val = (offer.getQuantity()*self.uniCost+minimum)*self.profit_margin
	
		return val*self.tax + val if self.money >= val*self.tax else math.inf

	def setOffer(self, offer):
		self.offers.append(offer)
		self.money -= self.tax*offer.getValue()

	def setUniCost(self, uniCost):
		self.uniCost = uniCost
	
	def setTruckThreshold(self, threshold):
		self.truck_threshold = threshold

	def cleanOldOffers(self, i):
		for o in self.offers:
			if i - o.getTimestamp() > 5:
				self.offers.remove(o)

	def getCompletedOffers(self):
		return self.completedOffers

	def go(self, g, i):
		# print(f"{self} -- {self.offers}")
		self.graph = g
		
		for t in self.trucks:
			t.go(g)
		
		
		# self.cleanOldOffers(i)

		for o in self.offers:
			success = self.chooseTruck(o)
			if success:
				self.offers.remove(o)
				self.completedOffers += 1
		
		# if not not self.offers:
			# print(len(self.offers), " not empty and num free trucks ", len([t for t in self.trucks if t.getStatus() == "livre"]), "   ", self)

		self.updateTrucks()

