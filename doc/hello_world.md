# Hello World
Every program you write in qaxiwa has a main function. This function will be called when you start the program. It looks like this:
```c++
main = {
}
```
### Import the io library
To print text to the console, you can the `io` library. You can find it in `<qaxiwa>/lib/io.qaxiwa`. To import the library, you should add the following line to the beginnig of your code.

```c++
@import "io"
```
### Print
If you want to output text in qaxiwa, you can use ```io->print("Text")```. Let's use ```io->print``` to output the text "Hello World".

```c++
@import "io"

main = {
	io->print("Hello World")
}
```

Output:
```
Hello World
```
