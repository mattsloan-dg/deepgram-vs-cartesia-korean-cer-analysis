# deepgram-vs-cartesia-korean-cer-analysis

Deepgram (nova-3) vs. Cartesia (ink-whisper) Korean CER (character error rate) analysis

## Setup

This project includes example files in the required directories for testing. You're welcome to run the script with these examples first, or replace them with your own files.

### Audio Directory

The `audio` directory expects a single audio file named **`master_korean_audio.wav`**.

**Requirements:**

- File name: `master_korean_audio.wav`
- Format: WAV audio format

**If your audio file is not in WAV format**, use ffmpeg to convert it:

```bash
ffmpeg -i <original_file>.mp3 <converted_file>.wav
```

Then rename the converted file to `master_korean_audio.wav` and place it in the `audio` directory.

### True Transcript Directory

The `true_transcript` directory expects a single text file named **`master_korean_transcript.txt`**.

This will be our source of truth transcript. It is the 100% accurate transcript, which we will compare the Deepgram and Cartesia outputted transcripts to and measure the accuracy.

**Requirements:**

- File name: `master_korean_transcript.txt`
- Content: A single continuous line containing the full transcript in Korean characters
- **No punctuation, line breaks, or paragraphs** - just one long line of Korean text
