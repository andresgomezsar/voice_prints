import torch
import torchaudio
import logging
import json
import asyncio
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple
import os

@dataclass
class VADSegment:
    start: float
    end: float
    speech_prob: float

class SileroVAD:
    def __init__(self, sample_rate: int = 16000, threshold: float = 0.5, max_gap_ms: int = 500):
        self.sample_rate = sample_rate
        self.threshold = threshold
        self.max_gap_ms = max_gap_ms
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        # Initialize logging
        self._setup_logging()
        
        # Load Silero VAD model with caching
        self.model = self._load_cached_model()
        logging.info(f"Initialized Silero VAD on {self.device}")

    def _setup_logging(self):
        log_dir = Path("vad_logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / f"vad_{torch.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
                logging.StreamHandler()
            ]
        )

    def _load_cached_model(self, force_reload=False):
        """Load Silero VAD model with caching support."""
        cache_dir = Path.home() / ".cache" / "silero_vad"
        cache_dir.mkdir(parents=True, exist_ok=True)
        model_path = cache_dir / "silero_vad.pt"

        if model_path.exists() and not force_reload:
            logging.info("Loading Silero VAD model from cache")
            return torch.jit.load(model_path)
        else:
            logging.info("Downloading Silero VAD model")
            model, utils = torch.hub.load(
                repo_or_dir='snakers4/silero-vad',
                model='silero_vad',
                force_reload=True
            )
            torch.jit.save(model, model_path)
            return model

    async def _load_audio(self, audio_path: str) -> Tuple[torch.Tensor, int]:
        """Load and preprocess audio file."""
        try:
            wav, sr = await asyncio.to_thread(torchaudio.load, audio_path)
            
            # Convert to mono if stereo
            if wav.shape[0] > 1:
                wav = wav.mean(dim=0, keepdim=True)
            
            # Resample if needed
            if sr != self.sample_rate:
                wav = await asyncio.to_thread(
                    torchaudio.functional.resample, 
                    wav, 
                    sr, 
                    self.sample_rate
                )
            
            return wav.squeeze(0), self.sample_rate
        
        except Exception as e:
            logging.error(f"Error loading audio file {audio_path}: {str(e)}")
            raise

    async def process_file(self, audio_path: str) -> List[VADSegment]:
        """Process audio file and return speech segments."""
        logging.info(f"Processing file: {audio_path}")
        
        # Load audio
        audio, sr = await self._load_audio(audio_path)
        
        # Get speech probabilities
        speech_probs = await asyncio.to_thread(
            self.model, 
            audio, 
            self.sample_rate
        )
        
        # Convert probabilities to segments
        segments = self._convert_probs_to_segments(speech_probs.squeeze().cpu().numpy())
        
        # Merge close segments
        merged_segments = self._merge_segments(segments)
        
        # Save metadata
        await self._save_metadata(audio_path, merged_segments)
        
        contains_speech = len(merged_segments) > 0
        if contains_speech:
            logging.info(f"Speech detected in {audio_path}: {len(merged_segments)} segments")
        else:
            logging.warning(f"No speech detected in {audio_path}")
        
        return merged_segments

    def _convert_probs_to_segments(self, speech_probs) -> List[VADSegment]:
        """Convert model probabilities to VADSegment objects."""
        segments = []
        in_speech = False
        current_start = 0
        
        for i, prob in enumerate(speech_probs):
            if prob >= self.threshold and not in_speech:
                current_start = i
                in_speech = True
            elif prob < self.threshold and in_speech:
                segments.append(VADSegment(
                    start=current_start / self.sample_rate,
                    end=i / self.sample_rate,
                    speech_prob=float(speech_probs[current_start:i].mean())
                ))
                in_speech = False
        
        # Handle speech at the end of audio
        if in_speech:
            segments.append(VADSegment(
                start=current_start / self.sample_rate,
                end=len(speech_probs) / self.sample_rate,
                speech_prob=float(speech_probs[current_start:].mean())
            ))
        
        return segments

    def _merge_segments(self, segments: List[VADSegment]) -> List[VADSegment]:
        """Merge segments that are close together."""
        if not segments:
            return []
        
        max_gap_sec = self.max_gap_ms / 1000
        merged = [segments[0]]
        
        for current in segments[1:]:
            previous = merged[-1]
            if current.start - previous.end <= max_gap_sec:
                merged[-1] = VADSegment(
                    start=previous.start,
                    end=max(previous.end, current.end),
                    speech_prob=max(previous.speech_prob, current.speech_prob)
                )
            else:
                merged.append(current)
        
        return merged

    async def _save_metadata(self, audio_path: str, segments: List[VADSegment]):
        """Save VAD results to a JSON file."""
        metadata = {
            "filename": Path(audio_path).name,
            "sampling_rate": self.sample_rate,
            "threshold": self.threshold,
            "segments": [vars(segment) for segment in segments],
            "total_segments": len(segments),
            "processing_time": torch.datetime.now().isoformat()
        }
        
        output_dir = Path("vad_results")
        output_dir.mkdir(exist_ok=True)
        
        output_path = output_dir / f"{Path(audio_path).stem}_vad.json"
        await asyncio.to_thread(lambda: json.dump(metadata, open(output_path, 'w'), indent=2))
        logging.info(f"Saved VAD results to {output_path}")

async def main():
    # Example usage
    vad = SileroVAD()
    audio_dir = Path("audio_files")
    
    for audio_file in audio_dir.glob("*.wav"):
        try:
            segments = await vad.process_file(str(audio_file))
            if segments:
                print(f"Speech detected in {audio_file.name}, sending for transcription...")
            else:
                print(f"No speech detected in {audio_file.name}, skipping...")
        except Exception as e:
            logging.error(f"Failed to process {audio_file}: {e}")

if __name__ == "__main__":
    asyncio.run(main())