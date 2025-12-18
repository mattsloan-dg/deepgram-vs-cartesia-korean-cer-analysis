def normalize_true_transcript():
    """
    Read the true Korean transcript, remove punctuation and line breaks,
    and return the normalized text.
    """
    import string
    
    # Read the file
    with open('./true_transcript/master_korean_transcript.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Remove line breaks
    text = text.replace('\n', '').replace('\r', '')
    
    # Remove punctuation (both English and common Korean punctuation)
    punctuation = string.punctuation + '。，、；：？！''""（）《》【】'
    for char in punctuation:
        text = text.replace(char, '')
    
    return text

def get_deepgram_transcript():
    pass

def get_cartesia_transcript():
    pass

def check_spaces():
    pass

def compare_chars():
    pass

def calculate_cer():
    pass

def main():
    source_of_truth = normalize_true_transcript()
    print(source_of_truth)
    get_deepgram_transcript()
    get_cartesia_transcript()
    check_spaces()
    compare_chars()
    calculate_cer()

if __name__ == "__main__":
    main()
