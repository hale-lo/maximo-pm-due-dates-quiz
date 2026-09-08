import tkinter as tk

class QuizApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Maximo - PM Due Dates - Quiz")
        self.geometry('1200x800')

if __name__ == "__main__":
    app = QuizApp()
    app.mainloop()