def count_words(text):
    words = text.strip().split()
    return len(words)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python word_counter.py '<input_text>'")
        sys.exit(1)
    
    input_text = sys.argv[1]
    count = count_words(input_text)
    print(f"Word Count: {count}") 