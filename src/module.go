package main

import "syscall/js"

func main() {
	c := make(chan struct{}, 0)
	js.Global().Set("svca", js.FuncOf(func(this js.Value, args []js.Value) interface{} {
		return "SVCA deterministic module OK"
	}))
	<-c
}
