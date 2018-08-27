from itertools import *
import random

def one_in(n):
	return random.random() < 1/n

def take(s, n):
	return islice(s,n)

def shift(s, by):
	return s[by:] + s[:by]

def sign(i):
	if i<0:
		return -1
	elif i==0:
		return 0
	else:
		return 1

if __name__ == '__main__':
	print(shift(1, list(range(10))))
	print(shift(2, list(range(10))))
