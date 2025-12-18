import os
import requests
from dotenv import load_dotenv
import string
import json
    
load_dotenv()

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
    
    with open('./audio/master_korean_audio.wav', 'rb') as audio_file:
        audio_data = audio_file.read()
    
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
    
    with open('./deepgram_transcript/deepgram.txt', 'w', encoding='utf-8') as f:
        f.write(transcript)
    
    print("Deepgram transcript retrieved and saved to ./deepgram_transcript/deepgram.txt")
    return

def get_cartesia_transcript():
    cartesia_api_key = os.getenv('CARTESIA_API_KEY')

    if not cartesia_api_key:
        raise ValueError("DEEPGRAM_API_KEY not found in .env file")

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
    
    with open('./cartesia_transcript/cartesia.txt', 'w', encoding='utf-8') as f:
        f.write(transcript)
    
    print("Cartesia transcript retrieved and saved to ./cartesia_transcript/cartesia.txt")
    return

def check_spaces():
    pass

def compare_chars():
    pass

def calculate_cer():
    pass

def main():
    source_of_truth = normalize_true_transcript()
    get_deepgram_transcript()
    get_cartesia_transcript()
    check_spaces()
    compare_chars()
    calculate_cer()

if __name__ == "__main__":
    main()
