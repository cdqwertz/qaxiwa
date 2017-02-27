import utils
from parser import *
from compiler import *

if __name__ == "__main__":
	string = utils.load_file("code.txt")
	data = parse(string)

	s = []
	for my_node in data:
		s.append(str(my_node))

	print("[" + ", ".join(s) + "]")
	print()

	names = {"while" : var(FUNCTION, "while"), "if" : var(FUNCTION, "if"), "return" : var(FUNCTION, "return")}

	out = compile(data, names = names)
	out = "#include <iostream>\n#include <string>\n\n" + out
	print(out)

	utils.save_file("output.cpp", out)
