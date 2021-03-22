from tkinter import *
from tkinter import Menu
from PIL import ImageTk, Image
from functools import partial

lmain=None 
selected = None 
topLeft=None
bottomRight=None
def setUpMenu():
    def handleClick(event):
        global topLeft
        global bottomRight
        if(topLeft==None):
            topLeft=[event.x,event.y]
        elif(bottomRight==None):
            bottomRight=[event.x,event.y]
        else:
            topLeft=None
            bottomRight=None
    global lmain
    global selected

    root = Tk()
    root.title("Motion detector")
    root.bind("<Button-1>",handleClick) #Kliknięcie myszy
    app = Frame(root, bg="white")
    app.grid()
    lmain = Label(app)
    lmain.grid(column=0,row=1)
    lmenu=Label(app)
    lmenu.grid(column=0,row=0)
    selected=IntVar()
    modes = ["None","Gray","Blurred","Treshold","Frame Difference"]
    for i in range(5):
        r = Radiobutton(lmenu,text=modes[i],value=i,variable=selected)
        r.grid(column=i,row=0)
    return root
def getLabel():
    return lmain
def getStatus():
    return selected.get()
def getMaskCoords():
    if(topLeft==None or bottomRight == None):
        return None
    else:
        return [topLeft[0],topLeft[1],bottomRight[0],bottomRight[1]]