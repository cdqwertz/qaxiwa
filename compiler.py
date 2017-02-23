import utils, copy
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

		#get next nodes
		next_node = None
		if i+1 < len(data):
			next_node = data[i+1]

		next_node_2 = None
		if i+2 < len(data):
			next_node_2 = data[i+2]

		if my_node.type == NAME:
			if next_node and next_node.type == NAME and next_node.value == "=":
				if next_node_2:
					t = next_node_2.type

					#does the name exist?
					if my_node.value in names:
						if t == NAME:
							if next_node_2.value in names:
								if names[next_node_2.value].type == names[my_node.value].type:
									if t == FLOAT:
										output.append(my_node.value + " = " + str(next_node_2.value) + "f;")
									elif t == NUMBER or t == BOOL:
										output.append(my_node.value + " = " + str(next_node_2.value) + ";")
						else:
							if names[my_node.value].type == t:
								if t == FLOAT:
									output.append(my_node.value + " = " + str(next_node_2.value) + "f;")
								elif t == NUMBER or t == BOOL:
									output.append(my_node.value + " = " + str(next_node_2.value) + ";")

					else:
						t = next_node_2.type
						if t == NAME:
							if next_node_2.value in names:
								t = names[next_node_2.value].type

								if t == NUMBER:
									output.append("int " + my_node.value + " = " + str(next_node_2.value) + ";")
									names[my_node.value] = var(NUMBER, my_node.value)
									i += 2
								elif t == FLOAT:
									output.append("float " + my_node.value + " = " + str(next_node_2.value) + ";")
									names[my_node.value] = var(FLOAT, my_node.value)
									i += 2
								elif t == BOOL:
									output.append("bool " + my_node.value + " = " + str(next_node_2.value) + ";")
									names[my_node.value] = var(BOOL, my_node.value)
									i += 2
						else:
							if t == FUNCTION:
								if my_node.value == "main":
									output.append("int main() {\n" + compile(next_node_2.value, names = copy.deepcopy(names)) + "\nreturn 0;\n}")
									names[my_node.value] = var(FUNCTION, my_node.value)
								else:
									output.append("void " + my_node.value + "() {\n" + compile(next_node_2.value, names = copy.deepcopy(names)) + "\n}")
									names[my_node.value] = var(FUNCTION, my_node.value)
								i += 2
							elif t == NUMBER:
								output.append("int " + my_node.value + " = " + str(next_node_2.value) + ";")
								names[my_node.value] = var(NUMBER, my_node.value)
								i += 2
							elif t == FLOAT:
								output.append("float " + my_node.value + " = " + str(next_node_2.value) + "f;")
								names[my_node.value] = var(FLOAT, my_node.value)
								i += 2
							elif t == BOOL:
								output.append("bool " + my_node.value + " = " + str(next_node_2.value) + ";")
								names[my_node.value] = var(BOOL, my_node.value)
								i += 2
			elif next_node and next_node.type == ARRAY:
				if my_node.value == "print":
					output.append("std::cout << " + compile_array(next_node.value, names = copy.deepcopy(names), char= " << ") + " << std::endl;")
				elif my_node.value == "read":
					output.append("std::cin >> " + compile_array(next_node.value, names = copy.deepcopy(names), char= " >> ") + ";")
				else:
					func = None
					if next_node_2 and next_node_2.type == FUNCTION:
						func = "{\n" + compile(next_node_2.value, names = copy.deepcopy(names)) + "\n}"

					params = compile_array(next_node.value, names = copy.deepcopy(names))

					if func:
						output.append(my_node.value + "(" + params + ") " + func)
					else:
						output.append(my_node.value + "(" + params + ");")

		i += 1

	return char.join(output)

def compile_array(data, names = {}, char = ", "):
	output = []

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

		i += 1

	return char.join(output)
