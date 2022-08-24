package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"math"
	"net/http"
	"os/exec"
	"strconv"
	"strings"
)

func trader(quotation string, volumeFlag, imageFlag bool) {
	pred := "python trader.py"

	var command string
	command = pred + " " + quotation + " " +
		strconv.FormatBool(volumeFlag) + " " +
		strconv.FormatBool(imageFlag)
	cmd := exec.Command("cmd.exe", "/C", command)

	stdoutStderr, err := cmd.CombinedOutput()

	if err != nil {
		fmt.Println(err)
	}

	fmt.Printf("%s\n", stdoutStderr)
}

func filesListReturn(path string) []string {
	files, err := ioutil.ReadDir(path)
	if err != nil {
		fmt.Println(err)
	}

	var quotes []string
	for _, file := range files {
		quotes = append(quotes, strings.Split(file.Name(), ".")[0])
	}

	return quotes
}

func levelAnalysis(quotation string, volumeFlag, imageFlag bool) (resistLevel, suppotrLevel float64) {
	var (
		command string
	)

	pref := "python analyzer.py"

	command = pref + " " + quotation + " " +
		strconv.FormatBool(volumeFlag) + " " +
		strconv.FormatBool(imageFlag)

	cmd := exec.Command("cmd.exe", "/C", command)

	stdoutStderr, err := cmd.CombinedOutput()
	if err != nil {
		fmt.Println(err)
	}

	analyzerResponse := strings.TrimRight(string(stdoutStderr), "\r\n")
	s := strings.Split(analyzerResponse, " ")

	fmt.Println(s)

	resistLevel, err = strconv.ParseFloat(s[1], 64)
	if err != nil {
		fmt.Println("error with float-convert resistance level")
	}

	suppotrLevel, err = strconv.ParseFloat(s[2], 64)
	if err != nil {
		fmt.Println("error with float-convert support level")
	}

	return resistLevel, suppotrLevel
}

func bybitRequest(quotation string) (respRaw *http.Response, err error) {
	request := "https://api.bybit.com/v2/public/tickers?symbol=" + quotation
	respRaw, err = http.Get(request)

	return respRaw, err
}

func bybitParcer(respRaw *http.Response) (float64, error) {
	var resp map[string][]interface{}
	json.NewDecoder(respRaw.Body).Decode(&resp)

	resultRaw := resp["result"]

	result, ok := resultRaw[0].(map[string]interface{})
	if !ok {
		fmt.Println("bybitParcer>>> error of bybit request")
	}

	priceInterface := result["last_price"]
	priceStr, ok := priceInterface.(string)
	if !ok {
		fmt.Println("bybitParcer>>> error interface -> string convert")
	}

	return strconv.ParseFloat(priceStr, 64)
}

func priceChecker(quotation string, th, resistanceLevel, supportLevel float64) {
	longSide := "long"
	shortSide := "short"

	for {
		respRaw, err := bybitRequest(quotation)
		if err != nil {
			fmt.Println("priceChecker error >>>", err)
		}

		currentPrice, err := bybitParcer(respRaw)
		if err != nil {
			fmt.Println("priceChecker error >>>", err)
		}

		resistanceDictance := math.Abs(resistanceLevel-currentPrice) / currentPrice * 100
		supportDictance := math.Abs(supportLevel-currentPrice) / currentPrice * 100

		//fmt.Println(quotation, " :", resistanceDictance, supportDictance)

		if resistanceDictance < th {
			fmt.Println(quotation, ":", longSide)
			trader(quotation, false, true)
		}

		if supportDictance < th {
			fmt.Println(quotation, ":", shortSide)
			trader(quotation, false, true)
		}

		if (currentPrice > resistanceLevel) || (currentPrice < supportLevel) {
			resistanceLevel, supportLevel = levelAnalysis(quotation, false, true)
			fmt.Println(quotation, ": ", "levels recalculate")
		}
	}
}

func main() {
	quotes := filesListReturn("market_history")

	//th := 0.05

	for _, q := range quotes[40:50] {
		//resistanceLevel, supportLevel := levelAnalysis(q, false, true)
		go trader(q, false, true)
	}

	var input string
	fmt.Scanln(&input)
}
