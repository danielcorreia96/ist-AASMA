#!/usr/bin/python
from company import *
from offer import *
import math
import numpy as np
from random import *

class Client:
	def __init__(self, pos, companies):
		# self.money = 5 SALARIO MINIMO???
		self.pos = pos
		self.risk = random()
		self.utilities = self.calculateUtilities(companies)
		self.companies = companies

	def __repr__(self):
		return f"Client {self.pos} with utilities: {self.utilities} and a risk of {self.risk}"

	def calculateUtilities(self,companies):
		pref = np.array([random() for _ in range(len(companies))])
		return list(pref/sum(pref))

	def offer(self):
		return Offer(self, randint(20,100)) if random() < self.risk else None

	def chooseBestBid(self, bids):
		bids_values = [self.utilities[i]*bids[i] for i in range(len(bids))]
		return bids_values.index(min(bids_values))

	def go(self):
		offer = self.offer();
		if offer != None:
			company = self.chooseBestBid([c.getBid(offer).getValue() for c in self.companies])
			if offer.getValue() != math.inf:
				self.companies[company].setOffer(offer)
				# print("Client ", self.pos, " requesting offer from ", self.companies[company].pos)