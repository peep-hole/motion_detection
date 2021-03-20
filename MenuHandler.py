from tkinter import *
from tkinter import Menu
from PIL import ImageTk, Image
from functools import partial

lmain=None 
selected = None 
def setUpMenu():
    def setMode():
        print("nowy tryb")
        #mode = newMode
    global lmain
    global selected

    root = Tk()
    root.bind("<Button-1>",setMode)
    app = Frame(root, bg="white")
    app.grid()
    lmain = Label(app)
    lmain.grid(column=0,row=1)
    lmenu=Label(app)
    lmenu.grid(column=0,row=0)
    selected=IntVar()
    modes = ["None","Gray","Blurred","Treshold","Frame Difference"]
    for i in range(4):
        r = Radiobutton(lmenu,text=modes[i],value=i,variable=selected)
        r.grid(column=i,row=0)
    return root
def getLabel():
    return lmain
def getStatus():
    return selected.get()