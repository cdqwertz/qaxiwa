# Calculations
```c++
@import "io"

main = {
	a = 2
	b = 1
	c = [a + b]
	io->print(c)
}
```

```c++
@import "io"

main = {
	a = 0
	b = 1
	a = io->read()
	if ([a == b]) {
		io->print("a == b")
	}
}
```
