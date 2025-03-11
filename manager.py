import os
import time
import threading
from datetime import datetime
import pygame

from config import AppConfig

class SoundManager:
    """Manages sound effects for the application."""

    def __init__(self, resources_path: str):
        """Initialize the SoundManager."""
        self.PORT_DETECTED_SOUND_PATH = os.path.join(resources_path, 'port_detected.mp3')
        self.SCAN_COMPLETED_SOUND_PATH = os.path.join(resources_path, 'scan_completed.mp3')
        pygame.mixer.init()

    def play_port_detected_sound(self):
        """Plays port detected sound."""
        pygame.mixer.music.stop()  # Önceki sesi durdur
        pygame.mixer.music.load(self.PORT_DETECTED_SOUND_PATH)
        pygame.mixer.music.play()

    def play_scan_completed_sound(self):
        """Plays scan completed sound."""
        pygame.mixer.music.load(self.SCAN_COMPLETED_SOUND_PATH)
        pygame.mixer.music.play()

class TimeManager:
    """Class to manage timestamps and duration calculations."""

    @staticmethod
    def get_formatted_time() -> str:
        """Return the current time formatted as a string."""
        return datetime.now().strftime(AppConfig.LOG_DATE_FORMAT)

    @staticmethod
    def get_current_time() -> float:
        """Get the current time in seconds since the epoch."""
        return time.time()

    @staticmethod
    def calculate_duration(start: float, end: float) -> float:
        """Calculate the duration between two timestamps."""
        return end - start

    @staticmethod
    def get_elapsed_time(start: float) -> float:
        """Calculate the elapsed time since the start time."""
        return TimeManager.get_current_time() - start

    @staticmethod
    def estimate_remaining_time(elapsed: float, progress: int, total: int) -> float:
        """Calculate the estimated time remaining."""
        return (elapsed / progress) * (total - progress)

class LogManager:
    """Class to manage logging functionality."""

    @staticmethod
    def log_message(log_widget, message: str) -> None:
        """Log a message to the specified widget."""
        log_widget.insert('end', f"{TimeManager.get_formatted_time()} - {message}\n")
        log_widget.see('end')

class FileManager:
    """Class to manage file operations."""

    @staticmethod
    def save_to_file(filename: str, data: str) -> None:
        """Save data to a file."""
        with open(filename, 'w') as file:
            file.write(data)

class ThreadManager:
    """Manage threads for the port scanner application."""

    def __init__(self) -> None:
        """Initialize the ThreadManager."""
        self.threads = []

    def start_thread(self, target, args=()) -> None:
        """Start a new thread with the given target function and arguments."""
        thread = threading.Thread(target=target, args=args)
        thread.start()
        self.threads.append(thread)

    def stop_all_threads(self) -> None:
        """Stop all running threads except the current one."""
        current_thread = threading.current_thread()
        for thread in self.threads:
            if thread != current_thread:
                thread.join()