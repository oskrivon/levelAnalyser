package main

import (
	"fmt"
	"io/ioutil"
	"os/exec"
	"strings"
)

func f(q string) {
	pred := "python cmd_test.py"

	var command string
	command = pred + " " + q
	cmd := exec.Command("cmd.exe", "/C", command)

	stdoutStderr, err := cmd.CombinedOutput()

	if err != nil {
		fmt.Println(err)
	}

	fmt.Printf("%s\n", stdoutStderr)
}

func main() {
	files, err := ioutil.ReadDir("market_history")
	if err != nil {
		fmt.Println(err)
	}

	for _, file := range files {
		quotation := strings.Split(file.Name(), ".")[0]
		go f(quotation)
		//fmt.Println(quotation)
	}

	/* 	for i := 0; i < 5; i++ {
		go f(quot[i])
	} */

	var input string
	fmt.Scanln(&input)
}
