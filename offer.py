#!/usr/bin/python
class Offer:
	def __init__(self, target, quantity, timestamp):
		self.quantity = quantity
		self.value = None # value of item
		self.target = target # client
		self.timestamp = timestamp
	def __repr__(self):
		return f"Item with value {self.value} to client {self.target}"

	def getValue(self):
		return self.value

	def getTarget(self):
		return self.target

	def setValue(self, value):
		self.value = value

	def getQuantity(self):
		return self.quantity

	def getTimestamp(self):
		return self.timestamp