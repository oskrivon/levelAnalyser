package main

import (
	"fmt"
	"io/ioutil"
	"os/exec"
	"strings"
)

func f(q, side string) {
	pred := "python trader.py"

	var command string
	command = pred + " " + q + " " + side
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

	i := 0
	for _, q := range quotes {
		var command string
		command = pref + " " + q

		cmd := exec.Command("cmd.exe", "/C", command)

		stdoutStderr, err := cmd.CombinedOutput()

		if err != nil {
			fmt.Println(err)
		}

		s := string(stdoutStderr)
		//fmt.Println(s)
		sss := strings.Split(s, " ")
		if len(sss) > 1 {
			mark := strings.TrimRight(sss[1], "\r\n")

			//fmt.Println(mark)
			//fmt.Printf("%s\n", sss)
			l := "long"
			s := "short"

			if mark == l {
				fmt.Println(q, ":", l)
				go f(q, mark)
			}

			if mark == s {
				fmt.Println(q, ":", s)
				go f(q, mark)
			}

			i++
		} else {
			fmt.Println(q, ": no levels")
		}

		if i >= 30 {
			break
		}
	}

	/* 	for _, file := range fffS {
		quotation := strings.Split(file, ".")[0]
		go f(quotation)
	} */

	var input string
	fmt.Scanln(&input)
}
