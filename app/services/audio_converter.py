import os

# Try to import pydub, but make it optional
try:
    from pydub import AudioSegment
    AUDIO_CONVERSION_AVAILABLE = True
except ImportError:
    AUDIO_CONVERSION_AVAILABLE = False
    AudioSegment = None

def convert_audio(input_path, output_path, target_format):
    """Convert audio files between different formats"""
    if not AUDIO_CONVERSION_AVAILABLE:
        raise Exception("Audio conversion not available - missing system dependencies (ffmpeg)")
    
    try:
        # Load audio file
        audio = AudioSegment.from_file(input_path)
        
        # Export to target format
        if target_format.lower() == 'mp3':
            audio.export(output_path, format="mp3")
        elif target_format.lower() == 'wav':
            audio.export(output_path, format="wav")
        elif target_format.lower() == 'ogg':
            audio.export(output_path, format="ogg")
        elif target_format.lower() == 'flac':
            audio.export(output_path, format="flac")
        elif target_format.lower() == 'aac':
            audio.export(output_path, format="aac")
        elif target_format.lower() == 'm4a':
            audio.export(output_path, format="m4a")
        else:
            raise ValueError(f"Unsupported audio format: {target_format}")
            
    except Exception as e:
        raise Exception(f"Audio conversion failed: {str(e)}")

def get_audio_info(input_path):
    """Get audio file information"""
    if not AUDIO_CONVERSION_AVAILABLE:
        return {"error": "Audio processing not available"}
    
    try:
        audio = AudioSegment.from_file(input_path)
        return {
            "duration": len(audio) / 1000.0,  # seconds
            "channels": audio.channels,
            "sample_rate": audio.frame_rate,
            "format": audio.sample_width * 8  # bits
        }
    except Exception as e:
        return {"error": str(e)}

def is_audio_conversion_available():
    """Check if audio conversion is available"""
    return AUDIO_CONVERSION_AVAILABLE