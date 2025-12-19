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

def check_spaces(source_of_truth, comparison_transcript):
    extra_spaces = 0
    missing_spaces = 0
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

def calculate_cer(insertions, deletions, substitutions, reference_length):
    """
    Calculate Character Error Rate (CER)
    
    CER = (I + D + S) / N
    where:
        I = insertions
        D = deletions
        S = substitutions
        N = total characters in reference
    """
    total_errors = insertions + deletions + substitutions
    cer = total_errors / reference_length if reference_length > 0 else 0
    return cer, total_errors

def print_cer_analysis(provider, 
                       ins_no_space, 
                       del_no_space,
                       sub_no_space, 
                       total_errors_no_space,
                       cer_no_space,
                       ins_with_space,
                       del_with_space,
                       sub_with_space,
                       total_errors_with_space,
                       cer_with_space
                       ):
    with open(f'./results/{provider}_cer_result.txt', 'w', encoding='utf-8') as output_file:
        print("=" * 80, file=output_file)
        print("Character Error Rate (CER) Calculator", file=output_file)
        print("=" * 80, file=output_file)
        print(file=output_file)

        # ======================================================================
        # Option 1: CER WITHOUT SPACES (character-level accuracy only)
        # ======================================================================
        print("=" * 80, file=output_file)
        print("OPTION 1: CER WITHOUT SPACES", file=output_file)
        print("(Focuses on character accuracy, ignoring spacing differences)", file=output_file)
        print("=" * 80, file=output_file)
        print(file=output_file)

        print(f"Insertions:     {ins_no_space}", file=output_file)
        print(f"Deletions:      {del_no_space}", file=output_file)
        print(f"Substitutions:  {sub_no_space}", file=output_file)
        print(f"Total Errors:   {total_errors_no_space}", file=output_file)
        print(file=output_file)
        print(f"CER (without spaces): {cer_no_space:.4f} ({cer_no_space * 100:.2f}%)", file=output_file)
        print(f"Character Accuracy:   {(1 - cer_no_space):.4f} ({(1 - cer_no_space) * 100:.2f}%)", file=output_file)
        print(file=output_file)

        # ======================================================================
        # Option 2: CER WITH SPACES (includes spacing errors)
        # ======================================================================
        print("=" * 80, file=output_file)
        print("OPTION 2: CER WITH SPACES", file=output_file)
        print("(Includes both character errors and spacing errors)", file=output_file)
        print("=" * 80, file=output_file)
        print(file=output_file)

        print(f"Insertions:     {ins_with_space}", file=output_file)
        print(f"Deletions:      {del_with_space}", file=output_file)
        print(f"Substitutions:  {sub_with_space}", file=output_file)
        print(f"Total Errors:   {total_errors_with_space}", file=output_file)
        print(file=output_file)
        print(f"CER (with spaces): {cer_with_space:.4f} ({cer_with_space * 100:.2f}%)", file=output_file)
        print(f"Character Accuracy: {(1 - cer_with_space):.4f} ({(1 - cer_with_space) * 100:.2f}%)", file=output_file)
        print(file=output_file)

         # ======================================================================
        # Summary and Recommendation
        # ======================================================================
        print("=" * 80, file=output_file)
        print("SUMMARY", file=output_file)
        print("=" * 80, file=output_file)
        print(file=output_file)
        print("1. CER WITHOUT SPACES (Character-only):", file=output_file)
        print(f"   - CER: {cer_no_space * 100:.2f}%", file=output_file)
        print(file=output_file)
        print("2. CER WITH SPACES (Complete):", file=output_file)
        print(f"   - CER: {cer_with_space * 100:.2f}%", file=output_file)
        print(file=output_file)

    print(f"Results written to {provider}_cer_result.txt")

def print_space_analysis(provider, extra_spaces, missing_spaces):
    with open(f'./results/{provider}_check_spaces_result.txt', 'w', encoding='utf-8') as output_file:
        print("=" * 60, file=output_file)
        print("Space Comparison Tool", file=output_file)
        print("=" * 60, file=output_file)
        print(file=output_file)

        print("=" * 60, file=output_file)
        print("RESULTS", file=output_file)
        print("=" * 60, file=output_file)
        print(file=output_file)
        print(f"Extra spaces in {provider}.txt (not in source): {extra_spaces}", file=output_file)
        print(f"  → These are spaces that {provider} added that shouldn't be there", file=output_file)
        print(file=output_file)
        print(f"Missing spaces in {provider}.txt (present in source): {missing_spaces}", file=output_file)
        print(f"  → These are spaces that should be in {provider} but aren't", file=output_file)
        print(file=output_file)
        print("=" * 60, file=output_file)

    print(f"Results written to {provider}_check_spaces_result.txt")


def main():
    source_of_truth = normalize_true_transcript()
    deepgram_transcript = get_deepgram_transcript()
    cartesia_transcript = get_cartesia_transcript()
    
    source_of_truth_no_spaces = source_of_truth.replace(" ", "")
    deepgram_transcript_no_spaces = deepgram_transcript.replace(" ", "")
    cartesia_transcript_no_spaces = cartesia_transcript.replace(" ", "")
    
    _, ins_dg_nosp, del_dg_nosp, sub_dg_nosp = levenshtein_with_operations(
        source_of_truth_no_spaces, 
        deepgram_transcript_no_spaces
        )
    _, ins_cart_nosp, del_cart_nosp, sub_cart_nosp = levenshtein_with_operations(
        source_of_truth_no_spaces, 
        cartesia_transcript_no_spaces
        )
    _, ins_dg_withsp, del_dg_withsp, sub_dg_withsp = levenshtein_with_operations(
        source_of_truth, 
        deepgram_transcript_no_spaces
        )
    _, ins_cart_withsp, del_cart_withsp, sub_cart_withsp  = levenshtein_with_operations(
        source_of_truth, 
        cartesia_transcript
        )
    
    cer_dg_nosp, total_errors_dg_nosp = calculate_cer(ins_dg_nosp, del_dg_nosp, sub_dg_nosp, len(source_of_truth_no_spaces))
    cer_cart_nosp, total_errors_cart_nosp = calculate_cer(ins_cart_nosp, del_cart_nosp, sub_cart_nosp, len(source_of_truth))
    cer_dg_withsp, total_errors_dg_withsp = calculate_cer(ins_dg_withsp, del_dg_withsp, sub_dg_withsp, len(source_of_truth))
    cer_cart_withsp, total_errors_cart_withsp = calculate_cer(ins_cart_withsp, del_cart_withsp, sub_cart_withsp, len(source_of_truth))

    print_cer_analysis("deepgram", ins_dg_nosp, del_dg_nosp, sub_dg_nosp, total_errors_dg_nosp, cer_dg_nosp, ins_dg_withsp, del_dg_withsp, sub_dg_withsp, total_errors_dg_withsp, cer_dg_withsp)
    print_cer_analysis("cartesia", ins_cart_nosp, del_cart_nosp, sub_cart_nosp, total_errors_cart_nosp, cer_cart_nosp, ins_cart_withsp, del_cart_withsp, sub_cart_withsp, total_errors_cart_withsp, cer_cart_withsp)

    # Replace the last part comparison_transcript with the variable "deepgram_transcript" for producfion.
    dg_extra_spaces, dg_missing_spaces = check_spaces(source_of_truth, deepgram_transcript)
    cart_extra_spaces, cart_missing_spaces = check_spaces(source_of_truth, cartesia_transcript)
    
    print_space_analysis("deepgram", dg_extra_spaces, dg_missing_spaces)
    print_space_analysis("cartesia", cart_extra_spaces, cart_missing_spaces)
    
    # write_file("./results/deepgram_spaces.txt", deepgram_space_check)
    # calculate_cer()

if __name__ == "__main__":
    main()
