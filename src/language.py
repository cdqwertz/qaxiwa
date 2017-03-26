import utils
from parser import *

class language:
	def __init__(self, path):
		self.string = utils.load_file(path)
		self.data = {}

		self.parse()

		self.end = self.data["end"]
		self.array = self.data["array"]

		self.end_namespace = "\n"
		if "end-namespace" in self.data:
			self.end_namespace = self.data["end-namespace"]

		self.operators = self.data["calculations/operators"].split("|")

		x = self.data["calculations/operators-replace"].replace("\\|", "!pipe").split("|")
		self.operators_replace = {}
		for it in range(0, len(x), 2):
			self.operators_replace[x[it]] = x[it+1].replace("!pipe", "|")

		self.keywords = self.data["keywords"].split("|")

	def parse(self):
		lines = self.string.split("\n")

		z = 0
		path = []

		for line in lines:
			if line == "":
				continue

			tabs = 0
			while tabs < len(line) and line[tabs] == '\t':
				tabs += 1

			while tabs < len(path):
				path.pop()

			if line.endswith(":") and not(line.endswith("\\:")):
				z += 1
				path.append(line.strip(" \t:"))
				self.data["/".join(path)] = ""
			else:
				self.data["/".join(path)] = line.strip(" \t").replace("\\n", "\n").replace("\\:", ":").replace("\\e", "").replace("\\s", " ").replace("\\t", "\t")
				#print("/".join(path), "=", self.data["/".join(path)])

	def get_code(self, name, params = {}):
		s = self.data[name]
		for i in params.keys():
			if i == "...":
				s = s.replace("...", params[i])
			else:
				s = s.replace("..." + i + "...", params[i])
		return s

	def get_type(self, t, list_types = []):
		if len(list_types) > 0:
			t = list_types.pop(0)

		if t == NUMBER:
			return self.data["types/number/name"]
		elif t == FLOAT:
			return self.data["types/float/name"]
		elif t == STR:
			return self.data["types/str/name"]
		elif t == BOOL:
			return self.data["types/bool/name"]
		elif t == ARRAY:
			return self.get_code("types/list/name", {"type" : self.get_type(t, list_types = list_types)})

	def get_value(self, t, value):
		a = ""
		if t == NUMBER:
			a = "types/number/"
		elif t == FLOAT:
			a = "types/float/"
		elif t == STR:
			a = "types/str/"
		elif t == BOOL:
			a = "types/bool/"
		elif t == ARRAY:
			a = "types/list/"

		if a + "pattern" in self.data:
			return self.get_code(a + "pattern", {"..." : value})
		else:
			return value

	def get_name(self, name, namespace = ""):
		o = []
		for n in name.split("->"):
			if n in self.keywords:
				o.append("var_" + n)
			else:
				o.append(n)

		name = "->".join(o)

		name = name.replace("->", self.data["scope"])

		return name

	def set_var(self, t, name, value = None, name_2 = None, is_namespace = False, namespace = ""):
		e = self.end

		if value != None:
			return self.get_code("set-var", {"name" : self.get_name(name, namespace = namespace), "value" : self.get_value(t, value)}) + self.end
		else:
			return self.get_code("set-var", {"name" : self.get_name(name, namespace = namespace), "value" : self.get_name(name_2, namespace = namespace)}) + self.end

	def define_var(self, t, name, value = None, name_2 = None, is_namespace = False, namespace = "", list_types = []):
		if is_namespace and "define-var-namespace" in self.data:
			if value != None:
				return self.get_code("define-var-namespace", {"type" : self.get_type(t, list_types), "name" : self.get_name(name), "value" : self.get_value(t, value)}) + self.end
			else:
				return self.get_code("define-var-namespace", {"type" : self.get_type(t, list_types), "name" : self.get_name(name), "value" : self.get_name(name_2, namespace = namespace)}) + self.end
		else:
			if value != None:
				return self.get_code("define-var", {"type" : self.get_type(t, list_types), "name" : self.get_name(name), "value" : self.get_value(t, value)}) + self.end
			else:
				return self.get_code("define-var", {"type" : self.get_type(t, list_types), "name" : self.get_name(name), "value" : self.get_name(name_2, namespace = namespace)}) + self.end

if __name__ == "__main__":
	my_language = language("languages/cpp.txt")
