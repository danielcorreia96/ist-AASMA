#!/usr/bin/python
# File:	item.py
# Description:	Item node
# Author:	Pedro M Orvalho & Daniel Correia
# Created on:	03-05-2018 14:16:16
# Usage:	python item.py
# Python version:	3.6.4

class Item:
	def __init__(self, value, target):
		self.value = value # value of item
		self.target = target # client

	def getValue(self):
		return self.value

	def getTarget(self):
		return self.target