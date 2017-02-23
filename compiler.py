import utils
from parser import *

class var:
	def __init__(self, t, name):
		self.name = name
		self.type = t

def compile(data, char="\n", names = {}):
	output = []

	i = 0
	while i < len(data):
		my_node = data[i]

		next_node = None
		if i+1 < len(data):
			next_node = data[i+1]

		next_node_2 = None
		if i+2 < len(data):
			next_node_2 = data[i+2]

		if my_node.type == NAME:
			if next_node and next_node.type == NAME and next_node.value == "=":
				if next_node_2 and next_node_2.type == FUNCTION:
					output.append("void " + my_node.value + "() {\n" + compile(next_node_2.value) + "\n}")
					data[my_node.value] = var(FUNCTION, my_node.value)
					i += 2
				elif next_node_2 and next_node_2.type == NUMBER:
					output.append("int " + my_node.value + " = " + str(next_node_2.value) + ";")
					data[my_node.value] = var(NUMBER, my_node.value)
					i += 2
				elif next_node_2 and next_node_2.type == FLOAT:
					output.append("float " + my_node.value + " = " + str(next_node_2.value) + "f;")
					data[my_node.value] = var(FLOAT, my_node.value)
					i += 2
			elif next_node and next_node.type == ARRAY:
				params, func = compile_array(next_node.value)
				if func != "":
					output.append(my_node.value + "(" + params + ") " + func)
				else:
					output.append(my_node.value + "(" + params + ");")

		i += 1

	return char.join(output)

def compile_array(data, names = {}):
	output = []
	output_2 = []

	i = 0
	while i < len(data):
		my_node = data[i]

		next_node = None
		if i+1 < len(data):
			next_node = data[i+1]

		if my_node.type == NAME:
			if next_node and next_node.type == ARRAY:
				output.append(my_node.value + "(" + compile_array(next_node.value)[0] + ")")
			else:
				output.append(my_node.value)
		elif my_node.type == NUMBER:
			output.append(my_node.value)
		elif my_node.type == STR:
			output.append("\"" + my_node.value + "\"")
		elif my_node.type == FUNCTION:
			output_2.append("{\n" + compile(my_node.value) + "\n}")

		i += 1

	return ",".join(output), "\n".join(output_2)
