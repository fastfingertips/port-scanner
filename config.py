import customtkinter as ctk

class AppConfig:
    """Class to manage UI configuration and theme settings."""

    # UI Settings
    WINDOW_WIDTH = 480
    WINDOW_HEIGHT = 480
    FONT_SIZE = 12
    FONT_FAMILY = 'Arial'
    WINDOW_TITLE = 'Port Scanner'
    SCAN_BUTTON_TEXT = 'Scan'
    STOP_BUTTON_TEXT = 'Stop'
    COLORS = {
        "background": "#2b2b2b",
        "foreground": "white",
        "active_background": "#3b3b3b",
        "active_foreground": "white"
    }
    THEME_SETTINGS = {
        "appearance_mode": "dark",
        "color_theme": "dark-blue"
    }
    resources_directory_name = 'resources'

    # Scan Settings
    DEFAULT_TIMEOUT = 1.0
    DEFAULT_THREADS = 100
    DEFAULT_PORT_RANGE = (1, 1024)

    # Log Settings
    LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

    # Network Settings
    DEFAULT_IP = '127.0.0.1'
    PREDEFINED_IPS = [
        "127.0.0.1",
        "192.168.1.1",
        "192.168.0.1",
        "10.0.0.1"
    ]

    @staticmethod
    def apply_theme(root) -> None:
        """Apply the theme settings to the root window."""
        ctk.set_appearance_mode(AppConfig.THEME_SETTINGS["appearance_mode"])
        ctk.set_default_color_theme(AppConfig.THEME_SETTINGS["color_theme"])
        root.configure(bg=AppConfig.COLORS["background"])

    @staticmethod
    def toggle_theme() -> None:
        """Toggle between dark and light themes."""
        ctk.set_appearance_mode("Dark" if ctk.get_appearance_mode() == "Light" else "Light")
