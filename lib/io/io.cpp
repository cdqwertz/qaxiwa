#include <iostream>
#include <string>

#include <fstream>
namespace io {
	std::string load_file(std::string path) {
		std::string content = "";
		std::string line = "";
		std::ifstream my_file;
		my_file.open(path.c_str());
		if(my_file.is_open()) {
		while(std::getline(my_file, line)) {
		content = content + line + "\n";
		}
		my_file.close();
		}
		return(content);
	}
	void save_file(std::string path, std::string content) {
		std::ofstream my_file;
		my_file.open(path.c_str());
		if(my_file.is_open()) {
		my_file << content;
		my_file.close();
		}
	}
	void write(std::string text) {
		std::cout << text;
	}
	void print(std::string text) {
		std::cout << text << std::endl;
	}
	int read() {
		int n = 0;
		std::cin >> n;
		return(n);
	}
	float read_float() {
		float n = 0.0f;
		std::cin >> n;
		return(n);
	}
	std::string input(std::string text) {
		write(text);
		std::string s = "";
		std::getline(std::cin, s);
		return(s);
	}
}