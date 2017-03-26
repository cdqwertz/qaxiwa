import utils, copy, sys, os, json
from parser import *

class var:
	def __init__(self, t, name, params = {}, output = -1):
		self.name = name
		self.type = t
		self.params = params
		self.output = output

	def get_dict(self):
		if self.type == FUNCTION:
			p = []
			for i in self.params.keys():
				p.append(self.params[i].get_dict())
			d = {"name" : self.name, "type" : self.type, "params" : p, "output" : self.output}
			return d
		else:
			d = {"name" : self.name, "type" : self.type}
			return d

class compiler:
	def __init__(self, language):
		self.language = language

	def get_code(self, data):
		out = self.language.data["file-start"]

		names = {}
		for i in ["if", "while", "for", "return"]:
			if not("functions/built-in/" + i + "/custom-params" in self.language.data):
				names[i] = var(FUNCTION, i)

		out += self.compile(data, names = names)

		out += self.language.data["file-end"]

		names_str = []
		for n in names.keys():
			if not(n in ["if", "while", "for", "return"]):
				names_str.append(json.dumps(names[n].get_dict()))

		utils.save_file("names.txt", "\n".join(names_str))

		return out

	def throw_error(self, name, line, s = ""):
		print("[" + name + " error][line " + str(line) + "] " + s)
		a = input("exit (y/n)? ")
		if a.lower().strip() in ["y", "yes", "yea"]:
			exit()
		else:
			pass

	def indent_text(self, text, indent = 0):
		if indent > 0:
			out = []
			for line in text.split("\n"):
				out.append("\t" + line)

			return "\n".join(out)
		else:
			return text

	def compile(self, data, char="\n", names = {}, namespace = "", is_namespace = False, indent = 0):
		output = []

		if is_namespace and char == "\n":
			char = self.language.end_namespace

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
						if my_node.value == "@" + self.language.get_code("name"):
							output.append(self.indent_text(next_node.value, indent))
						elif my_node.value == "@load":
							output.append(self.language.get_code("import", {"name" : next_node.value}))
						elif my_node.value == "@import":
							#TODO
							l = os.getcwd().split(os.path.sep)
							l.pop()
							l.append("lib")
							l.append(next_node.value)
							l2 = copy.deepcopy(l)
							l3 = copy.deepcopy(l)
							l2.append(next_node.value + self.language.data["file_ending"])
							l3.append("names.txt")
							p1 = os.path.sep.join(l2)
							p2 = os.path.sep.join(l3)
							output.append(self.language.get_code("import", {"name" : p1}))

							for line in utils.load_file(p2).split("\n"):
								obj = json.loads(line)
								params = {}
								print(obj)
								if "params" in obj:
									for it in obj["params"]:
										params[it["name"]] = var(it["type"], it["name"])
									names[obj["name"]] = var(obj["type"], obj["name"], params, obj["output"])
								else:
									names[obj["name"]] = var(obj["type"], obj["name"])

						i += 1
				elif next_node and next_node.type == NAME and next_node.value == "=":
					if next_node_2:
						t = next_node_2.type

						#does the name exist?
						if my_node.value in names:
							if t == NAME:
								if next_node_2.value in names:
									if names[next_node_2.value].type == names[my_node.value].type:
										output.append(self.indent_text(self.language.set_var(t, my_node.value, name_2 = next_node_2.value), indent))
										i += 2
									elif next_node_3 and next_node_3.type == ARRAY and names[next_node_2.value].type == FUNCTION:
										out, names, out_t = self.compile_call_function(next_node_2, next_node_3, None, names, namespace = namespace)
										output.append(self.indent_text(self.language.set_var(t, my_node.value, name_2 = out), indent))
										i += 3
									else:
										self.throw_error("type", my_node.line)
								else:
									self.throw_error("undefined name", next_node_2.line, "\"" + next_node_2.value + "\"")
							else:
								if names[my_node.value].type == t:
									if t == FLOAT or t == NUMBER or t == BOOL or t == STR:
										output.append(self.indent_text(self.language.set_var(t, my_node.value, value = next_node_2.value), indent))
									elif t == FUNCTION:
										self.throw_error("override function", my_node.line)
									i += 2
								elif t == CALCULATION:
									out, out_t = self.compile_calculation(next_node_2.value, copy.deepcopy(names), namespace = namespace)
									output.append(self.indent_text(self.language.set_var(t, my_node.value, name_2 = out), indent))
								else:
									self.throw_error("type", my_node.line)

						else:
							t = next_node_2.type
							if t == NAME:
								if next_node_2.value in names:
									t = names[next_node_2.value].type

									if t == NUMBER or t == BOOL or t == FLOAT or t == STR:
										output.append(self.indent_text(self.compile_var(t, my_node.value, str(next_node_2.value), True, True, is_namespace = is_namespace), indent))
										names[namespace + my_node.value] = var(t, namespace + my_node.value)
										i += 2
									elif t == FUNCTION:
										next_node_3 = None
										if i+3 < len(data):
											next_node_3 = data[i+3]
											if next_node_3.type == ARRAY:
												out, names, out_t = self.compile_call_function(next_node_2, next_node_3, None, names, end = "", namespace = namespace)
												output.append(self.indent_text(self.compile_var(out_t, my_node.value, out, True, True, is_namespace = is_namespace), indent))
												names[namespace + my_node.value] = var(out_t, namespace + my_node.value)
												i += 3
								else:
									self.throw_error("undefined name", next_node_2.line, "\"" + next_node_2.value + "\"")

							else:
								if t == FUNCTION:
									if my_node.value == "main":
										output.append(self.indent_text(self.language.get_code("functions/define/main", {"value" : self.compile(next_node_2.value, names = copy.deepcopy(names), indent = indent + 1)}), indent))
										names[namespace + my_node.value] = var(FUNCTION, namespace + my_node.value)
									else:

										output.append(self.indent_text(self.language.get_code("functions/define/no-params", {"name" : self.language.get_name(my_node.value), "value" : self.compile(next_node_2.value, names = copy.deepcopy(names), indent = indent + 1)}), indent))
										names[namespace + my_node.value] = var(FUNCTION, namespace + my_node.value)
									i += 2
								elif t == NUMBER or t == FLOAT or t == BOOL or t == STR:
									output.append(self.indent_text(self.compile_var(t, my_node.value, str(next_node_2.value), True, is_namespace = is_namespace), indent))
									names[namespace + my_node.value] = var(t, namespace + my_node.value)
									i += 2
								elif t == CALCULATION:
									out, out_t = self.compile_calculation(next_node_2.value, copy.deepcopy(names), namespace = namespace)
									names[namespace + my_node.value] = var(out_t, namespace + my_node.value)
									output.append(self.indent_text(self.compile_var(out_t, my_node.value, out, True, True, namespace = namespace), indent))
								elif t == NAMESPACE:
									output.append(self.indent_text(self.language.get_code("blocks/namespace", {"name" : self.language.get_name(my_node.value), "value" : self.compile(next_node_2.value, names = names, namespace = namespace + my_node.value + "->", is_namespace = True, indent = indent + 1)}), indent))
									names[namespace + my_node.value] = var(NAMESPACE, namespace + my_node.value)
									i += 2
								elif t == ARRAY:
									list_types = self.get_list_types(next_node_2.value)
									list_types = [ARRAY] + list_types
									output.append(self.indent_text(self.compile_var(t, my_node.value, self.compile_array(next_node_2.value, copy.deepcopy(names), namespace = namespace), True, is_namespace = is_namespace, list_types = list_types), indent))
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

						output.append(self.indent_text(self.language.get_code("functions/define/other", {"return" : self.get_type(next_node_3.value)[0],"name" : self.language.get_name(my_node.value), "params" : out, "value" : self.compile(next_node_5.value, names = n, indent = indent + 1)}), indent))
						names[namespace + my_node.value] = var(FUNCTION, namespace + my_node.value, params, self.get_type(next_node_3.value)[1])
						i += 3

					elif next_node_2 and next_node_2.type == NAME and next_node_2.value == "=" and next_node_3 and next_node_3.type == FUNCTION:
						out, params = self.compile_params(next_node.value)

						n = copy.deepcopy(names)
						for j in params.keys():
							n[params[j].name] = params[j]

						output.append(self.indent_text(self.language.get_code("functions/define/no-return-value", {"name" : self.language.get_name(my_node.value), "params" : out, "value" : self.compile(next_node_3.value, names = n, indent = indent + 1)}), indent))
						names[namespace + my_node.value] = var(FUNCTION, namespace + my_node.value, params)
						i += 3
					else:
						out, names, out_t = self.compile_call_function(my_node, next_node, next_node_2, names, indent = indent, namespace = namespace)
						output.append(self.indent_text(out, indent))

			i += 1

		return char.join(output)

	def compile_var(self, t, name, value, new = False, is_name = False, is_namespace = False, namespace = "", list_types = []):
		out = ""

		if new:
			if is_name:
				return self.language.define_var(t, name, name_2 = value, is_namespace = is_namespace, namespace = namespace, list_types = list_types)
			else:
				return self.language.define_var(t, name, value, is_namespace = is_namespace, namespace = namespace, list_types = list_types)
		else:
			if is_name:
				return self.language.set_var(t, name, name_2 = value, namespace = namespace)
			else:
				return self.language.set_var(t, name, value, namespace = namespace)

		return out + ";"

	def compile_call_function(self, my_node, next_node, next_node_2, names, end = "@", indent = 0, namespace = ""):
		#TODO
		if end == "@":
			end = self.language.end

		out = ""
		output_type = -1
		if my_node.value == "for":
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
						func = self.compile(next_node_2.value, names = copy.deepcopy(names), indent = indent + 1)

					n = copy.deepcopy(names)
					params = self.compile_array(next_node.value, names = n, namespace = namespace)
					output_type = names[my_node.value].output
					print(my_node.value, "", output_type)

					path = "functions/call/call"

					if "functions/built-in/" + my_node.value + "/custom" in self.language.data:
						path = "functions/built-in/" + my_node.value + "/custom"

					if func != None:
						out = self.language.get_code(path + "-func", {"name" : self.language.get_name(my_node.value, namespace = namespace), "params" : params, "func" : func})
					else:
						out = self.language.get_code(path, {"name" : self.language.get_name(my_node.value, namespace = namespace), "params" : params}) + end

				elif names[my_node.value].type == STR:
					out = my_node.value + ".c_str()[" + self.compile_array(next_node.value, names = copy.deepcopy(names), char= "][", namespace = namespace) + "]" + end
					#TODO
				elif names[my_node.value].type == ARRAY:
					pass
					#TODO
				else:
					self.throw_error("type", my_node.line)
			else:
				self.throw_error("undefined function/name", my_node.line, "\"" + my_node.value + "\"")

		return out, names, output_type

	def compile_calculation(self, data, names = {}, char = " ", namespace = ""):
		output = []
		output_type = NUMBER
		i = 0
		while i < len(data):
			my_node = data[i]

			if my_node.type == NAME:
				#TODO
				if my_node.value in self.language.operators:
					output.append(my_node.value)

					if my_node.value in ["==", "!=", "<", ">", "and", "or"]:
						output_type = BOOL
				elif my_node.value in self.language.operators_replace.keys():
					output.append(self.language.operators_replace[my_node.value])

					if my_node.value in ["==", "!=", "<", ">", "and", "or"]:
						output_type = BOOL
				elif my_node.value in names:
					print("NAME ", my_node.value, " TYPE ", names[my_node.value].type)
					if names[my_node.value].type == FLOAT:
						output_type = FLOAT
						output.append(self.language.get_name(my_node.value, namespace = namespace))
					if names[my_node.value].type == NUMBER:
						output.append(self.language.get_name(my_node.value, namespace = namespace))
					if names[my_node.value].type == STR:
						output.append(self.language.get_name(my_node.value, namespace = namespace))

						if output_type == NUMBER or output_type == FLOAT:
							output_type = STR
				else:
					self.throw_error("undefined name", my_node.line, "\"" + my_node.value + "\"")
			elif my_node.type == CALCULATION:
				out, out_t = self.compile_calculation(my_node.value, names = names, namespace = namespace)
				output.append(self.language.get_code("blocks/calculation", {"..." : out}))

				if out_t == FLOAT:
					output_type = FLOAT
			elif my_node.type == NUMBER:
				output.append(self.language.get_value(my_node.type, my_node.value))
			elif my_node.type == STR:
				output.append(self.language.get_value(my_node.type, my_node.value))

				if output_type == NUMBER or output_type == FLOAT:
					output_type = STR
			elif my_node.type == FLOAT:
				output.append(self.language.get_value(my_node.type, my_node.value))
				output_type = FLOAT

			i += 1

		return char.join(output), output_type

	def compile_array(self, data, names = {}, char = "@", namespace = ""):
		if char == "@":
			char = self.language.array
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
						out, names, out_t = self.compile_call_function(my_node, next_node, None, names, end = "", namespace = namespace)
						output.append(out)
						i += 1
					else:
						output.append(self.language.get_name(my_node.value, namespace = namespace))
				else:
					self.throw_error("undefined name", my_node.line, "\"" + my_node.value + "\"")
			elif my_node.type == NUMBER or my_node.type == BOOL or my_node.type == STR:
				output.append(self.language.get_value(my_node.type, my_node.value))
			elif my_node.type == CALCULATION:
				out, out_t = self.compile_calculation(my_node.value, names = names, namespace = namespace)
				output.append(out)
			elif my_node.type == ARRAY:
				output.append(self.language.get_code("types/list/pattern", {"..." : self.compile_array(my_node.value, names, namespace = namespace)}))
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
					t, t2, t3 = self.get_type(next_node_2.value)
					if t:
						out.append(self.language.get_code("parameter", {"type" : t, "value" : my_node.value}))
						params[my_node.value] = var(t2, my_node.value)
					else:
						self.throw_error("unknown type", my_node.line, "\"" + next_node_2.value + "\"")
			i += 1

		return ", ".join(out), params

	def get_type(self, name):
		t = name.split("->")
		if t[0] == "list":
			t.pop(0)
			t, t2, t3 = self.get_type("->".join(t))
			return self.language.get_type(ARRAY, list_types = [ARRAY] + t3), ARRAY, [ARRAY] + t3
		else:
			#types = {"number" : "int", "str" : "std::string", "bool" : "bool", "float" : "float", "int" : "int", "list" : "list"}
			types = {"number" : NUMBER, "str" : STR, "bool" : BOOL, "float" : FLOAT, "int" : NUMBER, "list" : ARRAY}
			if name in types.keys():
				return self.language.get_type(types[name]), types[name], [types[name]]

	def get_list_types(self, v):
		if len(v) > 0:
			item = v[0]

			#TODO: d = (((1)) (("Hello")))
			for i in v:
				if i.type != item.type:
					self.throw_error("type error", i.line)

			if item.type == ARRAY:
				list_types = [ARRAY]
				list_types = list_types + self.get_list_types(item.value)
				return list_types
			else:
				return [item.type]
