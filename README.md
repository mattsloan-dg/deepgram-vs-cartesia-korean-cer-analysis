# Deepgram vs. Cartesia Korean CER Analysis

Deepgram (nova-3) vs. Cartesia (ink-whisper) Korean CER (character error rate) analysis

## Prerequisites

You must install [uv](https://docs.astral.sh/uv/). This can be installed very easily with one short terminal command:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

You must have a [Deepgram API Key](https://developers.deepgram.com/home)

You must have a [Cartesia API Key](https://docs.cartesia.ai/get-started/overview)

## Setup

This project includes example files in the `audio` and `true_transcript` directories for testing. These example audio and source of truth transcript files were pulled from the following [HuggingFace dataset](https://huggingface.co/datasets/kresnik/zeroth_korean) (the first 100 records of the dataset).

You're welcome to run the script with these examples first, or replace them with your own files.

### Audio Directory

The `audio` directory expects a single audio file named **`master_korean_audio.wav`**.

**Requirements:**

- File name: `master_korean_audio.wav`
- Format: WAV audio format

**If your audio file is not in WAV format**, use ffmpeg to convert it:

```bash
ffmpeg -i <original_file>.mp3 <converted_file>.wav
```

The above example shows how to convert a .mp3 file (original). To convert from a different audio file format, please see the [ffmpeg docs](https://www.ffmpeg.org/ffmpeg.html).

Then rename the converted file to `master_korean_audio.wav` and place it in the `audio` directory.

### True Transcript Directory

The `true_transcript` directory expects a single text file named **`master_korean_transcript.txt`**.

This will be our source of truth transcript. It is the 100% accurate transcript, which we will compare the Deepgram and Cartesia outputted transcripts to and measure the accuracy.

**Requirements:**

- File name: `master_korean_transcript.txt`
- Content: A single continuous line containing the full transcript in Korean characters
- **No punctuation, line breaks, or paragraphs** - just one long line of Korean text

## Running the Script

Follow these steps to run the analysis:

1. **Set up your environment variables** by copying the example file:

```bash
cp .env.example .env
```

2. **Add your API keys** to the `.env` file:

   - Open `.env` in your editor
   - Replace the placeholder values with your actual Deepgram and Cartesia API keys

3. **Sync dependencies** using uv:

```bash
uv sync
```

4. **Run the program**:

```bash
uv run python main.py
```

The script will generate transcripts in both `deepgram_transcript` and `cartesia_transcript` directories, and output the CER (Character Error Rate) analysis comparing both services against your source of truth transcript, in the `results` directory.
