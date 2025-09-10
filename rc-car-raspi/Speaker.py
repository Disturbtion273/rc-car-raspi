import os
import tempfile
import threading
from gtts import gTTS
import sounddevice as sd
import soundfile as sf
from pydub import AudioSegment

class Speaker:
    device = None
    volume = 1.0
    
    @classmethod
    def initialize(cls, device=None, volume=1.0):
        """
        Initialize static parameters:
        device: ALSA device (e.g., 'plughw:0,0'), None = default device
        volume: volume level (0.0 to 1.0)
        """
        if device is None:
            device = sd.default.device[1]  # output device
        if device is None or device < 0:
            raise RuntimeError("No default output device found.")
        cls.device = device
        cls.volume = volume

    @staticmethod
    def Speak(text, lang="de", callback=None):
        """Non-blocking Text-to-Speech using threading"""
        def _speak_thread():
            try:
                if Speaker.device is None:
                    raise RuntimeError("Speaker not initialized. Call Speaker.initialize() first.")
                
                # Create temporary mp3 file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                    mp3_file = f.name
                
                tts = gTTS(text=text, lang=lang)
                tts.save(mp3_file)
                
                # Convert mp3 -> wav
                wav_file = mp3_file.replace(".mp3", ".wav")
                sound = AudioSegment.from_mp3(mp3_file)
                sound.export(wav_file, format="wav")
                
                # Play WAV file 
                data, samplerate = sf.read(wav_file, dtype='float32')
                print("Speak: " + text)
                sd.play(data * Speaker.volume, samplerate, device=Speaker.device)
                sd.wait()  
                
                # Clean up temporary files
                os.remove(mp3_file)
                os.remove(wav_file)
                
                # Call callback if provided
                if callback:
                    callback()
                    
            except Exception as e:
                print(f"Error in speech thread: {e}")
        
        # Start speech in separate daemon thread
        thread = threading.Thread(target=_speak_thread, daemon=True)
        thread.start()
        return thread