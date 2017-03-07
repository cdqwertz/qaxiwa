import utils
from parser import *
from compiler import *
from language import *

if __name__ == "__main__":
	string = utils.load_file("code.txt")
	data = parse(string)

	s = []
	for my_node in data:
		s.append(str(my_node))

	print("[" + ", ".join(s) + "]")
	print()

	my_language = language("languages/cpp.txt")
	my_compiler = compiler(my_language)
	out = my_compiler.get_code(data)
	print(out)

	utils.save_file("output.cpp", out)
