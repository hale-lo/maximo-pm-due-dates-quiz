# maximo-pm-due-dates-quiz

## Table of Contents

- [Introduction](#introduction)
- [Design](#design)
    - [GUI Prototype](#gui-prototype)
    - [Functional Requirements](#functional-requirements)
    - [Non-Functional Requirements](#non-functional-requirements)
    - [Tech Stack](#tech-stack)
    - [Code Design](#code-design)
- [Development](#development)
- [Testing](#testing)
- [Documentation](#documentation)
- [Evaluation](#evaluation)

## Introduction

**MACS EU** is a system integration consultancy that helps implement asset management systems, including **IBM Maximo**.

My current role inside MACS EU is as a **data and analytics consultant**. Working here gave me a deeper professional perspective and highlighted a recurring issue with client data in IBM Maximo: mismanagement. This mostly stems from a lack of understanding. That's why I chose this section to review: it has the most depth, bringing together one major Maximo function and three key database tables: Asset, PM and Job Plan.

The mismanagement of data can seem small, but if PMs are not attended to on time, even if due to a small data error, this can make companies non-compliant with their SLAs and lead to fines or even cause damage onsite if an asset isn't checked.

To address this knowledge gap, this Tkinter application lets users learn how Preventive Maintenance work orders are generated and how assets, PMs, and job plans relate. It provides the user with synthetic asset, PM, and Job plan data and asks them to provide the next PM due date and the next job plan frequency, reinforcing the knowledge with repetition through multiple generated questions. 

This quiz is aimed at users who will interact with Preventive Maintenance data through the front end (clients or internal users) or through database and MIF loading. With higher training and knowledge among both our clients and the individuals implementing the data design, MACS EU can support a more logical workflow and communicate requirements for the Preventive Maintenance application more clearly to clients.

## Design
### GUI Prototype

The GUI and user journey were both generated in Figma, as a clickable prototype which covers the full user journey. I generated a Lo-Fi diagram in greyscale, deliberately keeping it sketch-style rather than a full deployment view, to allow for a more deliberate design style to be outlined later.

Figma prototype: [Maximo PM Due Date Quiz - AE2 - Design](https://www.figma.com/community/file/1679898121843546210)

---

#### Figma GUI Walkthrough of User Journey:

##### Landing Frame
![Landing frame prototype](figma/landing.png)

**Figure 1**: Landing frame of the Maximo PM Due Date Quiz Figma prototype.

The landing frame (Figure 1) holds the instructions to the quiz and provides the user with two directions: one to start a new quiz, taking them to the User Details frame (Figure 2), or the other to view the leaderboard (Figure 11).

##### User Details Frame
![User Details frame prototype](figma/player-details.png)

**Figure 2**: User Details frame of the Maximo PM Due Date Quiz Figma prototype.

The User Details frame (Figure 2) holds an open text field for the user to type into. Once they have populated their name, they can click "Continue" to proceed to the first question of the quiz (Figure 4). If the user clicks "Continue" before they input their name, or only inputs whitespace, an error message will display (Figure 3). Otherwise, if they would like to review the instructions again, they can click the "Back" button, taking them to the Landing frame (Figure 1).

##### User Details Frame - Validation Error
![User Details error frame prototype](figma/player-details_validation-error.png)

**Figure 3**: User Details frame with error of the Maximo PM Due Date Quiz Figma prototype.

When a user incorrectly enters their name, an error message will appear below the text box informing them of their mistake and requesting a name. Once a correct name is input, the user can click "Continue" to proceed to the first question of the quiz (Figure 4).

##### Quiz Frame - Question One
![Quiz frame question one prototype](figma/question_first.png)

**Figure 4**: Quiz frame of the Maximo PM Due Date Quiz Figma prototype.

When a user loads the quiz frame it will generate synthetic Asset, PM and Job Plan data for the question, including a Last Completed date, Current PM Counter, and Job Plan Intervals and Frequencies. The user will take their knowledge from the introduction and use it to calculate and input a date value into the "Next Due Date" field, followed by an integer in the "Frequency" dropdown on the left side. There is only one action from this frame, but it has multiple outputs:
1. If there is an incorrect value in either field, an error will occur and display as in Figure 5.
2. If the answer is wrong, it will display below "Incorrect Guesses" on the left side (Figure 6).
3. If the answer is correct, the user will be taken to the summary timeline (Figure 7).

This is replicated ten times over, once for each randomly generated question.

##### Quiz Frame - Question One - Invalid Input
![Quiz frame question one prototype](figma/question_first_validation-error.png)

**Figure 5**: Quiz frame with invalid value of the Maximo PM Due Date Quiz Figma prototype.

When a user inputs an invalid date or frequency, or doesn't populate either, and then clicks the "Submit" button, an error will display below the two input boxes as in Figure 5. Once a correct value is input, it will proceed to either Figure 6 if incorrect, or the Timeline frame (Figure 7) if correct.

##### Quiz Frame - Question One - Incorrect
![Quiz frame question one with incorrect guess prototype](figma/question_first_incorrect.png)

**Figure 6**: Quiz frame with incorrect guess of the Maximo PM Due Date Quiz Figma prototype.

When an input doesn't exactly match the correct date and frequency, a red set of text will appear below the "Incorrect Guesses" section of the frame, informing the user of their prior guess. The user will get three guesses in total; on a correct guess, or the third incorrect guess, they will be taken to the Timeline frame (Figure 7).

##### Quiz Frame - Question One - Correct Timeline
![Quiz frame question ten prototype](figma/question_first_correct.png)

**Figure 7**: Timeline frame of the Maximo PM Due Date Quiz Figma prototype.

Once a user reaches three incorrect guesses, or a single correct guess, they will be taken to the Timeline review frame, which displays the timeline of their PM Job Plans for the following two years. On this frame the text input fields and "Submit" button will be greyed out to stop inputs, and the "Next Question" button will show, which will navigate to another question frame where a new question will be generated (Figure 8).

##### Quiz Frame - Question Ten - Incorrect
![Quiz frame question ten prototype](figma/question_last.png)

**Figure 8**: Quiz frame question ten of the Maximo PM Due Date Quiz Figma prototype.

Question ten is the final question; once again, the user will get three attempts to correctly conclude the Next Due Date and Frequency. Upon their final submit, be it correct or incorrect, they will once again be directed to the Timeline frame (Figure 9).

##### Quiz Frame - Question Ten - Correct Timeline
![Quiz frame question ten prototype](figma/question_last_correct.png)

**Figure 9**: Quiz frame question ten timeline of the Maximo PM Due Date Quiz Figma prototype.

This frame is the only quiz frame that has a different action button: on the final question's timeline frame, the user will see "Next Question" has changed to "View Results", which will take the user to the Result frame instead (Figure 10).

##### Quiz Frame - Result Frame
![Quiz frame question ten prototype](figma/question_quiz-complete.png)

**Figure 10**: Quiz complete frame of the Maximo PM Due Date Quiz Figma prototype.

The Result frame is a simple frame that brings together some of the data stored across the quiz. Each question is worth 0-3 points, depending on whether the user answered correctly and in how many guesses:

        1 Guess = 3 Points
        2 Guesses = 2 Points
        3 Guesses = 1 Point
        Incorrect = 0 Points

This will provide a final score out of 30 for the player, which will be displayed on their Quiz Complete frame (Figure 10).

Following this, the user has three actions:
1. View Leaderboard: Review where they placed in comparison with the other top 10 users (Figure 11).
2. Retake Quiz: This will take them back to the User Details frame (Figure 2), but will keep their current player name.
3. Return Home: This will take the player back to the Landing frame (Figure 1).

##### Quiz Frame - Leaderboard
![Leaderboard](figma/leaderboard.png)

**Figure 11**: Leaderboard frame of the Maximo PM Due Date Quiz Figma prototype.

The Leaderboard frame is a table which displays the stored data of previous users, ranking them from first to last, ordered by score and date played. It is part of a three-level Treeview, in which each table is interactive: clicking an entry in the leaderboard will take the user to the Questions frame (Figure 12). There are two other inputs on this frame. The "Export History" button will provide a download of the leaderboard with game information, whilst the "Back" button will return the user to the Landing frame (Figure 1).

##### Quiz Frame - Leaderboard - Questions
![Leaderboard](figma/leaderboard_question-scores.png)

**Figure 12**: Leaderboard questions frame of the Maximo PM Due Date Quiz Figma prototype.

On the Questions frame, it will display the list of 10 questions which were asked and the score the player received for each question. This is again a Treeview which can be drilled into to review the Timeline frame (Figure 13) for that specific question. There is also a navigation button to go back to the Leaderboard frame (Figure 11).

##### Quiz Frame - Leaderboard - Questions - Timeline
![Leaderboard](figma/leaderboard_question-timeline.png)

**Figure 13**: Leaderboard question timeline frame of the Maximo PM Due Date Quiz Figma prototype.

The final frame of this Treeview displays the timeline of the question selected on the prior frame (Figure 12). It takes the data from a saved CSV and displays it alongside a legend informing the user of which Job Plans and Frequencies the points relate to. The "Back" button on this frame will take the user back to the Questions frame (Figure 12) for the previously selected question.

### Functional Requirements

Table 1: Functional requirements for the Maximo PM Due Date Quiz.
| ID | Requirement |
|---|---|
| FR1 | The application must provide a landing page with options to start a new quiz or view the Leaderboard/History page. |
| FR2 | The application must require a valid name on the Player Details page before a quiz can begin, with visible feedback on invalid input. |
| FR3 | On Retake Quiz, the application must pre-fill the name field with the previous player's name, editable before the new attempt starts. |
| FR4 | The application must let the user submit a next due date and a frequency selected from the question's valid job-plan-sequence frequencies. |
| FR5 | The application must display each question's last-completed date, counter value, and defined intervals and frequencies. |
| FR6 | The application must mark an answer correct only on an exact match of frequency and due date, allow up to three attempts, and complete the question on a correct answer or after three attempts. |
| FR7 | The application must list each incorrect guess (date and frequency), kept visible until the next question begins. |
| FR8 | The application must plot each incorrect guessed date on the timeline, clearing the markers when the next question begins. |
| FR9 | On question completion, the application must reveal the correct frequency, due date, and a calculated PM timeline of further occurrences. |
| FR10 | The application must score each question 3/2/1/0 points by attempt number (first, second, third, or none correct). |
| FR11 | The application must disable inputs on question completion, showing "Next Question" for questions 1-9 and "View Results" after question 10. |
| FR12 | The application must persist the completed attempt (name, score, timeline data) before showing the Results page. |
| FR13 | The Results page must show the player's name and score, with "View Leaderboard", "Retake Quiz", and "Return Home" actions. |
| FR14 | The application must display the top 10 stored attempts by score on the Leaderboard/History page, ties broken by recency. |
| FR15 | The user must be able to select an attempt and a question from the Leaderboard to view its timeline, replacing any timeline shown. |
| FR16 | The application must provide an "Export History" action to export the full attempt summary history to a chosen location. |
| FR17 | The application must provide a "Return Home" action on the Leaderboard/History page. |
| FR18 | The application must validate the due date before evaluating the answer; invalid input shows feedback and does not count as an attempt. |
| FR19 | Each attempt must consist of exactly 10 questions, ending at Results after the tenth. |
| FR20 | The application must catch read, write, and export errors without crashing, showing clear feedback and never falsely indicating success. |

### Non-Functional Requirements

Table 2: Non-Functional requirements for the Maximo PM Due Date Quiz.
| ID | Requirement |
|---|---|
| NFR1 | With up to 100 stored attempts, user actions (answering, advancing, loading the Leaderboard, exporting) must respond within 1 second. |
| NFR2 | At a 1200x800 window size, all primary controls must be usable without resizing, including all Quiz page elements at once. |
| NFR3 | Body text must be at least 11pt with a 4.5:1 contrast ratio, and colour-coded states must also use a non-colour cue. |
| NFR4 | On a clean setup following the README instructions, the application must launch to the Landing page within 3 seconds with no pre-existing CSV files required. |

### Tech Stack

Table 3: Tech stack used in the Maximo PM Due Date Quiz.

| Component | Choice | Why |
|---|---|---|
| Language | Python 3.12 | Brief has a Python 3.9+ minimum, and the newer version let me use structural pattern matching (`match`/`case`) for the scoring logic instead of a chain of if/elif statements. |
| GUI framework | Tkinter, with `ttk` for the themed widgets | Studied in the course, and it needed nothing to host or deploy which benefits MACS EU for more available usage. |
| Data visualisation | Matplotlib | Draws the PM timeline straight inside the Tkinter window, no need to leave the app to see the result. |
| Synthetic data generation | NumPy | Studied in course and generates the randomised asset, PM and job-plan-sequence data behind each question. |
| Persistent storage | CSV | As using a desktop app can meets the storage requirement without a database, and can use mutliple files with key ids for relationships. |
| Automated testing | `unittest` | Comes with Python, no extra dependency for CI to manage, and it's what the course teaches. |
| Continuous integration | GitHub Actions | Runs the test suite on every push and pull from GitHub |
| Prototyping | Figma | Used to build GUI Prototype, evidenced earlier in design. |

### Code Design

The application is built around three classes: `QuizApp`, `Attempt`, and `Question`. I kept this small, following prior advice not to overcomplicate the design. `QuizApp` inherits from `tk.Tk`. Everything else is built through composition instead. `Attempt` and `Question` are plain dataclasses holding data only, with no behaviour of their own. The scoring, timeline, and due-date logic all live separately in `pm_logic.py`, so that logic can be unit tested without needing the GUI. The relationship between the three classes is shown below in Figure 14.

![Class diagram](draw.io/class-diagram.png)

**Figure 14**: Class diagram of the Maximo PM Due Date Quiz, showing QuizApp, Attempt, and Question.

## Development



## Testing



## Documentation



## Evaluation

