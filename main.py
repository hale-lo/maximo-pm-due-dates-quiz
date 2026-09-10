import tkinter as tk
from tkinter import ttk
from datetime import datetime
import ctypes
import sys

from validators import (
    validate_name,
    validate_date,
    validate_frequency
)

from question_bank import generate_question_bank
from pm_logic import (
    resolve_job_plan,
    calculate_next_due_date
)

if sys.platform == "win32":
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

        if sys.platform == "win32":
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

    def create_menu_button(
        self,
        text,
        command,
        pady=(10, 0),
        side="top"
    ):
        button = tk.Button(
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
        )

        button.pack(
            side=side,
            pady=pady
        )

        return button

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
            anchor="center"
        )

    def build_quiz_screen(self):
        self.reset_screen()

        question = self.current_question
        self.incorrect_guesses = []
        next_counter = question["start_counter"] + 1

        self.correct_jobplan = resolve_job_plan(
            next_counter,
            question["sequence"]
        )

        self.correct_frequency = question["sequence"][
            self.correct_jobplan
        ]["months"]

        base_frequency = min(
            details["months"]
            for details in question["sequence"].values()
        )

        self.correct_due_date = calculate_next_due_date(
            question["last_completed"],
            base_frequency
        )

        self.attempts = 0

        tk.Label(
            self.menu_frame,
            text="Your Answer",
            font=self.instruction_bold_font,
            bg=self.primary_colour,
            fg=self.bg_colour
        ).pack(
            padx=15,
            pady=(30, 15),
            anchor="w"
        )

        tk.Label(
            self.menu_frame,
            text="Next due date:",
            font=self.button_font,
            bg=self.primary_colour,
            fg=self.bg_colour
        ).pack(
            padx=15,
            anchor="w"
        )

        self.date_entry = tk.Entry(
            self.menu_frame,
            font=self.button_font,
            width=20
        )

        self.date_entry.pack(
            padx=15,
            pady=(5, 15),
            anchor="w"
        )

        tk.Label(
            self.menu_frame,
            text="Next frequency:",
            font=self.button_font,
            bg=self.primary_colour,
            fg=self.bg_colour
        ).pack(
            padx=15,
            anchor="w"
        )

        self.valid_frequencies = sorted(
            details["months"]
            for details in question["sequence"].values()
        )

        self.frequency_var = tk.StringVar()

        self.frequency_dropdown = ttk.Combobox(
            self.menu_frame,
            textvariable=self.frequency_var,
            values=self.valid_frequencies,
            font=self.button_font,
            width=17,
            state="readonly"
        )

        self.frequency_dropdown.pack(
            padx=15,
            pady=(5, 10),
            anchor="w"
        )

        self.answer_error_label = tk.Label(
            self.menu_frame,
            text="",
            font=self.button_font,
            bg=self.primary_colour,
            fg=self.error_colour,
            wraplength=165,
            justify="center"
        )

        self.answer_error_label.pack(
            anchor="center"
        )

        self.submit_button = self.create_menu_button(
            "Submit Answer",
            self.submit_answer,
            pady=(5, 20),
            side="top"
        )

        tk.Label(
            self.menu_frame,
            text="Incorrect\nGuesses",
            font=self.instruction_bold_font,
            bg=self.primary_colour,
            fg=self.bg_colour
        ).pack(
            padx=15,
            pady=(5, 5),
            anchor="center"
        )

        self.incorrect_guesses_frame = tk.Frame(
            self.menu_frame,
            bg=self.primary_colour
        )

        self.incorrect_guesses_frame.pack(
            padx=15,
            fill="x",
            anchor="w"
        )

        tk.Label(
            self.content_frame,
            text=f"Question {self.current_question_index + 1} of 10",
            font=self.title_font,
            bg=self.bg_colour,
            fg=self.accent_colour
        ).pack(
            padx=30,
            pady=(30, 20),
            anchor="w"
        )

        question_frame = tk.Frame(
            self.content_frame,
            bg=self.bg_colour
        )

        question_frame.pack(
            fill="x",
            padx=30,
            pady=(0, 20)
        )

        question_frame.grid_columnconfigure(0, weight=1)
        question_frame.grid_columnconfigure(1, weight=1)

        asset_frame = tk.Frame(
            question_frame,
            bg=self.bg_colour,
            highlightbackground=self.connected_colour,
            highlightthickness=1,
            padx=20,
            pady=20
        )

        asset_frame.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 10)
        )

        tk.Label(
            asset_frame,
            text="Asset Data",
            font=self.instruction_bold_font,
            bg=self.bg_colour,
            fg=self.accent_colour
        ).pack(
            anchor="w",
            pady=(0, 15)
        )

        tk.Label(
            asset_frame,
            text=f"Asset: {question['asset_name']}",
            font=self.instruction_bold_font,
            bg=self.bg_colour,
            fg=self.accent_colour
        ).pack(
            anchor="w",
            pady=(0, 8)
        )

        tk.Label(
            asset_frame,
            text=f"PM: {question['pm_id']}",
            font=self.instruction_font,
            bg=self.bg_colour,
            fg=self.accent_colour
        ).pack(
            anchor="w",
            pady=(0, 8)
        )

        tk.Label(
            asset_frame,
            text=(
                "Last Completed: "
                f"{question['last_completed'].strftime('%d/%m/%Y')}"
            ),
            font=self.instruction_font,
            bg=self.bg_colour,
            fg=self.accent_colour
        ).pack(
            anchor="w",
            pady=(0, 8)
        )

        tk.Label(
            asset_frame,
            text=f"Current Counter: {question['start_counter']}",
            font=self.instruction_font,
            bg=self.bg_colour,
            fg=self.accent_colour
        ).pack(
            anchor="w"
        )

        jobplan_frame = tk.Frame(
            question_frame,
            bg=self.bg_colour,
            highlightbackground=self.connected_colour,
            highlightthickness=1,
            padx=20,
            pady=20
        )

        jobplan_frame.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(10, 0)
        )

        tk.Label(
            jobplan_frame,
            text="Job Plan Sequence",
            font=self.instruction_bold_font,
            bg=self.bg_colour,
            fg=self.accent_colour
        ).pack(
            anchor="w",
            pady=(0, 15)
        )

        for jobplan, details in question["sequence"].items():
            tk.Label(
                jobplan_frame,
                text=(
                    f"{jobplan}\n"
                    f"Interval: {details['interval']}    "
                    f"Frequency: {details['months']} months"
                ),
                font=self.instruction_font,
                bg=self.bg_colour,
                fg=self.accent_colour,
                justify="left"
            ).pack(
                anchor="w",
                pady=(0, 12)
            )

    def submit_answer(self):
        due_date_text = self.date_entry.get()
        frequency_text = self.frequency_var.get()

        valid, message = validate_date(due_date_text)

        if not valid:
            self.answer_error_label.config(text=message)
            return

        valid, message = validate_frequency(
            frequency_text,
            self.valid_frequencies
        )

        if not valid:
            self.answer_error_label.config(text=message)
            return

        self.answer_error_label.config(text="")

        submitted_date = datetime.strptime(
            due_date_text,
            "%d/%m/%Y"
        ).date()

        frequency = int(frequency_text)

        self.attempts += 1

        correct = (
            submitted_date == self.correct_due_date
            and frequency == self.correct_frequency
        )

        if correct:
            print(f"Correct on attempt {self.attempts}")

            self.complete_question(
                "Correct!",
                self.correct_colour
            )

        else:
            print(f"Incorrect on attempt {self.attempts}")

            self.incorrect_guesses.append({
                "date": submitted_date,
                "frequency": frequency
            })

            tk.Label(
                self.incorrect_guesses_frame,
                text=(
                    f"Attempt {self.attempts}:"
                ),
                font=self.instruction_bold_font,
                bg=self.primary_colour,
                fg=self.error_colour
            ).pack(
                anchor="center",
                pady=(2, 0)
            )

            tk.Label(
                self.incorrect_guesses_frame,
                text=(
                    f"{submitted_date.strftime('%d/%m/%Y')}\n"
                    f"{frequency} months"
                ),
                font=self.instruction_font,
                bg=self.primary_colour,
                fg=self.error_colour
            ).pack(
                anchor="center"
            )

            if self.attempts >= 3:
                self.complete_question(
                    "No attempts\nremaining.",
                    self.error_colour
                )

    def complete_question(self, message, colour):
        self.date_entry.config(
            state="disabled"
        )

        self.frequency_dropdown.config(
            state="disabled"
        )

        self.submit_button.config(
            state="disabled"
        )

        self.answer_error_label.config(
            text=message,
            fg=colour
        )

        if self.current_question_index == len(self.questions) - 1:
            button_text = "View Results"
        else:
            button_text = "Next Question"

        self.create_menu_button(
            button_text,
            self.next_question,
            pady=(10, 0),
            side="top"
        )

    def next_question(self):
        print("Next question")

    def build_leaderboard_screen(self):
        self.reset_screen()

    def start_quiz(self):
        name = self.name_entry.get()

        valid, message = validate_name(name)

        if not valid:
            self.error_label.config(text=message)
            return

        self.player_name = name

        self.questions = generate_question_bank(
            number_of_questions=10
        )

        self.current_question_index = 0
        self.current_question = self.questions[0]

        self.build_quiz_screen()

if __name__ == "__main__":
    app = QuizApp()
    app.mainloop()