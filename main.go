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
	pref := "python analyzer.py"

	files, err := ioutil.ReadDir("market_history")
	if err != nil {
		fmt.Println(err)
	}

	var quotes []string

	for _, file := range files {
		quotes = append(quotes, strings.Split(file.Name(), ".")[0])
	}

	//quotesSome := quotes[:3]

	//fmt.Println(quotesSome)

	for _, q := range quotes {
		var command string
		command = pref + " " + q

		cmd := exec.Command("cmd.exe", "/C", command)

		stdoutStderr, err := cmd.CombinedOutput()

		if err != nil {
			fmt.Println(err)
		}

		s := string(stdoutStderr)
		sss := strings.Split(s, " ")[1]

		fmt.Println(q, sss)
		//fmt.Printf("%s\n", sss)
	}

	/* 	for _, file := range fffS {
		quotation := strings.Split(file, ".")[0]
		go f(quotation)
	} */

	var input string
	fmt.Scanln(&input)
}
