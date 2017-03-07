import utils

class language:
	def __init__(self, path):
		self.string = utils.load_file(path)
		self.data = {}

		self.parse()

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

			if line.endswith(":"):
				z += 1
				path.append(line.strip(" \t:"))
				self.data["/".join(path)] = ""
			else:
				self.data["/".join(path)] = line.strip(" \t").replace("\\n", "\n")
				print("/".join(path), "=", self.data["/".join(path)])

	def get(self, name, params = {}):
		s = self.data[name]
		for i in params.keys():
			if i == "...":
				s = s.replace("...", params[i])
			else:
				s = s.replace("..." + i + "...", params[i])
		return s

if __name__ == "__main__":
	my_language = language("languages/cpp.txt")
