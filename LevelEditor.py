# GUI editor for Plytform levels via tkinter

from tkinter import *


class LevelEditor:
    def __init__(self, master):
        self.master = master
        master.title("Plytform level editor")

        self.master.attributes("-fullscreen", True)

        self.label = Label(master, text="This is our first GUI!")
        self.label.pack(side="right")

        self.greet_button = Button(master, text="Greet", command=self.greet)
        self.greet_button.pack(side="right")

        self.close_button = Button(master, text="Close", command=master.quit)
        self.close_button.pack(side="right")

    def greet(self):
        print("Greetings!")

