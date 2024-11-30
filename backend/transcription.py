import mlx_whisper

def transcribe_audio(filepath: str) -> str:
    """Transcribe audio file using mlx_whisper."""
    result = mlx_whisper.transcribe(
        filepath,
        path_or_hf_repo="mlx-community/whisper-turbo"
    )
    transcription = result["text"]
    return transcription