import tkinter as tk
from tkinter import ttk
import ctypes

from validators import (
    validate_name,
    validate_date,
    validate_frequency
)

ctypes.windll.shcore.SetProcessDpiAwareness(1)

class QuizApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Quiz - Maximo - PM Due Dates")
        self.geometry("1440x1024")

        self.title_font = ("Segoe UI", 22, "bold")
        self.instruction_font = ("Segoe UI", 12)
        self.instruction_bold_font = ("Segoe UI", 12, "bold")
        self.button_font = ("Segoe UI", 9, "bold")

        self.bg_colour = "#F2EFEC"
        self.connected_colour = "#D1C6BD"
        self.primary_colour = "#B09D8E"
        self.accent_colour = "#2A231D"
        self.active_colour = "#3B3129"
        self.correct_colour = "#1E573F"
        self.error_colour = "#5D2222"

        self.resizable(False, False)
        self.configure(bg=self.bg_colour)

        hwnd = ctypes.windll.user32.GetParent(self.winfo_id())

        value = ctypes.c_int(1)

        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd,
            20,
            ctypes.byref(value),
            ctypes.sizeof(value)
        )

        self.build_landing_screen()

    def empty_screen(self):
        for widget in self.winfo_children():
            widget.destroy()


    def reset_screen(self):
        self.empty_screen()

        self.configure(bg=self.bg_colour)

        self.menu_frame = tk.Frame(
            self,
            bg=self.primary_colour,
            width=200
        )

        self.menu_frame.pack(
            side="left",
            padx=(30, 0),
            pady=(30, 0),
            fill="y"
        )

        self.menu_frame.pack_propagate(False)

        tk.Label(
            self.menu_frame,
            text="MAXIMO",
            font=self.title_font,
            bg=self.primary_colour,
            fg=self.bg_colour
        ).pack(
            pady=(30, 0)
        )

        self.content_frame = tk.Frame(
            self,
            bg=self.bg_colour
        )

        self.content_frame.pack(
            side="left",
            fill="both",
            expand=True
        )

        tk.Label(
            self.content_frame,
            text=": PM Due Dates",
            font=self.title_font,
            bg=self.connected_colour,
            fg=self.accent_colour,
            anchor="w"
        ).pack(
            fill="x",
            pady=(60, 0)
        )

    def create_menu_button(self, text, command, pady=(10, 0), side="top"):
        tk.Button(
            self.menu_frame,
            text=text,
            font=self.button_font,
            bg=self.accent_colour,
            fg=self.bg_colour,
            activebackground=self.active_colour,
            relief="flat",
            bd=0,
            highlightthickness=0,
            width=20,
            height=2,
            cursor="hand2",
            command=command
        ).pack(
            side=side,
            pady=pady
        )

    def build_landing_screen(self):
        self.reset_screen()

        self.create_menu_button(
            "Start Quiz",
            self.build_name_screen,
            pady=(30, 0)
        )

        self.create_menu_button(
            "View Leaderboard",
            self.build_leaderboard_screen
        )

        tk.Label(
            self.content_frame,
            text="Instructions",
            font=self.title_font,
            bg=self.bg_colour,
            fg=self.accent_colour
        ).pack(
            padx=30,
            pady=(30, 10),
            anchor="w"
        )

        tk.Label(
            self.content_frame,
            text=(
                "You will be shown a series of ten questions. "
                "For each question, you must review the last completed date, "
                "job plans and frequencies. Use this information to determine "
                "when the next maintenance activity is due and which job plan "
                "should be applied.\n\n"
                "There are two equations you need to know:\n"
            ),
            font=self.instruction_font,
            bg=self.bg_colour,
            fg=self.accent_colour,
            wraplength=900,
            justify="left",
            anchor="w"
        ).pack(
            padx=30,
            pady=(5, 0),
            anchor="w"
        )

        tk.Label(
            self.content_frame,
            text=(
                "Next frequency:\n"
                "   Use the largest interval where counter % interval = 0.\n\n"
                "Next due date:\n"
                "   Last completed date + frequency (calendar months)"
            ),
            font=self.instruction_bold_font,
            bg=self.bg_colour,
            fg=self.error_colour,
            wraplength=900,
            justify="left",
            anchor="w"
        ).pack(
            padx=30,
            pady=(5, 0),
            anchor="w"
        )

    def build_name_screen(self):
        self.reset_screen()

        self.create_menu_button(
            "Continue",
            self.start_quiz,
            pady=(30, 0),
            side="top"
        )

        self.create_menu_button(
            "Back",
            self.build_landing_screen,
            pady=(0, 30),
            side="bottom"
        )

        tk.Label(
            self.content_frame,
            text="Enter Your Name",
            font=self.title_font,
            bg=self.bg_colour,
            fg=self.accent_colour
        ).pack(
            padx=30,
            pady=(30, 10),
            anchor="w"
        )

        tk.Label(
            self.content_frame,
            text="Please enter your name before starting the quiz.",
            font=self.instruction_font,
            bg=self.bg_colour,
            fg=self.accent_colour
        ).pack(
            padx=30,
            pady=(0, 20),
            anchor="w"
        )

        self.name_entry = tk.Entry(
            self.content_frame,
            font=self.instruction_font,
            width=30
        )

        self.name_entry.pack(
            padx=30,
            pady=(0, 20),
            anchor="w"
        )

        self.error_label = tk.Label(
        self.content_frame,
        text="",
        font=self.instruction_font,
        bg=self.bg_colour,
        fg=self.error_colour
        )

        self.error_label.pack(
            padx=30,
            anchor="w"
        )

    def build_quiz_screen(self):
            self.reset_screen()

    def build_leaderboard_screen(self):
        self.reset_screen()

    def start_quiz(self):
        name = self.name_entry.get()

        valid, message = validate_name(name)

        if not valid:
            self.error_label.config(text=message)
            return

        self.player_name = name

        self.build_quiz_screen()

if __name__ == "__main__":
    app = QuizApp()
    app.mainloop()