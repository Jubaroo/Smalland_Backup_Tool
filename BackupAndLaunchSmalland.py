import json
import os
import shutil
import subprocess
import threading
import time
import tkinter as tk
import webbrowser
from datetime import datetime
from pathlib import Path
from tkinter import simpledialog, ttk, scrolledtext, messagebox

import psutil

settings_file = Path("settings.json")
backup_path = Path.home() / "AppData/Local/SMALLAND/Saved/SaveGames"
settings = {"backupCount": 10, "backupFrequency": 30, "darkMode": False}  # Add 'darkMode' key with a default value
current_language = "en"  # Default language
languages = {"English": "en", "Spanish": "es", "German": "de", "Malaysian": "ms"}

translations = {
    "en": {
        "backup_count": "Set Number of Backups to Keep",
        "backup_frequency": "Set Backup Frequency (minutes)",
        "launch_backup": "Start Smalland",
        "launching_smalland_log": "Launching Smalland...",
        "exit": "Exit",
        "file": "File",
        "open_backup_folder": "Open Backup Folder",
        "settings": "Settings",
        "language": "Language",
        "dark_mode": "Dark Mode",
        "current_settings": "Current settings:\nNumber of backups to keep: {}\nBackup frequency (minutes): {}",
        "backup_complete": "Backup complete. Next backup in {} minutes.",
        "waiting_for_game": "Waiting for Smalland to start...",
        "language_changed_log": "Language changed to {language_name}.",
        "starting_backup_log": "Smalland detected, starting backup process...",
        "stopping_backup_log": "Game has been closed. Stopping backup process...",
        "backup_stopped_log": "Backup process has been stopped.",
        "backup_count_changed_log": "Backup count changed to {}.",
        "backup_frequency_changed_log": "Backup frequency changed to {} minutes."
    },
    "es": {
        "backup_count": "Establecer número de copias de seguridad para mantener",
        "backup_frequency": "Establecer frecuencia de copias de seguridad (minutos)",
        "launch_backup": "Iniciar Smalland",
        "launching_smalland_log": "Iniciando Smalland...",
        "exit": "Salir",
        "file": "Archivo",
        "open_backup_folder": "Abrir carpeta de respaldo",
        "settings": "Configuraciones",
        "language": "Idioma",
        "dark_mode": "Modo Oscuro",
        "current_settings": "Configuraciones actuales:\nNúmero de copias de seguridad para mantener: {}\nFrecuencia de copias de seguridad (minutos): {}",
        "backup_complete": "Copia de seguridad completa. Próxima copia en {} minutos.",
        "waiting_for_game": "Esperando que Smalland inicie...",
        "language_changed_log": "Idioma cambiado a {language_name}.",
        "starting_backup_log": "Smalland detectado, iniciando proceso de copia de seguridad...",
        "stopping_backup_log": "Juego cerrado. Deteniendo proceso de copia de seguridad...",
        "backup_stopped_log": "Proceso de copia de seguridad detenido.",
        "backup_count_changed_log": "Cantidad de copias de seguridad cambiada a {}.",
        "backup_frequency_changed_log": "Frecuencia de copias de seguridad cambiada a {} minutos."
    },
    "de": {
        "backup_count": "Anzahl der zu behaltenden Backups festlegen",
        "backup_frequency": "Backup-Häufigkeit festlegen (Minuten)",
        "launch_backup": "Starte Smalland",
        "launching_smalland_log": "Smalland wird gestartet...",
        "exit": "Beenden",
        "file": "Datei",
        "open_backup_folder": "Backup-Ordner öffnen",
        "settings": "Einstellungen",
        "language": "Sprache",
        "dark_mode": "Dunkler Modus",
        "current_settings": "Aktuelle Einstellungen:\nAnzahl der Backups zum Behalten: {}\nBackup-Frequenz (Minuten): {}",
        "backup_complete": "Backup abgeschlossen. Nächstes Backup in {} Minuten.",
        "waiting_for_game": "Warten auf den Start von Smalland...",
        "language_changed_log": "Sprache geändert zu {language_name}.",
        "starting_backup_log": "Smalland erkannt, Backup-Prozess wird gestartet...",
        "stopping_backup_log": "Spiel wurde geschlossen. Backup-Prozess wird gestoppt...",
        "backup_stopped_log": "Backup-Prozess wurde gestoppt.",
        "backup_count_changed_log": "Anzahl der Backups geändert zu {}.",
        "backup_frequency_changed_log": "Backup-Häufigkeit geändert zu {} Minuten."
    },
    "ms": {
        "backup_count": "Tetapkan Bilangan Sandaran untuk Dikekalkan",
        "backup_frequency": "Tetapkan Frekuensi Sandaran (minit)",
        "launch_backup": "Mulakan Smalland",
        "launching_smalland_log": "Melancarkan Smalland...",
        "exit": "Keluar",
        "file": "Fail",
        "open_backup_folder": "Buka Folder Sandaran",
        "settings": "Tetapan",
        "language": "Bahasa",
        "current_settings": "Tetapan semasa:\nBilangan sandaran untuk dikekalkan: {}\nFrekuensi sandaran (minit): {}",
        "backup_complete": "Sandaran selesai. Sandaran seterusnya dalam {} minit.",
        "waiting_for_game": "Menunggu Smalland untuk bermula...",
        "language_changed_log": "Bahasa ditukar ke {language_name}.",
        "starting_backup_log": "Smalland dikesan, memulakan proses sandaran...",
        "stopping_backup_log": "Permainan telah ditutup. Menghentikan proses sandaran...",
        "backup_stopped_log": "Proses sandaran telah dihentikan.",
        "backup_count_changed_log": "Bilangan sandaran berubah ke {}.",
        "backup_frequency_changed_log": "Frekuensi sandaran berubah ke {} minit.",
        "dark_mode": "Mod Gelap"
    }
}


def load_settings():
    global settings, current_language
    if os.path.exists(settings_file):
        with open(settings_file, 'r') as f:
            data = json.load(f)
            loaded_settings = data.get('settings', {})
            settings = {**{"backupCount": 10, "backupFrequency": 30, "darkMode": False}, **loaded_settings}
            current_language = data.get('language', current_language)
            if current_language not in languages.values():
                current_language = "en"
    else:
        save_settings()


def save_settings():
    with open(settings_file, 'w') as f:
        data = {'settings': settings, 'language': current_language}
        json.dump(data, f, indent=4)


def backup_files():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_dir = backup_path / "backups" / timestamp
    backup_dir.mkdir(parents=True, exist_ok=True)
    for file in backup_path.glob('**/*.sav'):
        if "backups" not in file.parts:
            destination = backup_dir / file.relative_to(backup_path)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file, destination)
    cleanup_backups()


def cleanup_backups():
    backups_dir = backup_path / "backups"
    backups = sorted(backups_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
    for backup in backups[settings['backupCount']:]:
        shutil.rmtree(backup)


def is_game_running(process_name="SMALLAND-Win64-Shipping.exe"):
    return any(proc.name().lower() == process_name.lower() for proc in psutil.process_iter(['name']))


def open_backup_folder():
    webbrowser.open(backup_path)


def get_current_settings():
    return translations[current_language]["current_settings"].format(settings['backupCount'],
                                                                     settings['backupFrequency'])


class BackupGUI:
    def __init__(self, root):
        self.root = root
        self.initialize_gui()
        self.apply_theme()  # Apply theme based on user preference at startup

    def initialize_gui(self):
        # Clear existing GUI components if they exist
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.title("Smalland Backup Tool")
        # Set the window size and center it
        window_width = 500
        window_height = 400
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.settings_label = ttk.Label(self.main_frame, text="", font=('Arial', 10), justify=tk.CENTER)
        self.settings_label.pack(pady=(0, 20))
        self.backup_count_btn = ttk.Button(self.main_frame, text="", command=self.set_backup_count, padding="15 2")
        self.backup_count_btn.pack(pady=5)

        self.backup_frequency_btn = ttk.Button(self.main_frame, text="", command=self.set_backup_frequency,
                                               padding="15 2")
        self.backup_frequency_btn.pack(pady=5)

        self.launch_backup_btn = ttk.Button(self.main_frame, text="", command=self.launch_and_backup, padding="15 2")
        self.launch_backup_btn.pack(pady=5)
        self.console = scrolledtext.ScrolledText(self.main_frame, height=10, state='disabled')
        self.console.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        self.create_menu()
        self.update_text()  # Update text of all elements according to the current language

    def create_menu(self):
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)

        # File Menu
        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label=translations[current_language]["file"], menu=self.file_menu)
        self.file_menu.add_command(label=translations[current_language]["open_backup_folder"],
                                   command=open_backup_folder)
        self.file_menu.add_separator()
        self.file_menu.add_command(label=translations[current_language]["exit"], command=self.root.destroy)

        # Settings Menu
        self.settings_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label=translations[current_language]["settings"], menu=self.settings_menu)

        # Dark Mode Toggle
        dark_mode_menu_label = translations[current_language]["dark_mode"]
        self.settings_menu.add_checkbutton(label=dark_mode_menu_label, onvalue=1, offvalue=0,
                                           variable=self.create_dark_mode_var(), command=self.toggle_dark_mode)

        # Language Submenu
        self.language_menu = tk.Menu(self.settings_menu, tearoff=0)
        self.settings_menu.add_cascade(label=translations[current_language]["language"], menu=self.language_menu)
        for language_name, language_code in languages.items():
            self.language_menu.add_command(
                label=language_name if language_code != current_language else "✓ " + language_name,
                command=lambda code=language_code: self.set_language(code))

    def update_menu_checkmarks(self):
        # Update the checkmark for Dark Mode
        dark_mode_menu_label = translations[current_language]["dark_mode"]
        if settings['darkMode']:
            dark_mode_label = "✓ " + dark_mode_menu_label
        else:
            dark_mode_label = "    " + dark_mode_menu_label  # Spaces to align with other menu items without a checkmark
        self.settings_menu.entryconfig(dark_mode_menu_label, label=dark_mode_label)

        # Update the checkmarks for languages
        for language_name in languages.keys():
            if languages[language_name] == current_language:
                checked_language_label = "✓ " + language_name
            else:
                checked_language_label = "    " + language_name
            self.language_menu.entryconfig(language_name, label=checked_language_label)

    def create_dark_mode_var(self):
        self.dark_mode_var = tk.BooleanVar(value=settings['darkMode'])
        return self.dark_mode_var

    def toggle_dark_mode(self):
        settings['darkMode'] = self.dark_mode_var.get()
        save_settings()
        self.apply_theme()

    def apply_theme(self):
        if settings['darkMode']:
            self.style.theme_use('alt')  # Assuming 'alt' is your dark theme
            # Apply dark theme colors
            self.style.configure('.', background='#333333', foreground='#FFFFFF')
            self.style.configure('TLabel', background='#333333', foreground='#FFFFFF')
            self.style.map('TButton',
                           background=[('active', '#666666')],  # Darker background on hover
                           foreground=[('active', 'white')])  # Ensure text is black on hover
            self.style.configure('TFrame', background='#333333', borderwidth=0)
            self.console.config(bg='#2b2b2b', fg='#cccccc')
        else:
            self.style.theme_use('clam')  # Assuming 'clam' is your light theme
            # Reset to light theme colors
            self.style.configure('.', background='#f0f0f0', foreground='black')
            self.style.configure('TLabel', background='#f0f0f0', foreground='black')
            self.style.configure('TButton', background='#eeeeee', foreground='black', borderwidth=1)
            self.style.map('TButton',
                           background=[('active', '#dddddd')],  # Lighter background on hover
                           foreground=[('active', 'black')])  # Ensure text is black on hover
            self.style.configure('TFrame', background='#f0f0f0', borderwidth=0)
            self.console.config(bg='white', fg='black')

        # Update text to force refresh without full GUI reinitialization
        self.update_text()

    def set_language(self, code):
        global current_language
        if code in languages.values():
            current_language = code
            save_settings()
            self.initialize_gui()
            self.apply_theme()
            # Update the language menu to correctly display the checkmark next to the selected language
            self.create_menu()  # Recreate the menu to update checkmarks
        else:
            print("Invalid language code:", code)

    def update_text(self):
        """Updates the GUI text based on the current language."""
        self.settings_label.config(
            text=translations[current_language]["current_settings"].format(settings['backupCount'],
                                                                           settings['backupFrequency']))
        self.backup_count_btn.config(text=translations[current_language]["backup_count"])
        self.backup_frequency_btn.config(text=translations[current_language]["backup_frequency"])
        self.launch_backup_btn.config(text=translations[current_language]["launch_backup"])

    def log_message(self, message_id, *args):
        message_template = translations[current_language][message_id]
        message = message_template.format(*args)
        # Format changed to include only time in 12-hour format with AM/PM
        timestamp = datetime.now().strftime("%I:%M:%S %p")
        formatted_message = f"[{timestamp}] {message}\n"
        self.console.config(state='normal')
        self.console.insert(tk.END, formatted_message)
        self.console.config(state='disabled')
        self.console.yview(tk.END)

    def refresh_log_display(self):
        self.console.config(state='normal')
        self.console.delete(1.0, tk.END)
        for message_id, args in self.log_messages:
            message_template = translations[current_language][message_id]
            message = message_template.format(*args)
            timestamp = datetime.now().strftime("%I:%M:%S %p")
            formatted_message = f"[{timestamp}] {message}\n"
            self.console.insert(tk.END, formatted_message)
        self.console.config(state='disabled')
        self.console.yview(tk.END)

    def update_settings_display(self):
        self.settings_label.config(text=get_current_settings())

    def set_backup_count(self):
        while True:
            num_backups = simpledialog.askinteger(translations[current_language]["backup_count"],
                                                  translations[current_language]["backup_count"], parent=self.root)
            if num_backups is None:
                break  # Break the loop if the user closes the dialog
            elif num_backups >= 1:  # Check if num_backups is at least 1
                if num_backups != settings['backupCount']:  # Check if the value has actually changed
                    settings['backupCount'] = num_backups
                    save_settings()
                    self.update_settings_display()
                    self.log_message("backup_count_changed_log", num_backups)  # Log the change
                break
            else:
                messagebox.showwarning("Invalid Input",
                                       "Backup count must be 1 or greater. Please enter a valid number.")

    def set_backup_frequency(self):
        while True:
            frequency = simpledialog.askinteger(translations[current_language]["backup_frequency"],
                                                translations[current_language]["backup_frequency"], parent=self.root)
            if frequency is None:
                break  # Break the loop if the user closes the dialog
            elif frequency >= 1:  # Check if frequency is at least 1
                if frequency != settings['backupFrequency']:  # Check if the value has actually changed
                    settings['backupFrequency'] = frequency
                    save_settings()
                    self.update_settings_display()
                    self.log_message("backup_frequency_changed_log", frequency)  # Log the change
                break
            else:
                messagebox.showwarning("Invalid Input",
                                       "Backup frequency must be 1 or greater. Please enter a valid number.")

    def launch_and_backup(self):
        threading.Thread(target=self._launch_and_backup, daemon=True).start()

    def _launch_and_backup(self):
        self.log_message("launching_smalland_log")  # Use the new log message
        subprocess.Popen(["start", "steam://rungameid/768200"], shell=True)
        # Delay to give the game time to start up
        time.sleep(60)
        self.start_backup_loop()

    def start_backup_loop(self):
        # Run the loop that checks for the game process and manages backups
        while True:
            if is_game_running():
                if not hasattr(self, 'backup_thread') or not self.backup_thread.is_alive():
                    # If the game is running and backup is not in progress, start the backup thread
                    self.log_message("starting_backup_log")  # Log message for starting backup
                    self.backup_thread = threading.Thread(target=self.backup_process, daemon=True)
                    self.backup_thread.start()
            else:
                # If the game is not running and backup is in progress, stop the backup thread
                if hasattr(self, 'backup_thread') and self.backup_thread.is_alive():
                    self.log_message("stopping_backup_log")
                    self.backup_thread.join()  # Wait for the backup process to finish
                    self.log_message("backup_stopped_log")
                    break
            time.sleep(20)  # Check every 20 seconds if the game is running

    def backup_process(self):
        # The actual backup process that will be run in a separate thread
        self.log_message("starting_backup_log")  # Use the new log message
        while is_game_running():
            backup_files()
            self.log_message("backup_complete", settings['backupFrequency'])
            time.sleep(settings['backupFrequency'] * 60)


if __name__ == "__main__":
    load_settings()
    root = tk.Tk()
    app = BackupGUI(root)
    root.mainloop()
