import re
import string


"""General utility module"""


def flatten(l):
	return [item for sublist in l for item in sublist]

def is_sublist(subli, li):
	'''Check if X is a sublist of Y

	Args:
		subli (list): Sublist
		li (list): List in which the sublist should occur
	
	Returns:
		bool: subli is sublist of li
	'''
	if subli == []: return True
	if li == []: return False
	return set(subli).issubset(set(li))

def is_exact_sublist(subli, li):
	'''Sees if X is a sublist of Y and takes the exact order into account

	Args:
		subli (list): Sublist
		li (list): List in which the sublist should occur
	
	Returns:
		int: Index of first occurence of sublist in list
	'''
	for i in range(len(li)-len(subli)):
		if li[i:i+len(subli)] == subli:
			return i
	else:
		return -1

def remove_punct(str):
	return re.sub(r"[,!?\.]", '', str).strip()

def text(a_list):
	return " ".join(str(x) for x in a_list)

def remove_duplicates(self, arr): # Potentially obsolete
	li = list()
	li_add = li.append
	return [ x for x in arr if not (x in li or li_add(x))]

def multiline(string):
	return [l.split(" ") for l in string.splitlines()]

def tab(string):
	if string.startswith("\t"):
		return True
	return False

def is_comment(line):
	if line[0] == "#":
		return True
	return False	

def occurence_list(li):
	res = []
	for o in li:
		if str(o) not in res and o >= 0:
			res.append(str(o))
	if res:
		return ', '.join(res)
	return "Does not occur, deducted"

