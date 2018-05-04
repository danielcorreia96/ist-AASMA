#!/usr/bin/python
class Item:
	def __init__(self, value, target):
		self.value = value # value of item
		self.target = target # client

	def __repr__(self):
		return f"Item with value {self.value} to client {self.target}"

	def getValue(self):
		return self.value

	def getTarget(self):
		return self.target