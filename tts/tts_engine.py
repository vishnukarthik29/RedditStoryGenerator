import os
import pyttsx3
import logging
import tempfile
from typing import Dict, Optional

import config

logger = logging.getLogger(__name__)

class TTSEngine:
    """Text-to-speech engine using pyttsx3."""
    
    def __init__(self, voice_id: Optional[str] = None, rate: int = config.TTS_RATE):
        """
        Initialize the TTS engine.
        
        Args:
            voice_id: ID of the voice to use (None for default)
            rate: Speech rate in words per minute
        """
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', rate)
        
        # Set voice if specified
        if voice_id:
            self.engine.setProperty('voice', voice_id)
        
        logger.info(f"TTS engine initialized with rate {rate}")
    
    def list_available_voices(self) -> Dict[str, str]:
        """
        List all available voices.
        
        Returns:
            Dictionary mapping voice IDs to voice names
        """
        voices = {}
        for voice in self.engine.getProperty('voices'):
            voices[voice.id] = voice.name
        return voices
    
    def text_to_speech(self, text: str, output_path: Optional[str] = None) -> str:
        """
        Convert text to speech and save as an audio file.
        
        Args:
            text: Text to convert to speech
            output_path: Path to save the audio file (if None, a temporary file is created)
            
        Returns:
            Path to the generated audio file
        """
        if not text:
            logger.warning("Empty text provided to TTS engine")
            return ""
            
        try:
            # Create a temporary file if no output path is specified
            if output_path is None:
                fd, output_path = tempfile.mkstemp(suffix='.mp3')
                os.close(fd)
                
            logger.info(f"Converting text to speech: {text[:50]}...")
            
            # Save audio to file
            self.engine.save_to_file(text, output_path)
            self.engine.runAndWait()
            
            logger.info(f"Audio saved to {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error in text-to-speech conversion: {e}")
            return ""
    
    def estimate_duration(self, text: str) -> float:
        """
        Estimate the duration of the speech in seconds.
        
        Args:
            text: Text to estimate duration for
            
        Returns:
            Estimated duration in seconds
        """
        # Average English word is ~5 characters
        word_count = len(text.split())
        
        # Calculate duration based on TTS rate (words per minute)
        duration = (word_count / config.TTS_RATE) * 60
        
        # Add some buffer time
        duration *= 1.1
        
        return duration