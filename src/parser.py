import utils

NAME = 0
NUMBER = 1
STR = 2
BOOL = 3
FLOAT = 4
ARRAY = 5
FUNCTION = 6
CALCULATION = 7

class node:
	def __init__(self, t, value, line = -1):
		self.type = t
		self.value = value
		self.line = line

		if self.type == NAME:
			if self.value in ["true", "false"]:
				self.type = BOOL

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
	number_mode = 0
	my_number = ""

	z = 0
	block_type = 0

	line = 1

	for i, token in enumerate(string):
		if z == 0:
			if is_str:
				if token == "\"":
					data.append(node(STR, my_str, line))
					is_str = False
					my_str = ""
				else:
					my_str += token
			elif is_number:
				my_number += token
				if token == ".":
					if number_mode == 0:
						number_mode = 1

				if i+1 < len(string):
					t = string[i+1]
					if t in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "."]:
						pass
					else:
						if number_mode == 0:
							data.append(node(NUMBER, my_number, line))
							is_number = False
							number_mode = 0
						elif number_mode == 1:
							if my_number.endswith("."):
								my_number += "0"
							data.append(node(FLOAT, my_number, line))
							is_number = False
							number_mode = 0
				else:
					if number_mode == 0:
						data.append(node(NUMBER, my_number, line))
					elif number_mode == 1:
						if my_number.endswith("."):
							my_number += "0"
						data.append(node(FLOAT, my_number, line))
					number_mode = 0
					is_number = False
			else:
				if token == "\"":
					is_str = True
					my_str = ""
				elif token in ["-", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "."]:
					my_number = ""
					number_mode = 0
					my_number += token

					if token == ".":
						my_number = "0."
						number_mode = 1

					if i+1 < len(string):
						t = string[i+1]
						if t in ["-", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "."]:
							is_number = True
						else:
							if my_number == "-":
								my_number = "-1"

							if number_mode == 0:
								data.append(node(NUMBER, my_number, line))
							elif number_mode == 1:
								if my_number.endswith("."):
									my_number += "0"
								data.append(node(FLOAT, my_number, line))
							number_mode = 0
					else:
						if my_number == "-":
							my_number = "-1"

						if number_mode == 0:
							data.append(node(NUMBER, my_number, line))
						elif number_mode == 1:
							if my_number.endswith("."):
								my_number += "0"
							data.append(node(FLOAT, my_number, line))
						number_mode = 0

				elif token == "(":
					if my_name != "":
						data.append(node(NAME, my_name, line))

					my_name = ""
					block_type = 0
					z += 1
				elif token == "{":
					if my_name != "":
						data.append(node(NAME, my_name, line))

					my_name = ""
					block_type = 1
					z += 1
				elif token == "[":
					if my_name != "":
						data.append(node(NAME, my_name, line))

					my_name = ""
					block_type = 2
					z += 1
				elif token in " \n\t":
					if my_name != "":
						data.append(node(NAME, my_name, line))
					my_name = ""
				else:
					my_name += token

				if i == len(string)-1:
					if my_name != "":
						data.append(node(NAME, my_name, line))
		else:
			if block_type == 0:
				if token in ")}]":
					z -= 1
					if z == 0:
						data.append(node(ARRAY, parse(my_name), line))
						my_name = ""
					else:
						my_name += token
				elif token in "([{":
					z += 1
					my_name += token
				else:
					my_name += token

				if i == len(string)-1 and z != 0:
					if my_name != "":
						data.append(node(ARRAY, parse(my_name), line))
			elif block_type == 1:
				if token in ")}]":
					z -= 1
					if z == 0:
						data.append(node(FUNCTION, parse(my_name), line))
						my_name = ""
					else:
						my_name += token
				elif token in "[({":
					z += 1
					my_name += token
				else:
					my_name += token

				if i == len(string)-1 and z != 0:
					if my_name != "":
						data.append(node(FUNCTION, parse(my_name), line))
			elif block_type == 2:
				if token in "])}":
					z -= 1
					if z == 0:
						data.append(node(CALCULATION, parse(my_name), line))
						my_name = ""
					else:
						my_name += token
				elif token in "[({":
					z += 1
					my_name += token
				else:
					my_name += token

				if i == len(string)-1 and z != 0:
					if my_name != "":
						data.append(node(CALCULATION, parse(my_name), line))

		if token == "\n":
			line += 1

	return data
