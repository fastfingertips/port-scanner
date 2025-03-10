import json
import os
import socket
import tkinter
from tkinter import messagebox
import pygame
import customtkinter as ctk

from config import AppConfig
from manager import FileManager, LogManager, ThreadManager, TimeManager

class BaseApp:
    """Base class for GUI applications."""

    def __init__(self) -> None:
        """Initialize the base application."""
        self.root = ctk.CTk()
        self.root.title(AppConfig.WINDOW_TITLE)
        self.root.geometry(f'{AppConfig.WINDOW_WIDTH}x{AppConfig.WINDOW_HEIGHT}')
        self.root.configure(font=(AppConfig.FONT_FAMILY, AppConfig.FONT_SIZE))

    def mainloop(self) -> None:
        """Run the application's main loop."""
        self.root.mainloop()

class App(BaseApp):
    """Main GUI class for the port scanner application."""

    def __init__(self) -> None:
        """Initialize the App with the main window."""
        super().__init__()
        AppConfig.apply_theme(self.root)
        pygame.mixer.init()

        self.results_dir = os.path.join(os.path.dirname(__file__), "results")
        os.makedirs(self.results_dir, exist_ok=True)

        # Create menu bar
        self.menu_bar = tkinter.Menu(
            self.root,
            bg=AppConfig.COLORS["background"],
            fg=AppConfig.COLORS["foreground"],
            activebackground=AppConfig.COLORS["active_background"],
            activeforeground=AppConfig.COLORS["active_foreground"]
        )
        self.root.config(menu=self.menu_bar)

        # File menu
        self.file_menu = tkinter.Menu(
            self.menu_bar,
            tearoff=0,
            bg=AppConfig.COLORS["background"],
            fg=AppConfig.COLORS["foreground"],
            activebackground=AppConfig.COLORS["active_background"],
            activeforeground=AppConfig.COLORS["active_foreground"]
        )
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Save Results as JSON", command=lambda: self.save_results("json"))
        self.file_menu.add_command(label="Save Results as TXT", command=lambda: self.save_results("txt"))
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)

        # Settings menu
        self.settings_menu = tkinter.Menu(
            self.menu_bar,
            tearoff=0,
            bg=AppConfig.COLORS["background"],
            fg=AppConfig.COLORS["foreground"],
            activebackground=AppConfig.COLORS["active_background"],
            activeforeground=AppConfig.COLORS["active_foreground"]
        )
        self.menu_bar.add_cascade(label="Settings", menu=self.settings_menu)
        self.settings_menu.add_command(
            label="Change Theme",
            command=lambda: AppConfig.toggle_theme()
        )

        self.local_ip = self.get_local_ip()

        self.scanning = False  # Add scanning flag

        self.timeout = AppConfig.DEFAULT_TIMEOUT
        self.threads = AppConfig.DEFAULT_THREADS
        self.port_range = AppConfig.DEFAULT_PORT_RANGE

        self.thread_manager = ThreadManager()  # Initialize ThreadManager

        self.create_widgets()

        # Check the initial IP address
        self.on_ip_change(self.local_ip)

        # Log the application start time
        self.start_time = TimeManager.get_current_time()
        LogManager.log_message(self.general_logs, "Application started")

    def get_local_ip(self) -> str:
        """Get the local IP address of the machine."""
        return socket.gethostbyname(socket.gethostname())

    def create_widgets(self) -> None:
        """Create the widgets for the application."""
        # Main frame
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # IP Address Label and ComboBox
        self.ip_label = ctk.CTkLabel(
            main_frame,
            text="IP Address:"
        )
        self.ip_entry = ctk.CTkComboBox(
            main_frame,
            width=150,
            values=AppConfig.PREDEFINED_IPS,
            command=self.on_ip_change
        )
        self.ip_status_label = ctk.CTkLabel(
            main_frame,
            text=""
        )

        self.ip_label.grid(row=0, column=0, padx=5, pady=5)
        self.ip_entry.set(self.local_ip)
        self.ip_entry.grid(row=0, column=1, padx=5, pady=5)
        self.ip_status_label.grid(row=0, column=2, padx=5, pady=5)

        # Başlangıç Portu
        self.start_port_label = ctk.CTkLabel(
            main_frame,
            text="Start Port:"
        )
        self.start_port_entry = ctk.CTkEntry(
            main_frame,
            width=100
        )
        self.start_port_slider = ctk.CTkSlider(
            main_frame,
            from_=1,
            to=65535,
            orientation="horizontal",
            command=self.update_start_port_entry
        )

        self.start_port_label.grid(row=1, column=0, padx=5, pady=5)
        self.start_port_entry.grid(row=1, column=1, padx=5, pady=5)
        self.start_port_entry.insert(0, "1")
        self.start_port_slider.grid(row=1, column=2, padx=5, pady=5)
        self.start_port_slider.set(1)

        # Bitiş Portu
        self.end_port_label = ctk.CTkLabel(
            main_frame,
            text="End Port:"
        )
        self.end_port_entry = ctk.CTkEntry(
            main_frame,
            width=100
        )
        self.end_port_slider = ctk.CTkSlider(
            main_frame,
            from_=1,
            to=65535,
            orientation="horizontal",
            command=self.update_end_port_entry
        )

        self.end_port_label.grid(row=2, column=0, padx=5, pady=5)
        self.end_port_entry.grid(row=2, column=1, padx=5, pady=5)
        self.end_port_entry.insert(0, "1024")
        self.end_port_slider.grid(row=2, column=2, padx=5, pady=5)
        self.end_port_slider.set(1024)

        # Butonlar
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)

        # Widget Definitions
        self.scan_button = ctk.CTkButton(
            button_frame,
            text=AppConfig.SCAN_BUTTON_TEXT,
            command=self.start_scan
        )
        self.stop_button = ctk.CTkButton(
            button_frame,
            text=AppConfig.STOP_BUTTON_TEXT,
            command=self.stop_scan
        )

        # Widget Placements
        self.scan_button.pack(side='left', padx=5)
        self.stop_button.pack(side='left', padx=5)
        self.stop_button.pack_forget()
        self.stop_button.configure(state="disabled")

        # Progress Bar with scan range label (initially hidden)
        self.progress_frame = ctk.CTkFrame(main_frame)
        self.progress_frame.grid(row=4, column=0, columnspan=3, padx=5, pady=5, sticky='ew')
        self.progress_label_left = ctk.CTkLabel(
            self.progress_frame,
            text="Progress:"
        )
        self.progress_label_left.pack(side='left', padx=5, pady=5)
        self.progress = ctk.CTkProgressBar(
            self.progress_frame,
            orientation='horizontal',
            width=250,
            progress_color="green"
        )
        self.progress.pack(side='left', fill='x', expand=True, padx=5, pady=5)
        self.progress_label_right = ctk.CTkLabel(
            self.progress_frame,
            text="0%"
        )
        self.progress_label_right.pack(side='right', padx=5, pady=5)
        self.progress_frame.grid_remove()
        self.scan_range_label = ctk.CTkLabel(
            main_frame,
            text=""
        )
        self.scan_range_label.grid(row=5, column=0, columnspan=3, pady=5, padx=5)
        self.scan_range_label.grid_remove()  # Hide initially

        # Logs Frame
        logs_frame = ctk.CTkFrame(main_frame)
        logs_frame.grid(row=6, column=0, columnspan=3, padx=5, pady=5, sticky='nsew')

        # General Logs
        self.general_logs = ctk.CTkTextbox(
            logs_frame,
            wrap='word',
            height=150,
            autoseparators=True
        )
        self.general_logs.pack(side='left', fill='both', expand=True, padx=5, pady=5)

        # Open Ports List
        self.open_ports_list = ctk.CTkTextbox(
            logs_frame,
            wrap='word',
            height=150,
            width=100,
            autoseparators=True
        )
        self.open_ports_list.pack(side='right', fill='y', padx=5, pady=5)

        # Configure grid weights
        main_frame.grid_rowconfigure(6, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)

    def update_start_port_entry(self, value) -> None:
        """Update the start port entry with the given value."""
        self.start_port_entry.delete(0, "end")
        self.start_port_entry.insert(0, str(int(value)))

    def update_end_port_entry(self, value) -> None:
        """Update the end port entry with the given value."""
        self.end_port_entry.delete(0, "end")
        self.end_port_entry.insert(0, str(int(value)))

    def validate_ip(self, ip: str) -> bool:
        """Validate the given IP address."""
        try:
            socket.inet_aton(ip)
            return True
        except socket.error:
            return False

    def check_ip_reachability(self, ip: str) -> bool:
        """Check if the given IP address is reachable."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                s.connect((ip, 80))
                s.close()
            return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            return False

    def on_ip_change(self, selected_ip: str) -> None:
        """Handle the IP address change event."""
        ip = selected_ip
        if self.validate_ip(ip):
            if self.check_ip_reachability(ip):
                self.ip_status_label.configure(text="Reachable", text_color="green")
            else:
                self.ip_status_label.configure(text="Unreachable", text_color="red")
        else:
            self.ip_status_label.configure(text="Invalid IP", text_color="red")

    def start_scan(self) -> None:
        """Start the port scanning process."""
        ip = self.ip_entry.get()
        if not self.check_ip_reachability(ip):
            response = messagebox.askyesno("Warning", "IP is unreachable. Do you want to continue scanning?")
            if not response:
                return
        start_port = int(self.start_port_entry.get())
        end_port = int(self.end_port_entry.get())

        if start_port > end_port:
            messagebox.showerror("Error", "Start port cannot be greater than end port.")
            return

        self.scanning = True  # Set scanning flag to True
        self.stop_button.pack()  # Show stop button when scan starts
        self.stop_button.configure(state="normal")
        self.scan_button.configure(state="disabled")  # Disable start button when scan starts
        target_ip = self.ip_entry.get()

        self.general_logs.delete(1.0, 'end')
        self.open_ports_list.delete(1.0, 'end')
        self.open_ports = []  # Initialize open_ports list

        # Log the start time
        self.start_time = TimeManager.get_current_time()
        LogManager.log_message(self.general_logs, "Scan started")

        self.scan_range_label.configure(text=f"Scanning {target_ip} from port {start_port} to {end_port}...")
        self.scan_range_label.grid()  # Show scan range label
        self.progress_frame.grid()  # Show progress bar
        self.progress.set(0)
        self.progress['maximum'] = end_port - start_port + 1

        def scan_port(port: int) -> None:
            """Scan a single port and update the UI with the result."""
            if not self.scanning:  # Check scanning flag
                return
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(0.1)
                    result = s.connect_ex((target_ip, port))
                    if result == 0:
                        timestamp = TimeManager.get_formatted_time()
                        try:
                            service = socket.getservbyport(port)
                        except OSError:
                            service = "Unknown"
                        self.open_ports_list.insert('end', f"{port}\n")
                        self.open_ports_list.see('end')
                        self.open_ports.append({'port': port, 'service': service, 'timestamp': timestamp})
                        LogManager.log_message(self.general_logs, f"Port {port} ({service}) is open")
                        self.play_port_detected_sound()
            except Exception as e:
                LogManager.log_message(self.general_logs, f"Error occurred while scanning port {port}: {str(e)}")

        def scan_ports() -> None:
            """Scan the ports in the given range."""
            total_ports = end_port - start_port + 1

            for port in range(start_port, end_port + 1):
                if not self.scanning:  # Check scanning flag
                    break
                self.thread_manager.start_thread(scan_port, args=(port,))

                # Update progress bar and scan range label
                elapsed_time = TimeManager.get_elapsed_time(self.start_time)
                estimated_time = TimeManager.estimate_remaining_time(elapsed_time, port - start_port + 1, total_ports)
                self.scan_range_label.configure(
                    text=f"Scanned {port - start_port + 1} of {total_ports} ports. "
                         f"Elapsed: {elapsed_time:.2f}s, Estimated: {estimated_time:.2f}s"
                )
                self.progress.set((port - start_port + 1) / (end_port - start_port + 1))
                self.progress_label_right.configure(
                    text=f"{(port - start_port + 1) / (end_port - start_port + 1) * 100:.2f}%"
                )
                self.root.update_idletasks()

            # Wait for remaining threads to finish
            self.thread_manager.stop_all_threads()

            if self.scanning:  # Check scanning flag
                duration = TimeManager.calculate_duration(self.start_time, TimeManager.get_current_time())
                self.scan_range_label.configure(text="Scan completed.")
                LogManager.log_message(self.general_logs, "Scan completed")
                LogManager.log_message(self.general_logs, f"Scan duration: {duration:.2f} seconds")
                self.play_scan_completed_sound()
            self.scanning = False  # Set scanning flag to False
            self.stop_button.pack_forget()
            self.stop_button.configure(state="disabled")
            self.scan_button.configure(state="normal")
            self.scan_range_label.grid_remove()  # Remove the scan range label

        # Start the scan in a separate thread
        self.thread_manager.start_thread(scan_ports)

    def stop_scan(self) -> None:
        """Stop the ongoing port scanning process."""
        self.scanning = False
        self.stop_button.pack_forget()
        self.stop_button.configure(state="disabled")
        self.scan_button.configure(state="normal")
        self.progress_frame.grid_remove()
        self.scan_range_label.grid_remove()

    def save_results(self, file_type: str = "txt") -> None:
        """Save the scan results to a file in the results directory."""
        if not hasattr(self, 'open_ports') or not self.open_ports:
            messagebox.showwarning("No Results", "No scan results to save.")
            return

        # Get the current open ports at the time of saving
        current_open_ports = self.open_ports.copy()

        # Get the logs from the general logs textbox
        logs = self.general_logs.get(1.0, 'end').strip()

        # If scanning is in progress, show a warning and adjust the port range
        if self.scanning:
            response = messagebox.askyesno("Warning", "Scanning in progress. Save partial results?")
            if not response:
                return
            current_end_port = self.start_port_slider.get() - 1
        else:
            current_end_port = int(self.end_port_entry.get())

        default_filename = (
            f"scan_results_{self.ip_entry.get()}_"
            f"{TimeManager.get_formatted_time().replace(' ', '_').replace(':', '-')}"
        )
        file_path = os.path.join(self.results_dir, f"{default_filename}.{file_type}")

        if not file_path:
            return

        results = {
            'ip': self.ip_entry.get(),
            'start_port': int(self.start_port_entry.get()),
            'end_port': current_end_port,
            'open_ports': current_open_ports,
            'logs': logs,
            'timestamp': TimeManager.get_formatted_time()
        }

        if file_path.endswith('.json'):
            FileManager.save_to_file(file_path, json.dumps(results, indent=4))
            messagebox.showinfo("Success", f"Results saved successfully to {file_path}")
        else:
            results_str = (
                f"=== Scan Results ===\n"
                f"Target IP: {self.ip_entry.get()}\n"
                f"Scan Range: {self.start_port_entry.get()} - {current_end_port}\n"
                f"Timestamp: {TimeManager.get_formatted_time()}\n"
                f"Status: {'In Progress' if self.scanning else 'Completed'}\n\n"
                "=== Open Ports ===\n"
            )
            for port in current_open_ports:
                results_str += f"{port['port']} ({port['service']})\n"
            results_str += (
                "\n=== Logs ===\n"
                f"{logs}\n\n"
                "=== Summary ===\n"
                f"Total Ports Scanned: {current_end_port - int(self.start_port_entry.get()) + 1}\n"
                f"Open Ports Found: {len(current_open_ports)}\n"
            )
            FileManager.save_to_file(file_path, results_str)
            messagebox.showinfo("Success", f"Results saved successfully to {file_path}")

    def play_port_detected_sound(self):
        """Plays port detected sound."""
        pygame.mixer.music.stop()  # Önceki sesi durdur
        pygame.mixer.music.load('resources/port_detected.mp3')
        pygame.mixer.music.play()

    def play_scan_completed_sound(self):
        """Plays scan completed sound."""
        pygame.mixer.music.load('resources/scan_completed.mp3')
        pygame.mixer.music.play()

if __name__ == "__main__":
    try:
        app = App()
        app.mainloop()
    except Exception as e:
        print(f"An error occurred: {e}")
