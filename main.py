import utils

NAME = 0
NUMBER = 1
STR = 2
ARRAY = 3
FUNCTION = 4

class node:
	def __init__(self, t, value):
		self.type = t
		self.value = value

	def __str__(self):
		if type(self.value) == type([]):
			s = []
			for my_node in self.value:
				s.append(str(my_node))
			return str(self.type) + ":[" + ", ".join(s) + "]"
		else:
			return str(self.type) + ":" + str(self.value)

def parse(string):
	data = []
	is_str = False
	my_str = ""
	my_name = ""

	is_number = False
	my_number = ""

	z = 0
	block_type = 0

	for i, token in enumerate(string):
		if z == 0:
			if is_str:
				if token == "\"":
					data.append(node(STR, my_str))
					is_str = False
					my_str = ""
				else:
					my_str += token
			elif is_number:
				my_number += token
				if i+1 < len(string):
					t = string[i+1]
					if t in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
						pass
					else:
						data.append(node(NUMBER, my_number))
						is_number = False
				else:
					data.append(node(NUMBER, my_number))
					is_number = False
			else:
				if token == "\"":
					is_str = True
					my_str = ""
				elif token in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
					my_number = ""
					my_number += token
					if i+1 < len(string):
						t = string[i+1]
						if t in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
							is_number = True
						else:
							data.append(node(NUMBER, my_number))
				elif token == "(":
					if my_name != "":
						data.append(node(NAME, my_name))

					my_name = ""
					block_type = 0
					z += 1
				elif token == "{":
					if my_name != "":
						data.append(node(NAME, my_name))

					my_name = ""
					block_type = 1
					z += 1
				elif token in " \n\t":
					if my_name != "":
						data.append(node(NAME, my_name))
					my_name = ""
				else:
					my_name += token

				if i == len(string)-1:
					if my_name != "":
						data.append(node(NAME, my_name))
		else:
			if block_type == 0:
				if token in ")}":
					z -= 1
					if z == 0:
						data.append(node(ARRAY, parse(my_name)))
						my_name = ""
					else:
						my_name += token
				elif token in "({":
					z += 1
					my_name += token
				else:
					my_name += token

				if i == len(string)-1 and z != 0:
					if my_name != "":
						data.append(node(ARRAY, parse(my_name)))
			elif block_type == 1:
				if token in ")}":
					z -= 1
					if z == 0:
						data.append(node(FUNCTION, parse(my_name)))
						my_name = ""
					else:
						my_name += token
				elif token in "({":
					z += 1
					my_name += token
				else:
					my_name += token

				if i == len(string)-1 and z != 0:
					if my_name != "":
						data.append(node(FUNCTION, parse(my_name)))

	return data

def compile(data, char="\n"):
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
					i += 2
				elif next_node_2 and next_node_2.type == NUMBER:
					output.append("int " + my_node.value + " = " + str(next_node_2.value) + ";")
					i += 2
			elif next_node and next_node.type == ARRAY:
				params, func = compile_array(next_node.value)
				if func != "":
					output.append(my_node.value + "(" + params + ") " + func)
				else:
					output.append(my_node.value + "(" + params + ");")

		i += 1

	return char.join(output)

def compile_array(data):
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
				output.append(my_node.value + "(" + compile(next_node.value) + ")")
			else:
				output.append(my_node.value)
		elif my_node.type == NUMBER:
			output.append(my_node.value)
		elif my_node.type == STR:
			output.append("\"" + my_node.value + "\"")
		elif my_node.type == FUNCTION:
			print("[info]" + str(my_node.value))
			output_2.append("{\n" + compile(my_node.value) + "\n}")

		i += 1

	return ",".join(output), "\n".join(output_2)

if __name__ == "__main__":
	string = utils.load_file("code.txt")
	data = parse(string)

	s = []
	for my_node in data:
		s.append(str(my_node))

	print("[" + ", ".join(s) + "]")
	print()

	out = compile(data)
	print(out)

	utils.save_file("output.cpp", out)
