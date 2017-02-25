def load_file(path):
	f = open(path, "r")
	c = f.read()
	f.close()
	return c

def save_file(path, string):
	f = open(path, "w")
	f.write(string)
	f.close()
