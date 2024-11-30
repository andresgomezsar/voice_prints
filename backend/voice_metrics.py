def calculate_voice_metrics(transcription: str, duration_seconds: float) -> dict:
    """Calculate sentiment and words per minute from transcription."""
    from textblob import TextBlob

    # Sentiment analysis
    blob = TextBlob(transcription)
    sentiment_polarity = blob.sentiment.polarity  # Between -1 and 1

    # Words per minute calculation
    word_count = len(transcription.split())
    duration_minutes = duration_seconds / 60  # Convert duration to minutes
    words_per_minute = word_count / duration_minutes if duration_minutes > 0 else 0

    return {
        "sentiment_polarity": sentiment_polarity,
        "words_per_minute": words_per_minute
    }