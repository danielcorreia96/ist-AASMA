#!/usr/bin/python
class Offer:
	def __init__(self, target, quantity):
		self.quantity = quantity
		self.value = None # value of item
		self.target = target # client

	def __repr__(self):
		return f"Item with value {self.value} to client {self.target}"

	def getValue(self):
		return self.value

	def getTarget(self):
		return self.target.pos

	def setValue(self, value):
		self.value = value

	def getQuantity(self):
		return self.quantity