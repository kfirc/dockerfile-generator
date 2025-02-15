package main

import (
    "fmt"
    "os"
)

func countCharacters(text string) int {
    return len(text)
}

func main() {
    if len(os.Args) != 2 {
        fmt.Println("Usage: go run char_counter.go '<input_text>'")
        os.Exit(1)
    }

    input := os.Args[1]
    count := countCharacters(input)
    fmt.Printf("Character Count: %d\n", count)
} 