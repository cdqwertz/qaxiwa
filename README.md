# Qaxiwa
This is a small programming language I make for fun.
*WIP*

### License
See LICENSE.txt

### Examples
Hello World:
```c++
@import "io"

main = {
	io->print("Hello World")
}
```

Add 2 numbers:
```c++
@import "io"

main = {
	a = io->read()
	b = io->read()
	c = [a + b]
	io->print([" " + c])
}
```
