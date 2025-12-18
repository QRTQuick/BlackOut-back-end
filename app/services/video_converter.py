import os

# Try to import moviepy, but make it optional
try:
    from moviepy.editor import VideoFileClip
    VIDEO_CONVERSION_AVAILABLE = True
except ImportError:
    VIDEO_CONVERSION_AVAILABLE = False
    VideoFileClip = None

def convert_video(input_path, output_path, target_format):
    """Convert video files between different formats"""
    if not VIDEO_CONVERSION_AVAILABLE:
        raise Exception("Video conversion not available - missing system dependencies (ffmpeg)")
    
    try:
        # Load video
        video = VideoFileClip(input_path)
        
        target_format = target_format.lower()
        
        if target_format == 'mp4':
            video.write_videofile(output_path, codec='libx264')
        elif target_format == 'avi':
            video.write_videofile(output_path, codec='libxvid')
        elif target_format == 'mov':
            video.write_videofile(output_path, codec='libx264')
        elif target_format == 'webm':
            video.write_videofile(output_path, codec='libvpx')
        elif target_format == 'gif':
            video.write_gif(output_path)
        else:
            raise ValueError(f"Unsupported video format: {target_format}")
        
        video.close()
        
    except Exception as e:
        raise Exception(f"Video conversion failed: {str(e)}")

def extract_audio_from_video(input_path, output_path):
    """Extract audio from video file"""
    if not VIDEO_CONVERSION_AVAILABLE:
        raise Exception("Video processing not available - missing system dependencies")
    
    try:
        video = VideoFileClip(input_path)
        audio = video.audio
        
        if audio is not None:
            audio.write_audiofile(output_path)
            audio.close()
        else:
            raise Exception("No audio track found in video")
        
        video.close()
        
    except Exception as e:
        raise Exception(f"Audio extraction failed: {str(e)}")

def get_video_info(input_path):
    """Get video file information"""
    if not VIDEO_CONVERSION_AVAILABLE:
        return {"error": "Video processing not available"}
    
    try:
        video = VideoFileClip(input_path)
        info = {
            "duration": video.duration,
            "fps": video.fps,
            "size": video.size,
            "has_audio": video.audio is not None
        }
        video.close()
        return info
    except Exception as e:
        return {"error": str(e)}

def is_video_conversion_available():
    """Check if video conversion is available"""
    return VIDEO_CONVERSION_AVAILABLE