import os
import requests
from dotenv import load_dotenv
import string
import json
from levenshtein_calc import levenshtein_with_operations
    
load_dotenv()

def read_text_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()
    
def open_audio_file(filename):
    with open(filename, 'rb') as audio_file:
        return audio_file.read()
    
def write_file(filename, text):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(text)

def normalize_true_transcript():
    import string
    
    text = read_text_file('./true_transcript/master_korean_transcript.txt')
    
    # Remove line breaks
    text = text.replace('\n', '').replace('\r', '')
    
    # Remove punctuation (both English and common Korean punctuation)
    punctuation = string.punctuation + '。，、；：？！''""（）《》【】'
    for char in punctuation:
        text = text.replace(char, '')
    
    return text

def normalize_api_transcript(words_object):
    # In the API responses, the full and complete `transcript` field might not have proper spacing.
    # Instead let's concatenate the individual words, which is mmore reliable.
    concatenated_text = ' '.join([word['word'].strip() for word in words_object])
    transcript = concatenated_text.replace('\n', '').replace('\r', '')
    
    # Normalize transcript (remove punctuation and line breaks)
    punctuation = string.punctuation + '。，、；：？！''""（）《》【】'
    for char in punctuation:
        transcript = transcript.replace(char, '')
    return transcript

def get_deepgram_transcript():
    deepgram_api_key = os.getenv('DEEPGRAM_API_KEY')
    if not deepgram_api_key:
        raise ValueError("DEEPGRAM_API_KEY not found in .env file")
    
    audio_data = open_audio_file('./audio/master_korean_audio.wav')
    
    url = 'https://api.deepgram.com/v1/listen?model=nova-3&language=ko&smart_format=false'
    headers = {
        'Authorization': f'Token {deepgram_api_key}',
        'Content-Type': 'audio/wav'
    }
    
    print("Calling Deepgram API...")
    response = requests.post(url, headers=headers, data=audio_data)
    response.raise_for_status()
    result = response.json()
    words_object = result['results']['channels'][0]['alternatives'][0]['words']
    transcript = normalize_api_transcript(words_object)

    output_filename = './deepgram_transcript/deepgram.txt'
    write_file(output_filename, transcript)
    print(f"Deepgram transcript retrieved and saved to {output_filename}")
    return transcript

def get_cartesia_transcript():
    cartesia_api_key = os.getenv('CARTESIA_API_KEY')
    if not cartesia_api_key:
        raise ValueError("CARTESIA_API_KEY not found in .env file")

    url = "https://api.cartesia.ai/stt"

    files = { "file": ("./audio/master_korean_audio.wav", open("./audio/master_korean_audio.wav", "rb")) }
    payload = {
        "model": "ink-whisper",
        "language": "ko",
        "timestamp_granularities[]": "word"
    }
    headers = {
        "Cartesia-Version": "2025-04-16",
        "Authorization": f"Bearer {cartesia_api_key}"
    }

    print("Calling Cartesia API...")
    response = requests.post(url, data=payload, files=files, headers=headers)
    json_response = response.json()
    words_object = json_response['words']
    transcript = normalize_api_transcript(words_object)
    output_filename = './cartesia_transcript/cartesia.txt'
    write_file(output_filename, transcript)
    print(f"Cartesia transcript retrieved and saved to {output_filename}")
    return transcript

def check_spaces(provider, source_of_truth, comparison_transcript, output_file=None):
    source_no_space = source_of_truth.replace(' ', '')
    comparison_no_space = comparison_transcript.replace(' ', '')
    if source_no_space != comparison_no_space:
        print("WARNING: The non-space characters don't match between files!", file=output_file)
        print(f"Source length (no spaces): {len(source_no_space)}", file=output_file)
        print(f"Deepgram length (no spaces): {len(comparison_no_space)}", file=output_file)
        print("\nProceeding with comparison anyway...\n", file=output_file)

    extra_spaces = 0  # Spaces in deepgram that aren't in source
    missing_spaces = 0  # Spaces in source that aren't in deepgram
    
    source_idx = 0
    comparison_idx = 0
    char_position = 0

    while source_idx < len(source_of_truth) and comparison_idx < len(comparison_transcript):
        source_char = source_of_truth[source_idx]
        comparison_char = comparison_transcript[comparison_idx]
        
        if source_char == ' ' and comparison_char == ' ':
            # Both have space at this position - good
            source_idx += 1
            comparison_idx += 1
        elif source_char == ' ' and comparison_char != ' ':
            # Source has space but comparison transcript doesn't - missing space
            missing_spaces += 1
            source_idx += 1
        elif source_char != ' ' and comparison_char == ' ':
            # Comparison transcript has space but source doesn't - extra space
            extra_spaces += 1
            comparison_idx += 1
        else:
            # Both are non-space characters
            if source_char == comparison_char:
                source_idx += 1
                comparison_idx += 1
                char_position += 1
            else:
                # Characters don't match - alignment issue
                print(f"Character mismatch at position {char_position}:", file=output_file)
                print(f"  Source: '{source_char}' (index {source_idx})", file=output_file)
                print(f"  {provider}: '{comparison_char}' (index {comparison_idx})", file=output_file)
                # Skip to try to realign
                source_idx += 1
                comparison_idx += 1

    # Handle remaining characters
    while source_idx < len(source_of_truth):
        if source_of_truth[source_idx] == ' ':
            missing_spaces += 1
        source_idx += 1
    
    while comparison_idx < len(comparison_transcript):
        if comparison_transcript[comparison_idx] == ' ':
            extra_spaces += 1
        comparison_idx += 1

    return extra_spaces, missing_spaces

def calculate_cer():
    pass

def main():
    source_of_truth = normalize_true_transcript()
    deepgram_transcript = get_deepgram_transcript()
    cartesia_transcript = get_cartesia_transcript()
    
    source_of_truth_no_spaces = source_of_truth.replace(" ", "")
    deepgram_transcript_no_spaces = deepgram_transcript.replace(" ", "")
    cartesia_transcript_no_spaces = cartesia_transcript.replace(" ", "")
    
    deepgram_levenshtein_no_spaces = levenshtein_with_operations(source_of_truth_no_spaces, deepgram_transcript_no_spaces)
    cartesia_levenshtein_no_spaces = levenshtein_with_operations(source_of_truth_no_spaces, cartesia_transcript_no_spaces)
    deepgram_levenshtein_with_spaces = levenshtein_with_operations(source_of_truth, deepgram_transcript_no_spaces)
    cartesia_levenshtein_with_spaces = levenshtein_with_operations(source_of_truth, cartesia_transcript)

    # Replace the last part comparison_transcript with the variable "deepgram_transcript" for producfion.
    deepgram_space_check = check_spaces("deepgram", source_of_truth, comparison_transcript=read_text_file('./deepgram_transcript/deepgram.txt'))
    cartesia_space_check = check_spaces("cartesia", source_of_truth, comparison_transcript=read_text_file('./cartesia_transcript/cartesia.txt'))
    
    
    # write_file("./results/deepgram_spaces.txt", deepgram_space_check)
    calculate_cer()

if __name__ == "__main__":
    main()
