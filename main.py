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
    """
    Call Deepgram API to transcribe Korean audio file and return normalized transcript.
    """
    import os
    import requests
    from dotenv import load_dotenv
    import string
    import json
    
    # Load environment variables
    load_dotenv()
    api_key = os.getenv('DEEPGRAM_API_KEY')
    
    if not api_key:
        raise ValueError("DEEPGRAM_API_KEY not found in .env file")
    
    # Read audio file
    with open('./audio/master_korean_audio.wav', 'rb') as audio_file:
        audio_data = audio_file.read()
    
    # Make API request to Deepgram
    url = 'https://api.deepgram.com/v1/listen?model=nova-3&language=ko&smart_format=false'
    headers = {
        'Authorization': f'Token {api_key}',
        'Content-Type': 'audio/wav'
    }
    
    print("Calling Deepgram API...")
    response = requests.post(url, headers=headers, data=audio_data)
    response.raise_for_status()
    
    # Extract transcript from response
    result = response.json()
    transcript = result['results']['channels'][0]['alternatives'][0]['transcript']
    words = result['results']['channels'][0]['alternatives'][0]['words']
    concatenated_text = ' '.join([word['word'] for word in words])

    # Normalize transcript (remove punctuation and line breaks)
    transcript = concatenated_text.replace('\n', '').replace('\r', '')
    punctuation = string.punctuation + '。，、；：？！''""（）《》【】'
    for char in punctuation:
        transcript = transcript.replace(char, '')
    
    # Save transcript to file
    with open('./deepgram_transcript/deepgram.txt', 'w', encoding='utf-8') as f:
        f.write(transcript)
    
    print("Deepgram transcript retrieved and saved to ./deepgram_transcript/deepgram.txt")
    return

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
    get_deepgram_transcript()
    get_cartesia_transcript()
    check_spaces()
    compare_chars()
    calculate_cer()

if __name__ == "__main__":
    main()
