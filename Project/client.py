#!/usr/bin/python
from company import *
from offer import *
import math
import numpy as np
from random import *

class Client:
	def __init__(self, pos, companies, risk=(randint(1,99)/100), utilities=[], min_offer_val=20, max_offer_val=100):
		self.pos = pos
		self.risk = risk
		self.utilities = utilities if utilities != [] else self.calculateUtilities(companies)
		self.companies = companies
		self.min_offer_val = min_offer_val
		self.max_offer_val = max_offer_val

	def __repr__(self):
		return f"Client {self.pos} with utilities: {self.utilities} and a risk of {self.risk}"

	def calculateUtilities(self,companies):
		pref = np.array([(randint(1,99)/100) for _ in range(len(companies))])
		return list(pref/sum(pref))

	def generate_offer(self, i):
		return Offer(self.pos, randint(self.min_offer_val, self.max_offer_val), i) if (randint(1,99)/100) < self.risk else None

	def chooseBestBid(self, bids):
		bids_values = [(1-self.utilities[i])*bids[i] for i in range(len(bids))]
		return bids_values.index(min(bids_values))

	def removeCompany(self, company):
		self.companies.remove(company)

	def setCompanies(self, companies):
		self.companies = companies
		
	def go(self, i):
		offer = self.generate_offer(i);
		if offer != None:
			offers = [c.getBid(offer) for c in self.companies]
			company = self.chooseBestBid([o.getValue() for o in offers])
			# print("Client ", self.pos, " requesting offer from ", self.companies[company].pos, "  ",offers[company].getValue(),"  ", self.companies)
			if offers[company].getValue() != math.inf:
				self.companies[company].setOffer(offers[company])
				# print("Client ", self.pos, " requesting offer from ", self.companies[company].pos, "    ", self.companies)