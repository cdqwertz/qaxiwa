import utils, copy
from parser import *

class var:
	def __init__(self, t, name, params = {}, output = -1):
		self.name = name
		self.type = t
		self.params = params
		self.output = output

class compiler:
	def get_code(self, data):
		out = "#include <iostream>\n#include <string>\n\n"

		names = {"while" : var(FUNCTION, "while"), "if" : var(FUNCTION, "if"), "return" : var(FUNCTION, "return")}
		out += self.compile(data, names = names)

		return out

	def throw_error(self, name, line, s = ""):
		print("[" + name + " error][line " + str(line) + "] " + s)
		a = input("exit (y/n)? ")
		if a.lower().strip() in ["y", "yes", "yea"]:
			exit()
		else:
			pass

	def compile(self, data, char="\n", names = {}, namespace = ""):
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

			next_node_3 = None
			if i+3 < len(data):
				next_node_3 = data[i+3]

			if my_node.type == NAME:
				if my_node.value.startswith("@"):
					if next_node and next_node.type == STR:
						if my_node.value == "@cpp":
							output.append(next_node.value)
						elif my_node.value == "@load":
							output.append("#include \"" + next_node.value + "\"")
						elif my_node.value == "@import":
							output.append("#include <" + next_node.value + ">")

						i += 1
				elif next_node and next_node.type == NAME and next_node.value == "=":
					if next_node_2:
						t = next_node_2.type

						#does the name exist?
						if my_node.value in names:
							if t == NAME:
								if next_node_2.value in names:
									if names[next_node_2.value].type == names[my_node.value].type:
										output.append(my_node.value + " = " + str(next_node_2.value.replace("->", "::")) + ";")
										i += 2
									elif next_node_3 and next_node_3.type == ARRAY and names[next_node_2.value].type == FUNCTION:
										print(next_node_2.value)
										out, names, out_t = self.compile_call_function(next_node_2, next_node_3, None, names)
										output.append(my_node.value + " = " + out)
										i += 3
									else:
										self.throw_error("type", my_node.line)
								else:
									self.throw_error("undefined name", next_node_2.line, "\"" + next_node_2.value + "\"")
							else:
								if names[my_node.value].type == t:
									if t == FLOAT:
										output.append(my_node.value + " = " + str(next_node_2.value) + "f;")
									elif t == NUMBER or t == BOOL or t == STR:
										output.append(my_node.value + " = " + str(next_node_2.value) + ";")
									elif t == FUNCTION:
										self.throw_error("override function", my_node.line)
									i += 2
								elif t == CALCULATION:
									out, out_t = self.compile_calculation(next_node_2.value, copy.deepcopy(names))
									output.append(my_node.value + " = " + out + ";")
								else:
									self.throw_error("type", my_node.line)

						else:
							t = next_node_2.type
							if t == NAME:
								if next_node_2.value in names:
									t = names[next_node_2.value].type

									if t == NUMBER or t == BOOL or t == FLOAT or t == STR:
										output.append(self.compile_var(t, my_node.value, str(next_node_2.value), True, True))
										names[namespace + my_node.value] = var(t, namespace + my_node.value)
										i += 2
									elif t == FUNCTION:
										next_node_3 = None
										if i+3 < len(data):
											next_node_3 = data[i+3]
											if next_node_3.type == ARRAY:
												out, names, out_t = self.compile_call_function(next_node_2, next_node_3, None, names, end = "")
												output.append(self.compile_var(out_t, my_node.value, out, True, True))
												names[namespace + my_node.value] = var(out_t, namespace + my_node.value)
												i += 3
								else:
									self.throw_error("undefined name", next_node_2.line, "\"" + next_node_2.value + "\"")

							else:
								if t == FUNCTION:
									if my_node.value == "main":
										output.append("int main() {\n" + self.compile(next_node_2.value, names = copy.deepcopy(names)) + "\nreturn 0;\n}")
										names[namespace + my_node.value] = var(FUNCTION, namespace + my_node.value)
									else:
										output.append("void " + my_node.value + "() {\n" + self.compile(next_node_2.value, names = copy.deepcopy(names)) + "\n}")
										names[namespace + my_node.value] = var(FUNCTION, namespace + my_node.value)
									i += 2
								elif t == NUMBER or t == FLOAT or t == BOOL or t == STR:
									output.append(self.compile_var(t, my_node.value, str(next_node_2.value), True))
									names[namespace + my_node.value] = var(t, namespace + my_node.value)
									i += 2
								elif t == CALCULATION:
									out, out_t = self.compile_calculation(next_node_2.value, copy.deepcopy(names))
									names[namespace + my_node.value] = var(out_t, namespace + my_node.value)
									output.append(self.compile_var(out_t, my_node.value, out, True, True))
								elif t == NAMESPACE:
									print(namespace + my_node.value + "->")
									output.append("namespace " + my_node.value + " {\n" + self.compile(next_node_2.value, names = names, namespace = namespace + my_node.value + "->") + "\n}")
									names[namespace + my_node.value] = var(NAMESPACE, namespace + my_node.value)
									i += 2
				elif next_node and next_node.type == ARRAY:
					next_node_4 = None
					if i+4 < len(data):
						next_node_4 = data[i+4]

					next_node_5 = None
					if i+5 < len(data):
						next_node_5 = data[i+5]

					c1 = next_node_2 and next_node_2.type == NAME and next_node_2.value == ":"
					c2 = next_node_3 and next_node_3.type == NAME and self.get_type(next_node_3.value) and self.get_type(next_node_3.value)[1]
					c3 = next_node_4 and next_node_4.type == NAME and next_node_4.value == "="


					if c1 and c2 and c3 and next_node_5 and next_node_5.type == FUNCTION:
						out, params = self.compile_params(next_node.value)

						n = copy.deepcopy(names)
						for j in params.keys():
							n[params[j].name] = params[j]

						output.append(self.get_type(next_node_3.value)[0] + " " + my_node.value + "(" + out + ") {\n" + self.compile(next_node_5.value, names = n) + "\n}")
						names[namespace + my_node.value] = var(FUNCTION, namespace + my_node.value, params, self.get_type(next_node_3.value)[1])
						i += 3

					elif next_node_2 and next_node_2.type == NAME and next_node_2.value == "=" and next_node_3 and next_node_3.type == FUNCTION:
						out, params = self.compile_params(next_node.value)

						n = copy.deepcopy(names)
						for j in params.keys():
							n[params[j].name] = params[j]

						output.append("void " + my_node.value + "(" + out + ") {\n" + self.compile(next_node_3.value, names = n) + "\n}")
						names[namespace + my_node.value] = var(FUNCTION, namespace + my_node.value, params)
						i += 3
					else:
						out, names, out_t = self.compile_call_function(my_node, next_node, next_node_2, names)
						output.append(out)

			i += 1

		return char.join(output)

	def compile_var(self, t, name, value, new = False, is_name = False):
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

	def compile_call_function(self, my_node, next_node, next_node_2, names, end = ";"):
		out = ""
		output_type = -1
		if my_node.value == "print":
			out = "std::cout << " + self.compile_array(next_node.value, names = copy.deepcopy(names), char= " << ") + " << std::endl" + end
		elif my_node.value == "write":
			out = "std::cout << " + self.compile_array(next_node.value, names = copy.deepcopy(names), char= " << ") + end
		elif my_node.value == "read":
			out = "std::cin >> " + self.compile_array(next_node.value, names = copy.deepcopy(names), char= " >> ") + end
		elif my_node.value == "for":
			if len(next_node.value) > 2:
				node_var = next_node.value[0]
				node_from = next_node.value[1]
				node_to = next_node.value[2]

				if node_var.type == NAME and node_from.type == NUMBER and node_to.type == NUMBER:
					if next_node_2 and next_node_2.type == FUNCTION:
						n = copy.deepcopy(names)
						n[node_var.value] = var(NUMBER, node_var.value)
						func = "{\n" + self.compile(next_node_2.value, names = n) + "\n}"
						out = "for(int " + node_var.value + " = " + node_from.value + ";" + node_var.value + " < " + node_to.value + ";" + node_var.value + "++)" + func
				elif node_var.type == NAME and node_from.type == NAME and node_to.type == NAME:
					if next_node_2 and next_node_2.type == FUNCTION:
						if node_from.value in names and names[node_from.value].type == NUMBER:
							if node_to.value in names and names[node_to.value].type == NUMBER:
								n = copy.deepcopy(names)
								n[node_var.value] = var(NUMBER, node_var.value)
								func = "{\n" + self.compile(next_node_2.value, names = n) + "\n}"
								out = "for(int " + node_var.value + " = " + node_from.value + ";" + node_var.value + " < " + node_to.value + ";" + node_var.value + "++)" + func
							else:
								self.throw_error("type", my_node.line, "for(var : name from : number to : number)")
						else:
							self.throw_error("type", my_node.line, "for(var : name from : number to : number)")
				else:
					self.throw_error("type", my_node.line, "for(var : name from : number to : number)")
			else:
				self.throw_error("type", my_node.line, "Not enough arguments")
		else:
			if my_node.value in names:
				if names[my_node.value].type == FUNCTION:
					func = None
					if next_node_2 and next_node_2.type == FUNCTION:
						func = "{\n" + self.compile(next_node_2.value, names = copy.deepcopy(names)) + "\n}"

					n = copy.deepcopy(names)
					params = self.compile_array(next_node.value, names = n)
					output_type = names[my_node.value].output
					print(my_node.value, "", output_type)

					if func:
						out = my_node.value.replace("->", "::") + "(" + params + ") " + func
					else:
						out = my_node.value.replace("->", "::") + "(" + params + ")" + end

				elif names[my_node.value].type == STR:
					out = my_node.value + ".c_str()[" + self.compile_array(next_node.value, names = copy.deepcopy(names), char= "][") + "]" + end
					#TODO
				else:
					self.throw_error("type", my_node.line)
			else:
				self.throw_error("undefined function/name", my_node.line, "\"" + my_node.value + "\"")

		return out, names, output_type

	def compile_calculation(self, data, names = {}, char = " "):
		output = []
		output_type = NUMBER
		i = 0
		while i < len(data):
			my_node = data[i]

			if my_node.type == NAME:
				if my_node.value in ["+", "-", "*", "/", "%", "==", "!=", "<", ">"]:
					output.append(my_node.value)

					if my_node.value in ["==", "!=", "<", ">"]:
						output_type = BOOL
				elif my_node.value == "and":
					output.append("&&")
					output_type = BOOL
				elif my_node.value == "or":
					output.append("||")
					output_type = BOOL
				elif my_node.value in names:
					print("NAME ", my_node.value, " TYPE ", names[my_node.value].type)
					if names[my_node.value].type == FLOAT:
						output_type = FLOAT
						output.append(my_node.value.replace("->", "::"))
					if names[my_node.value].type == NUMBER:
						output.append(my_node.value.replace("->", "::"))
					if names[my_node.value].type == STR:
						output.append(my_node.value.replace("->", "::"))

						if output_type == NUMBER or output_type == FLOAT:
							output_type = STR
				else:
					self.throw_error("undefined name", my_node.line, "\"" + my_node.value + "\"")
			elif my_node.type == CALCULATION:
				out, out_t = self.compile_calculation(my_node.value, names = names)
				output.append("(" + out + ")")

				if out_t == FLOAT:
					output_type = FLOAT
			elif my_node.type == NUMBER:
				output.append(my_node.value)
			elif my_node.type == STR:
				output.append("\"" + my_node.value + "\"")

				if output_type == NUMBER or output_type == FLOAT:
					output_type = STR
			elif my_node.type == FLOAT:
				output.append(my_node.value + "f")
				output_type = FLOAT

			i += 1

		return char.join(output), output_type

	def compile_array(self, data, names = {}, char = ", "):
		output = []

		i = 0
		while i < len(data):
			my_node = data[i]

			next_node = None
			if i+1 < len(data):
				next_node = data[i+1]

			if my_node.type == NAME:
				if my_node.value in names:
					if next_node and next_node.type == ARRAY:
						out, names, out_t = self.compile_call_function(my_node, next_node, None, names, end = "")
						output.append(out)
						i += 1
					else:
						output.append(my_node.value.replace("->", "::"))
				else:
					self.throw_error("undefined name", my_node.line, "\"" + my_node.value + "\"")
			elif my_node.type == NUMBER:
				output.append(my_node.value)
			elif my_node.type == BOOL:
				output.append(my_node.value)
			elif my_node.type == STR:
				output.append("\"" + my_node.value + "\"")
			elif my_node.type == CALCULATION:
				out, out_t = self.compile_calculation(my_node.value, names = names)
				output.append(out)

			i += 1

		return char.join(output)

	def compile_params(self, data):
		out = []
		params = {}

		i = 0
		while i < len(data):
			my_node = data[i]

			next_node = None
			if i+1 < len(data):
				next_node = data[i+1]

			next_node_2 = None
			if i+2 < len(data):
				next_node_2 = data[i+2]

			if next_node and next_node_2:
				if my_node.type == NAME and next_node.type == NAME and next_node.value == ":" and next_node_2.type == NAME:
					types = {"number" : "int", "str" : "std::string", "bool" : "bool", "float" : "float", "int" : "int"}
					types_2 = {"number" : NUMBER, "str" : STR, "bool" : BOOL, "float" : FLOAT, "int" : NUMBER}
					if next_node_2.value in types.keys():
						t = types[next_node_2.value]
						out.append(t + " " + my_node.value)
						params[my_node.value] = var(types_2[next_node_2.value], my_node.value)
					else:
						self.throw_error("unknown type", my_node.line, "\"" + next_node_2.value + "\"")
			i += 1

		return ", ".join(out), params

	def get_type(self, name):
		types = {"number" : "int", "str" : "std::string", "bool" : "bool", "float" : "float", "int" : "int"}
		types_2 = {"number" : NUMBER, "str" : STR, "bool" : BOOL, "float" : FLOAT, "int" : NUMBER}
		if name in types.keys():
			return types[name], types_2[name]
