import tkinter as tk
from tkinter import ttk, filedialog
from datetime import datetime
import ctypes
import sys
import uuid

import matplotlib.dates as mdates
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from validators import (
    validate_name,
    validate_date,
    validate_frequency
)

from question_bank import generate_question_bank
from pm_logic import (
    calculate_next_due_date,
    generate_timeline,
    get_base_frequency,
    score_for_attempt
)
from storage import (
    save_attempt,
    load_results,
    load_timeline_entries,
    export_results
)

if sys.platform == "win32":
    ctypes.windll.shcore.SetProcessDpiAwareness(1)

# Fixed categorical order - CVD-safe for adjacent pairs (validated against
# this app's chart background, #F2EFEC). Never cycled or reassigned by rank,
# so a job plan keeps its colour and marker for the life of a question.
JOBPLAN_COLOURS = [
    "#2a78d6",  # blue
    "#eb6834",  # orange
    "#1baf7a",  # aqua
    "#eda100",  # yellow
    "#e87ba4",  # magenta
    "#008300",  # green
    "#4a3aa7",  # violet
    "#e34948",  # red
]

JOBPLAN_MARKERS = ["o", "s", "^", "D", "v", "P", "X", "*"]

class QuizApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Quiz - Maximo - PM Due Dates")
        self.geometry("1440x1024")

        self.title_font = ("Cormorant Garamond", 22, "bold")
        self.instruction_font = ("Cormorant Garamond", 12)
        self.instruction_bold_font = ("Cormorant Garamond", 12, "bold")
        self.button_font = ("Cormorant Garamond", 9, "bold")

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

        self.configure_treeview_style()

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

        self.build_content_header()

    def build_content_header(self):
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

    def configure_treeview_style(self):
        style = ttk.Style(self)

        # "clam" is a pure-Tk theme, unlike Windows' native "vista" theme,
        # which ignores custom Treeview colours - needed for the palette
        # below to actually take effect.
        style.theme_use("clam")

        style.configure(
            "App.Treeview",
            background=self.bg_colour,
            fieldbackground=self.bg_colour,
            foreground=self.accent_colour,
            font=self.instruction_font,
            rowheight=32,
            borderwidth=0,
            relief="flat"
        )

        style.map(
            "App.Treeview",
            background=[("selected", self.active_colour)],
            foreground=[("selected", self.bg_colour)]
        )

        style.configure(
            "App.Treeview.Heading",
            background=self.connected_colour,
            foreground=self.accent_colour,
            font=self.instruction_bold_font,
            relief="flat",
            borderwidth=0
        )

        style.map(
            "App.Treeview.Heading",
            background=[("active", self.connected_colour)]
        )

        style.layout(
            "App.Treeview",
            [
                (
                    "Treeview.treearea",
                    {"sticky": "nswe"}
                )
            ]
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

    def build_name_screen(self, retake=False):
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

        if retake and getattr(self, "player_name", None):
            self.name_entry.insert(0, self.player_name)

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

        question = self.current_question
        self.incorrect_guesses = []

        self.base_frequency = get_base_frequency(question["sequence"])

        next_pm = generate_timeline(
            question["start_counter"],
            question["last_completed"],
            question["sequence"],
            1
        )[0]

        self.correct_jobplan = next_pm["jobplan"]
        self.correct_due_date = next_pm["due_date"]

        self.correct_frequency = question["sequence"][
            self.correct_jobplan
        ]["months"]

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

        self.incorrect_guesses_label = tk.Label(
            self.menu_frame,
            text="Incorrect\nGuesses",
            font=self.instruction_bold_font,
            bg=self.primary_colour,
            fg=self.bg_colour
        )

        self.incorrect_guesses_label.pack(
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
            text=(
                f"Question {self.current_question_index + 1} "
                f"of {len(self.questions)}"
            ),
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
                self.correct_colour,
                correct=True
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
                    self.error_colour,
                    correct=False
                )

    def complete_question(self, message, colour, correct):
        score = score_for_attempt(self.attempts, correct)
        self.total_score += score

        if correct:
            submitted_due_date = self.correct_due_date
            submitted_frequency = self.correct_frequency
        else:
            last_guess = self.incorrect_guesses[-1]
            submitted_due_date = last_guess["date"]
            submitted_frequency = last_guess["frequency"]

        self.question_results.append({
            "question_number": self.current_question_index + 1,
            "asset_name": self.current_question["asset_name"],
            "pm_id": self.current_question["pm_id"],
            "last_completed": self.current_question["last_completed"],
            "start_counter": self.current_question["start_counter"],
            "sequence": self.current_question["sequence"],
            "correct_due_date": self.correct_due_date,
            "correct_frequency": self.correct_frequency,
            "submitted_due_date": submitted_due_date,
            "submitted_frequency": submitted_frequency,
            "attempts": self.attempts,
            "correct": correct,
            "score": score
        })

        self.incorrect_guesses_label.destroy()
        self.incorrect_guesses_frame.destroy()

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

        tk.Label(
            self.menu_frame,
            text="Correct Answer",
            font=self.instruction_bold_font,
            bg=self.primary_colour,
            fg=self.bg_colour
        ).pack(
            pady=(20, 5)
        )

        tk.Label(
            self.menu_frame,
            text=(
                f"{self.correct_due_date.strftime('%d/%m/%Y')}\n"
                f"{self.correct_frequency} months"
            ),
            font=self.instruction_font,
            bg=self.primary_colour,
            fg=self.correct_colour,
            justify="center"
        ).pack()

        self.build_timeline_screen()

        if self.current_question_index == len(self.questions) - 1:
            button_text = "View Results"
        else:
            button_text = "Next Question"

        self.create_menu_button(
            button_text,
            self.next_question,
            pady=(20, 0),
            side="top"
        )

    def build_timeline_screen(self):
        question = self.current_question

        for widget in self.content_frame.winfo_children():
            widget.destroy()

        self.build_content_header()

        tk.Label(
            self.content_frame,
            text=(
                f"Question {self.current_question_index + 1} "
                "- Correct PM Timeline"
            ),
            font=self.title_font,
            bg=self.bg_colour,
            fg=self.accent_colour
        ).pack(
            padx=30,
            pady=(30, 5),
            anchor="w"
        )

        tk.Label(
            self.content_frame,
            text="Scheduled maintenance activity for the next two years.",
            font=self.instruction_font,
            bg=self.bg_colour,
            fg=self.accent_colour
        ).pack(
            padx=30,
            pady=(0, 20),
            anchor="w"
        )

        self.render_timeline_chart(
            self.content_frame,
            question["last_completed"],
            question["start_counter"],
            question["sequence"],
            self.correct_due_date
        )

    def render_timeline_chart(
        self,
        parent_frame,
        last_completed,
        start_counter,
        sequence,
        correct_due_date
    ):
        base_frequency = get_base_frequency(sequence)

        timeline_start = correct_due_date

        timeline_end = calculate_next_due_date(
            timeline_start,
            24
        )

        timeline_span = (
            24 // base_frequency
        ) + 1

        timeline = generate_timeline(
            start_counter,
            last_completed,
            sequence,
            timeline_span
        )

        timeline_dates = [
            item["due_date"]
            for item in timeline
        ]

        jobplans_by_frequency = sorted(
            sequence.items(),
            key=lambda entry: entry[1]["months"]
        )

        jobplan_styles = {
            jobplan: {
                "colour": JOBPLAN_COLOURS[index % len(JOBPLAN_COLOURS)],
                "marker": JOBPLAN_MARKERS[index % len(JOBPLAN_MARKERS)]
            }
            for index, (jobplan, details) in enumerate(jobplans_by_frequency)
        }

        figure = Figure(
            figsize=(10, 5),
            dpi=100,
            facecolor=self.bg_colour
        )

        axis = figure.add_subplot(111)

        axis.set_facecolor(self.bg_colour)

        if timeline_dates:
            axis.hlines(
                y=0,
                xmin=timeline_start,
                xmax=timeline_end,
                color=self.connected_colour,
                linewidth=3,
                zorder=1
            )

            axis.vlines(
                timeline_dates,
                ymin=-0.08,
                ymax=0.08,
                color=self.connected_colour,
                linewidth=2,
                zorder=2
            )

            for jobplan, details in jobplans_by_frequency:
                style = jobplan_styles[jobplan]

                jobplan_dates = [
                    item["due_date"]
                    for item in timeline
                    if item["jobplan"] == jobplan
                ]

                if not jobplan_dates:
                    continue

                axis.scatter(
                    jobplan_dates,
                    [0] * len(jobplan_dates),
                    color=style["colour"],
                    marker=style["marker"],
                    s=90,
                    zorder=3,
                    label=f"{jobplan} ({details['months']} months)"
                )

            legend_rows = 3

            legend_columns = (
                len(jobplans_by_frequency) + legend_rows - 1
            ) // legend_rows

            axis.legend(
                loc="upper center",
                ncol=legend_columns,
                frameon=False,
                fontsize=9,
                labelcolor=self.accent_colour
            )

        axis.xaxis.set_major_locator(
            mdates.MonthLocator(interval=3)
        )

        axis.xaxis.set_major_formatter(
            mdates.DateFormatter("%b\n%Y")
        )

        axis.set_yticks([])

        axis.set_ylim(
            -0.2,
            1
        )

        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)
        axis.spines["left"].set_visible(False)
        axis.spines["bottom"].set_visible(False)

        axis.tick_params(
            axis="x",
            colors=self.accent_colour,
            length=0
        )

        figure.subplots_adjust(
            left=0.05,
            right=0.97,
            top=0.82,
            bottom=0.18
        )

        canvas = FigureCanvasTkAgg(
            figure,
            master=parent_frame
        )

        canvas.draw()

        canvas_widget = canvas.get_tk_widget()

        canvas_widget.configure(
            bg=self.bg_colour,
            highlightthickness=0,
            borderwidth=0
        )

        canvas_widget.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=(0, 30)
        )

        return canvas

    def next_question(self):
        if self.current_question_index < len(self.questions) - 1:
            self.current_question_index += 1
            self.current_question = self.questions[self.current_question_index]

            self.build_quiz_screen()
        else:
            saved, message = save_attempt(
                self.player_name,
                self.game_id,
                self.attempt_started,
                self.question_results,
                self.total_score
            )

            if saved:
                self.build_results_screen()
            else:
                self.answer_error_label.config(
                    text=f"Could not save results:\n{message}",
                    fg=self.error_colour
                )

    def build_results_screen(self):
        self.reset_screen()

        self.create_menu_button(
            "View Leaderboard",
            self.build_leaderboard_screen,
            pady=(30, 0)
        )

        self.create_menu_button(
            "Retake Quiz",
            lambda: self.build_name_screen(retake=True)
        )

        self.create_menu_button(
            "Return Home",
            self.build_landing_screen
        )

        tk.Label(
            self.content_frame,
            text="Quiz Complete",
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
            text=f"Player: {self.player_name}",
            font=self.instruction_bold_font,
            bg=self.bg_colour,
            fg=self.accent_colour
        ).pack(
            padx=30,
            pady=(10, 5),
            anchor="w"
        )

        tk.Label(
            self.content_frame,
            text=f"Final Score: {self.total_score} / 30",
            font=self.instruction_bold_font,
            bg=self.bg_colour,
            fg=self.accent_colour
        ).pack(
            padx=30,
            pady=(0, 20),
            anchor="w"
        )

    def build_leaderboard_screen(self):
        self.reset_screen()

        self.create_menu_button(
            "Back",
            self.build_landing_screen,
            pady=(0, 30),
            side="bottom"
        )

        tk.Label(
            self.content_frame,
            text="Leaderboard",
            font=self.title_font,
            bg=self.bg_colour,
            fg=self.accent_colour
        ).pack(
            padx=30,
            pady=(30, 10),
            anchor="w"
        )

        results = load_results()

        if not results:
            tk.Label(
                self.content_frame,
                text="No attempts recorded yet.",
                font=self.instruction_font,
                bg=self.bg_colour,
                fg=self.accent_colour
            ).pack(
                padx=30,
                pady=(10, 0),
                anchor="w"
            )

            return

        self.create_menu_button(
            "Export History",
            self.export_leaderboard_history,
            pady=(30, 0)
        )

        tk.Label(
            self.content_frame,
            text="Select an attempt to review its questions.",
            font=self.instruction_font,
            bg=self.bg_colour,
            fg=self.accent_colour
        ).pack(
            padx=30,
            pady=(0, 10),
            anchor="w"
        )

        self.export_status_label = tk.Label(
            self.content_frame,
            text="",
            font=self.instruction_font,
            bg=self.bg_colour,
            fg=self.correct_colour,
            wraplength=900,
            justify="left",
            anchor="w"
        )

        self.export_status_label.pack(
            padx=30,
            pady=(0, 10),
            anchor="w"
        )

        ranked = sorted(
            results,
            key=lambda result: (
                -result["total_score"],
                -result["attempt_started"].timestamp()
            )
        )[:10]

        rows = [
            (
                (
                    str(index),
                    result["player_name"],
                    f"{result['total_score']} / 30",
                    result["attempt_started"].strftime("%d/%m/%Y %H:%M")
                ),
                result
            )
            for index, result in enumerate(ranked, start=1)
        ]

        self.build_row_table(
            self.content_frame,
            (
                ("Rank", 6, "center"),
                ("Player", 28, "w"),
                ("Score", 10, "center"),
                ("Date", 20, "center")
            ),
            rows,
            self.build_leaderboard_attempt_screen
        )

    def export_leaderboard_history(self):
        destination_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )

        if not destination_path:
            return

        exported, message = export_results(destination_path)

        if exported:
            self.export_status_label.config(
                text=f"Export successful: saved to {destination_path}",
                fg=self.correct_colour
            )
        else:
            self.export_status_label.config(
                text=f"Export failed: {message}",
                fg=self.error_colour
            )

    def build_row_table(self, parent_frame, columns, rows, on_row_click):
        table_frame = tk.Frame(
            parent_frame,
            bg=self.bg_colour,
            highlightbackground=self.connected_colour,
            highlightthickness=1,
            padx=15,
            pady=15
        )

        table_frame.pack(
            padx=30,
            pady=(0, 20),
            anchor="w"
        )

        column_ids = [
            str(index)
            for index in range(len(columns))
        ]

        tree = ttk.Treeview(
            table_frame,
            columns=column_ids,
            show="headings",
            height=min(len(rows), 10),
            style="App.Treeview"
        )

        for column_id, (heading, width, anchor) in zip(column_ids, columns):
            tree.heading(column_id, text=heading)

            tree.column(
                column_id,
                width=max(60, width * 11),
                anchor=anchor
            )

        row_lookup = {}

        for row_index, (row_values, row_data) in enumerate(rows):
            iid = str(row_index)

            row_lookup[iid] = row_data

            tree.insert(
                "",
                "end",
                iid=iid,
                values=row_values
            )

        tree.pack(
            fill="both",
            expand=True
        )

        tree.bind(
            "<<TreeviewSelect>>",
            lambda event: self.handle_row_table_select(
                event,
                row_lookup,
                on_row_click
            )
        )

    def handle_row_table_select(self, event, row_lookup, on_row_click):
        selection = event.widget.selection()

        if not selection:
            return

        on_row_click(row_lookup[selection[0]])

    def build_leaderboard_attempt_screen(self, result):
        self.reset_screen()

        self.create_menu_button(
            "Back",
            self.build_leaderboard_screen,
            pady=(0, 30),
            side="bottom"
        )

        tk.Label(
            self.content_frame,
            text=f"{result['player_name']} - {result['total_score']} / 30",
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
            text="Select a question to view its timeline.",
            font=self.instruction_font,
            bg=self.bg_colour,
            fg=self.accent_colour
        ).pack(
            padx=30,
            pady=(0, 10),
            anchor="w"
        )

        entries = [
            entry
            for entry in load_timeline_entries()
            if entry["game_id"] == result["game_id"]
        ]

        entries.sort(key=lambda entry: entry["question_number"])

        rows = [
            (
                (
                    str(entry["question_number"]),
                    entry["asset_name"],
                    "Correct" if entry["correct"] else "Incorrect",
                    str(entry["score"])
                ),
                entry
            )
            for entry in entries
        ]

        self.build_row_table(
            self.content_frame,
            (
                ("Q#", 6, "center"),
                ("Asset", 28, "w"),
                ("Result", 14, "center"),
                ("Score", 10, "center")
            ),
            rows,
            lambda entry: self.build_leaderboard_question_screen(result, entry)
        )

    def build_leaderboard_question_screen(self, result, entry):
        self.reset_screen()

        self.create_menu_button(
            "Back",
            lambda: self.build_leaderboard_attempt_screen(result),
            pady=(0, 30),
            side="bottom"
        )

        tk.Label(
            self.content_frame,
            text=(
                f"{result['player_name']} - Question "
                f"{entry['question_number']} - Correct PM Timeline"
            ),
            font=self.title_font,
            bg=self.bg_colour,
            fg=self.accent_colour
        ).pack(
            padx=30,
            pady=(30, 5),
            anchor="w"
        )

        tk.Label(
            self.content_frame,
            text=f"Asset: {entry['asset_name']}    PM: {entry['pm_id']}",
            font=self.instruction_font,
            bg=self.bg_colour,
            fg=self.accent_colour
        ).pack(
            padx=30,
            pady=(0, 20),
            anchor="w"
        )

        self.render_timeline_chart(
            self.content_frame,
            entry["last_completed"],
            entry["start_counter"],
            entry["sequence"],
            entry["correct_due_date"]
        )

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

        self.total_score = 0
        self.question_results = []
        self.attempt_started = datetime.now()
        self.game_id = uuid.uuid4().hex

        self.current_question_index = 0
        self.current_question = self.questions[0]

        self.build_quiz_screen()

if __name__ == "__main__":
    app = QuizApp()
    app.mainloop()