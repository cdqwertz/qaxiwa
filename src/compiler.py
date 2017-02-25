import utils, copy
from parser import *

def throw_error(string):
	print("ERROR: " + string)

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
									output.append(my_node.value + " = " + str(next_node_2.value) + ";")
									i += 2
						else:
							if names[my_node.value].type == t:
								if t == FLOAT:
									output.append(my_node.value + " = " + str(next_node_2.value) + "f;")
								elif t == NUMBER or t == BOOL or t == STR:
									output.append(my_node.value + " = " + str(next_node_2.value) + ";")
								i += 2
							elif t == CALCULATION:
								out, out_t = compile_calculation(next_node_2.value, copy.deepcopy(names))
								output.append(my_node.value + " = " + out + ";")

					else:
						t = next_node_2.type
						if t == NAME:
							if next_node_2.value in names:
								t = names[next_node_2.value].type

								if t == NUMBER or t == BOOL or t == FLOAT or t == STR:
									output.append(compile_var(t, my_node.value, str(next_node_2.value), True, True))
									names[my_node.value] = var(t, my_node.value)
									i += 2
								elif t == FUNCTION:
									next_node_3 = None
									if i+3 < len(data):
										next_node_3 = data[i+3]
										if next_node_3.type == ARRAY:
											pass
											#out, names = compile_call_function(next_node, next_node_2, next_node_3, names)
											#TODO


						else:
							if t == FUNCTION:
								if my_node.value == "main":
									output.append("int main() {\n" + compile(next_node_2.value, names = copy.deepcopy(names)) + "\nreturn 0;\n}")
									names[my_node.value] = var(FUNCTION, my_node.value)
								else:
									output.append("void " + my_node.value + "() {\n" + compile(next_node_2.value, names = copy.deepcopy(names)) + "\n}")
									names[my_node.value] = var(FUNCTION, my_node.value)
								i += 2
							elif t == NUMBER or t == FLOAT or t == BOOL or t == STR:
								output.append(compile_var(t, my_node.value, str(next_node_2.value), True))
								names[my_node.value] = var(t, my_node.value)
								i += 2
							elif t == CALCULATION:
								out, out_t = compile_calculation(next_node_2.value, copy.deepcopy(names))
								names[my_node.value] = var(out_t, my_node.value)
								output.append(compile_var(out_t, my_node.value, out, True, True))
			elif next_node and next_node.type == ARRAY:
				out, names = compile_call_function(my_node, next_node, next_node_2, names)
				output.append(out)

		i += 1

	return char.join(output)

def compile_var(t, name, value, new = False, is_name = False):
	out = ""

	if new:
		if t == NUMBER:
			out = "int " + name + " = " + value
		elif t == FLOAT:
			if is_name:
				out = "float " + name + " = " + value
			else:
				out = "float " + name + " = " + value + "f"
		elif t == BOOL:
			out = "bool " + name + " = " + value
		elif t == STR:
			if is_name:
				out = "std::string " + name + " = " + value
			else:
				out = "std::string " + name + " = \"" + value + "\""
	else:
		if t == NUMBER or t == BOOL:
			out = name + " = " + value
		elif t == FLOAT:
			if is_name:
				out = name + " = " + value
			else:
				out = name + " = " + value + "f"
		elif t == STR:
			if is_name:
				out = name + " = " + value
			else:
				out = name + " = \"" + value + "\""

	return out + ";"

def compile_call_function(my_node, next_node, next_node_2, names):
	out = ""
	if my_node.value == "print":
		out = "std::cout << " + compile_array(next_node.value, names = copy.deepcopy(names), char= " << ") + " << std::endl;"
	elif my_node.value == "read":
		out = "std::cin >> " + compile_array(next_node.value, names = copy.deepcopy(names), char= " >> ") + ";"
	else:
		func = None
		if next_node_2 and next_node_2.type == FUNCTION:
			func = "{\n" + compile(next_node_2.value, names = copy.deepcopy(names)) + "\n}"

		params = compile_array(next_node.value, names = copy.deepcopy(names))

		if func:
			out = my_node.value + "(" + params + ") " + func
		else:
			out = my_node.value + "(" + params + ");"

	return out, names

def compile_calculation(data, names = {}, char = " "):
	output = []
	output_type = NUMBER
	i = 0
	while i < len(data):
		my_node = data[i]

		if my_node.type == NAME:
			if my_node.value in ["+", "-", "*", "/", "%", "==", "!=", "<", ">"]:
				output.append(my_node.value)
			elif my_node.value == "and":
				output.append("&&")
			elif my_node.value == "or":
				output.append("||")
			elif my_node.value in names:
				print("NAME ", my_node.value, " TYPE ", names[my_node.value].type)
				if names[my_node.value].type == FLOAT:
					output_type = FLOAT
					output.append(my_node.value)
				if names[my_node.value].type == NUMBER:
					output.append(my_node.value)
		elif my_node.type == CALCULATION:
			out, out_t = compile_calculation(my_node.value, names = names)
			output.append("(" + out + ")")

			if out_t == FLOAT:
				output_type = FLOAT
		elif my_node.type == NUMBER:
			output.append(my_node.value)
		elif my_node.type == FLOAT:
			output.append(my_node.value + "f")
			output_type = FLOAT

		i += 1

	return char.join(output), output_type

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
		elif my_node.type == BOOL:
			output.append(my_node.value)
		elif my_node.type == STR:
			output.append("\"" + my_node.value + "\"")
		elif my_node.type == CALCULATION:
			out, out_t = compile_calculation(my_node.value, names = names)
			output.append(out)

		i += 1

	return char.join(output)
