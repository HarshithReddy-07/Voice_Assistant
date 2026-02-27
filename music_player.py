import vlc
import yt_dlp
import time
import threading
from utils import speak

# Global player instance
vlc_instance = vlc.Instance()
player = vlc_instance.media_player_new()

current_play_thread = None
abort_extraction = False

def get_youtube_audio_url(video_url):
    """Extracts the direct audio stream URL from a YouTube link."""
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(video_url, download=False)
            return info.get('url') if info else None
        except Exception as e:
            speak(f"Error extracting audio URL: {e}")
            return None

def play_music_task(video_url):
    """Runs the extraction and playback in a separate thread."""
    global abort_extraction
    
    audio_url = get_youtube_audio_url(video_url)
    # If the user pressed stop while we were extracting, abort securely.
    if abort_extraction:
        return
        
    if not audio_url:
        speak("Could not find audio URL.")
        return

    media = vlc_instance.media_new(audio_url)
    player.set_media(media)
    player.play()

    # Wait until playback starts
    time.sleep(1)
    
    # Stop playback if user typed 'stop' exactly as it started playing
    if abort_extraction:
        player.stop()
    elif player.is_playing():
        speak(f"Now playing audio from: {video_url}")
    else:
        print("Playback failed to start or is still buffering.")

def play_youtube_audio(video_url):
    """Initiates playback, cancelling any ongoing extraction/playback."""
    global current_play_thread, abort_extraction
    
    # Resume if paused instead of restarting?
    # If the exact same URL is requested while paused, we could resume,
    # but normally a new play command means a new song.
    state = str(player.get_state())
    if state == 'State.Paused':
        player.set_pause(0)
        # print("Music resumed.")
        return
    stop_audio() # Ensure anything playing is stopped first
    abort_extraction = False
    
    current_play_thread = threading.Thread(target=play_music_task, args=(video_url,))
    current_play_thread.daemon = True # Allow exit while extracting
    current_play_thread.start()

def stop_audio():
    """Stops the current playback and aborts any pending extractions."""
    global abort_extraction
    abort_extraction = True 
    
    state = str(player.get_state())
    if state not in ('State.Stopped', 'State.NothingSpecial', 'State.Ended'):
        player.stop()
        # print("Music stopped.")

def pause_audio():
    """Pauses or resumes the current playback."""
    state = str(player.get_state())
    if state == 'State.Playing':
        player.set_pause(1) # 1 maps to pause
        # print("Music paused.")
    elif state == 'State.Paused':
        player.set_pause(0) # 0 maps to resume
        # print("Music resumed.")
    else:
        speak("No music to pause/resume right now.")
