# Voice Prints: Advanced Audio Processing System

## Overview
Voice Prints transforms everyday conversations into actionable insights using advanced audio processing and natural language analysis. Designed for non-invasive cognitive and emotional monitoring, it leverages a wearable device to process speech patterns in natural settings while maintaining user privacy.

---

## Core Features

### 1. Audio Processing Pipeline
- **Voice Activity Detection (VAD)**:
  - Speech isolation using Silero VAD.
  - Optimized chunking for efficient storage and processing.
- **Speaker Diarization**:
  - Multi-speaker tracking with WhisperX and Pyannote.
  - Real-time interaction dynamics analysis.
- **Audio Enhancement**:
  - Noise reduction and clarity optimization.
  - Privacy-preserving local audio processing.

### 2. Natural Language Processing (NLP) Engine
- Speech-to-text transcription with Whisper.
- Linguistic feature extraction (e.g., grammatical complexity, pauses).
- Sentiment and semantic content analysis.

### 3. Metrics Dashboard
- Real-time data visualization of metrics.
- Historical trend analysis.
- Insights like Words Per Minute (WPM), sentiment, and engagement metrics.

---

## Technical Workflow

Raw Audio → VAD → Speaker Diarization → Transcription → Analysis → Insights

---

## Setup Instructions

### Prerequisites
- **Node.js** and **npm** for the frontend.
- **Python 3.9+** for the backend.

### Frontend Setup
1. Navigate to the `frontend` directory:
    ```bash
    cd frontend
    ```

2. Install dependencies:
    ```bash
    npm install
    ```

3. Start the development server:
    ```bash
    npm start
    ```
    The app will be available at [http://localhost:3000](http://localhost:3000).

### Backend Setup
1. Navigate to the `backend` directory:
    ```bash
    cd backend
    ```

2. Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Start the backend server:
    ```bash
    uvicorn app.main:app --reload
    ```
    The backend will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Privacy and Ethics

Voice Prints is designed with privacy at its core:
- Local Processing: All audio is processed locally when possible, ensuring sensitive data is not shared unnecessarily.
- Anonymized Insights: Outputs are stripped of personally identifiable information.
- Encrypted Data: Secure transmission and storage of audio and derived metrics.

---

## Applications

- Cognitive Monitoring: Early detection of neurodegenerative diseases through linguistic biomarkers.
- Psychiatric Assessment: Tracking speech changes in response to medication.
- Assistive Technologies: AI-driven tools for cognitive engagement in elderly or isolated populations.
- Real-Time Insights: Interactive dashboards for monitoring and exploring daily speech metrics.

---

## Future Directions

- Enhanced speaker diarization accuracy.
- Expanded language analysis capabilities (e.g., idea density, conversational flow).
- Integration with distributed GPU services like Salad for scalable processing.

---

## License

Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0)
