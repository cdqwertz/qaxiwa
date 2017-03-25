var_io = {
	load_file = function(path)
		local content = ""
		local line = ""
		content = content + line + "\n"
		return(content)
	end,

	save_file = function(path, content)

	end,

	write = function(text)
		io.write(text)
	end,

	var_print = function(text)
		print(text)
	end,

	read = function()
		local n = 0
		n = tonumber(io.read())
		return(n)
	end,

	read_float = function()
		local n = 0.0
		n = tonumber(io.read())
		return(n)
	end,

	input = function(text)
		var_io.write(text)
		local s = ""
		s = io.read()
		return(s)
	end
}
