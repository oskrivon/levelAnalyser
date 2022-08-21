package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os/exec"
	"strconv"
	"strings"
)

func trader(q, side string) {
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

func analysisProcess() {
	pref := "python analyzer.py"

	files, err := ioutil.ReadDir("market_history")
	if err != nil {
		fmt.Println(err)
	}

	var quotes []string
	for _, file := range files {
		quotes = append(quotes, strings.Split(file.Name(), ".")[0])
	}

	i := 0
	for _, q := range quotes {
		var command string
		command = pref + " " + q

		cmd := exec.Command("cmd.exe", "/C", command)

		stdoutStderr, err := cmd.CombinedOutput()

		if err != nil {
			fmt.Println(err)
		}

		analyzerResponse := string(stdoutStderr)
		s := strings.Split(analyzerResponse, " ")
		if len(s) > 1 {
			mark := strings.TrimRight(s[1], "\r\n")
			l := "long"
			s := "short"

			if mark == l {
				fmt.Println(q, ":", l)
				go trader(q, mark)
			}

			if mark == s {
				fmt.Println(q, ":", s)
				go trader(q, mark)
			}

			i++
		} else {
			fmt.Println(q, ": no levels")
		}

		if i >= 30 {
			break
		}
	}
}

func bybitRequest(quotation string) {
	request := "https://api.bybit.com/v2/public/tickers?symbol=" + quotation
	for {
		respRaw, err := http.Get(request)
		if err != nil {
			fmt.Println(err)
		}

		var resp map[string][]interface{}
		json.NewDecoder(respRaw.Body).Decode(&resp)

		resultRaw := resp["result"]

		result, ok := resultRaw[0].(map[string]interface{})
		if !ok {
			fmt.Println(quotation, "error of bybit request")
		}

		priceInterface := result["last_price"]
		priceStr, ok := priceInterface.(string)
		if !ok {
			fmt.Println(quotation, "error interface -> string convert")
		}

		price, err := strconv.ParseFloat(priceStr, 64)

		fmt.Println(quotation, price)
	}
}

func main() {
	//analysisProcess()

	x := [6]string{"BTCUSDT", "1INCHUSDT", "BITUSDT", "CTKUSDT", "IOTXUSDT", "STXUSDT"}
	//y := [1]string{"BTCUSDT"}
	for _, q := range x {
		go bybitRequest(q)
	}

	var input string
	fmt.Scanln(&input)
}
