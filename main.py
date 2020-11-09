import sys
import tkinter.filedialog
import tkinter as tk
from PIL import ImageTk, Image
import os
VERSION = "0.1"
DEFAULT_IMAGE_FILENAME = "load_dir.png"
#http://effbot.org/tkinterbook/tkinter-events-and-bindings.htm
#https://gist.github.com/brikeats/53664f4534c455f5d969
with open("classes.txt") as classes_file:
    CLASSES = classes_file.read().splitlines()
COLORS = ["yellow", "red", "green", "orange", "gray", "pink", "purple", "tan", "olive"]
MIN_WIDTH = 10
MIN_HEIGHT = 10
SELECTED_CLASS = 0
selected_class_indexes = [i for i in range(len(CLASSES))]
selected_class_indexes_as_strs = [str(index + 1) for index in selected_class_indexes] #used for easy indexing
"""
#Get Directory to explode from user dialogue================
print("requesting video directory to annotate..")
root = tk.Tk()
root.withdraw()
file_path = tk.filedialog.askdirectory()
print("selected...", file_path)


root = tk.Tk()

def key(event):
    print("pressed", event.char)
    if event.char in selected_class_indexes_as_strs:
        selected_class = int(event.char) - 1
        print("Updating class to ", selected_class, classes[selected_class])

def callback(event):
    #frame.focus_set()
    print("clicked at", event.x, event.y)

#top = tk.Toplevel()
# Code to add widgets will go here...


#frame = top.Frame(top, width=100, height=100)
#frame.pack()
"""


class ImageCanvas(tk.Canvas):
    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs)
        self.width = 1
        self.height = 1
        self.horizontal_dash_line = None
        self.vertical_dash_line = None
        self.bind("<Button-1>", self.clicked)
        self.bind("<ButtonRelease-1>", self.click_release)
        self.bind("<Motion>", self.move_mouse)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Configure>", self.on_resize)
        self.new_label_clicked_xy = None
        self.new_label_released_xy = None
        self.new_label_temporary_box = None
        self.new_label_temporary_text = None
        self.editing = False

        #TODO: Why is default image not loading?
        self.image_filename = DEFAULT_IMAGE_FILENAME
        self.resizeable_image = Image.open(self.image_filename)
        self.resizeable_image = self.resizeable_image.resize((1200, 800), Image.ANTIALIAS)
        self.resized_photoimage = ImageTk.PhotoImage(self.resizeable_image)
        self.image_on_canvas = self.create_image(0,0, anchor=tk.NW, image=self.resized_photoimage, tag="all")

        self.addtag_all("all")
        self.update()
        print(self.image_on_canvas)

        self.labels = [] #[(bb, class, bb_id, text_id)]

    def on_resize(self, event):
        print("on_resize", event.width, event.height)
        self.width = event.width
        self.height = event.height
        self.load_image(self.image_filename)

    def save_labels(self, image_filename, labels):

        label_filename = os.path.splitext(image_filename)[0] + ".txt"
        print("saved labels", image_filename, label_filename, labels)
        with open(label_filename, "w") as f:
            yolo_formatted_labels = [[str(CLASSES.index(class_name)),  #Class Name
                                       str(bb[0]),  #x
                                       str(bb[1]),  #y
                                       str(bb[2] - bb[0]), #width
                                       str(bb[3] - bb[1])] #height
                                    for bb, class_name, bb_id, text_id in labels ]
            f.write("\n".join([" ".join(yolo_label) for yolo_label in yolo_formatted_labels]))
    def clear_labels(self):
        for label in self.labels:
            bb, class_name, bb_id, text_id = label
            self.delete(bb_id)
            self.delete(text_id)
        self.labels = []

    def delete_label_file(self):
        self.clear_labels()
        label_filename = os.path.splitext(self.image_filename)[0] + ".txt"
        if os.path.exists(label_filename):
            os.remove(label_filename)
    def load_labels(self, image_filename, existing_labels):
        #check if label file exists
        label_filename = os.path.splitext(image_filename)[0] + ".txt"
        if os.path.exists(label_filename):
            print("Loading existing labels for", image_filename)
            self.clear_labels()
            #draw labels from file onto canvas
            with open(label_filename, "r") as yolo_label_file:
                yolo_labels = yolo_label_file.read().splitlines()
                for yolo_label in yolo_labels:
                    class_index, x, y, width, height = yolo_label.split(" ")
                    class_index = int(class_index)
                    x, y, width, height = float(x), float(y), float(width), float(height)
                    class_name = CLASSES[class_index]
                    bb = [x,y, x+width, y+height]
                    bb_id = self.create_rectangle(bb[0] * self.winfo_width(),bb[1] * self.winfo_height() ,bb[2] * self.winfo_width(),bb[3] * self.winfo_height(), fill="", outline=COLORS[class_index])
                    new_label_text_id = self.create_text(x * self.winfo_width(), (y * self.winfo_height()) - 5, fill=COLORS[class_index], text=class_name)
                    self.labels.append([bb,class_name,bb_id, new_label_text_id])
        print("labels:")
        for label in self.labels:
            print(label)

    def load_image(self,filename):
        print(filename)
        if self.image_filename != DEFAULT_IMAGE_FILENAME:
            if len(self.labels) > 0:
                print("Saving Labels", self.image_filename)
                self.save_labels(self.image_filename, self.labels)
            else:
                print("removing labels", self.image_filename)
                self.delete_label_file()
        self.load_labels(filename, self.labels)
        self.image_filename = filename
        self.resizeable_image = Image.open(self.image_filename).resize((self.width, self.height), Image.ANTIALIAS)
        self.resized_photoimage = ImageTk.PhotoImage(self.resizeable_image)
        self.itemconfig(self.image_on_canvas, image=self.resized_photoimage)





    def cancel(self): #Captured by Root bind_all method
        print("Cancelled Executed...")
        self.new_label_clicked_xy = None
        if self.new_label_temporary_box:
            self.delete(self.new_label_temporary_box)
            self.delete(self.new_label_temporary_text)
    def update_crosshair(self,event):
        if self.horizontal_dash_line:
            self.delete(self.horizontal_dash_line)
        if self.vertical_dash_line:
            self.delete(self.vertical_dash_line)
        cross_hair_color = "red" if self.editing else "black"

        self.horizontal_dash_line = self.create_line(0, event.y, self.winfo_width(), event.y, fill=cross_hair_color, dash=(5, 2))
        self.vertical_dash_line = self.create_line(event.x, 0, event.x, self.winfo_height(), fill=cross_hair_color, dash=(5, 2))
    def move_mouse(self, event):
        self.update_crosshair(event)
        if self.image_filename == DEFAULT_IMAGE_FILENAME:
            return
        if self.new_label_clicked_xy != None:
            if self.new_label_temporary_box != None:
                self.delete(self.new_label_temporary_box)
                self.delete(self.new_label_temporary_text)
            x1, y1 = self.new_label_clicked_xy
            x2 = min(max(event.x, 0), self.winfo_width())  # Don't go out of bounds
            y2 = min(max(event.y, 0), self.winfo_width())
            self.new_label_temporary_box  = self.create_rectangle(x1,y1, x2,y2, fill="", outline=COLORS[SELECTED_CLASS], dash=(5, 2))
            self.new_label_temporary_text = self.create_text(x1, y1 - 5, fill=COLORS[SELECTED_CLASS], text=CLASSES[SELECTED_CLASS])
    def clicked(self, event):
        if self.editing:
            x,y = (event.x/self.winfo_width(), event.y/self.winfo_height())
            candidate_click = None
            min_candidate_click_distance = 9999999999

            for i in range(len(self.labels)):
                label = self.labels[i]
                bb, class_name, bb_id, new_label_text_id = label
                if x >= bb[0] and x <= bb[2] and y >= bb[1] and y <= bb[3]:
                    print("found match", x,y, bb)
                    current_distance = (bb[0] - x) **2 + (bb[1] - y) ** 2
                    if current_distance <min_candidate_click_distance:
                        candidate_click = i
                        min_candidate_click_distance = current_distance
            if candidate_click != None:
                label = self.labels[candidate_click]
                bb, class_name, bb_id, text_id = label
                self.delete(bb_id)
                self.delete(text_id)
                del self.labels[candidate_click]
        else:
            self.new_label_released_xy = None
            self.new_label_clicked_xy = (event.x, event.y)
        print("clicked at", self.new_label_clicked_xy)
    def click_release(self, event):
        if self.editing:
            return
        self.new_label_released_xy = (event.x, event.y)
        if self.new_label_clicked_xy != None and self.image_filename != DEFAULT_IMAGE_FILENAME: #Create Box
            x1,y1 = self.new_label_clicked_xy
            x2,y2 = self.new_label_released_xy
            x2 =  min(max(x2, 0), self.winfo_width()) #Don't go out of bounds
            y2 =  min(max(y2, 0), self.winfo_width())
            if abs(x2 -x1) > MIN_WIDTH and abs(y2- y1) > MIN_HEIGHT:
                #Note: top left is (0,0), bottom right is (1,1)
                self.new_label_box = self.create_rectangle(x1,y1,x2,y2, fill="", outline=COLORS[SELECTED_CLASS])
                self.new_label_text = self.create_text(x1, y1 - 5, fill=COLORS[SELECTED_CLASS], text=CLASSES[SELECTED_CLASS])
                bounding_box = (min(x1,x2)/ self.winfo_width(), min(y1,y2)/self.winfo_height(), max(x1,x2)/self.winfo_width(), max(y1,y2)/self.winfo_height())
                new_label = (bounding_box,CLASSES[SELECTED_CLASS],self.new_label_box,self.new_label_text)
                print("added", bounding_box, CLASSES[SELECTED_CLASS])
                self.labels.append(new_label)
                self.delete(self.new_label_temporary_box)
                self.delete(self.new_label_temporary_text)
                self.addtag_all("all")
        self.new_label_released_xy = None
        self.new_label_clicked_xy = None
        self.new_label_temporary_box = None
        self.new_label_temporary_text = None
        print("released at", event.x, event.y)
    def on_enter(self, event):
        self.update_crosshair(event)
    def on_leave(self, event):
        if self.horizontal_dash_line:
            self.delete(self.horizontal_dash_line)
        if self.vertical_dash_line:
            self.delete(self.vertical_dash_line)

class App(tk.Tk):
    """
    A simple demo of the basic Tkinter widgets. This can be used as a skeleton for a simple GUI applications.
    Unfortunately, on my system (Ubuntu) it looks like shit.
    """
    def __init__(self):
        tk.Tk.__init__(self)
        self.filename_label = None
        self.create_widget_frame()

        self.create_menu()
        self.set_keybindings()
        App.center_on_screen(self)

        self.frames = []
        self.file_path = None
        self.current_frame_index = 0


    @staticmethod
    def center_on_screen(toplevel):
        toplevel.update_idletasks()
        w = toplevel.winfo_screenwidth()
        h = toplevel.winfo_screenheight()
        size = (1200,750)#1134 582

        x = w / 2 - size[0] / 2
        y = h / 2 - size[1] / 2
        toplevel.geometry('%dx%d+%d+%d' % (size + (x, y)))

    def create_widget_frame(self):

        label_config = {'sticky': tk.E, 'column': 0, 'padx': 6, 'pady': 6}
        widget_config = {'sticky': tk.W, 'column': 1, 'padx': 6, 'pady': 6}

        widget_frame = tk.Frame(self)
        current_row = 0

        tk.Label(widget_frame, text='Current File: ').grid(label_config, row=current_row)
        self.filename_label = tk.Label(widget_frame, text='')
        self.filename_label.grid(label_config, row=current_row)
        current_row += 1

        tk.Label(widget_frame, text='Label: ').grid(label_config, row=current_row)
        self.selected_optionmenu = tk.StringVar(widget_frame)
        self.selected_optionmenu.set(CLASSES[SELECTED_CLASS])
        self.class_optionmenu = tk.OptionMenu(widget_frame, self.selected_optionmenu, *CLASSES)
        self.selected_optionmenu.trace("w", self.updated_class_combobox)
        self.class_optionmenu.grid(widget_config, row=current_row)
        current_row += 1

        widget_frame.pack(fill=tk.X, expand=tk.NO)

        self.frame_canvas = ImageCanvas(self)
        self.frame_canvas.pack(fill=tk.BOTH, expand=tk.YES)

    def updated_class_combobox(self, *args):
        global SELECTED_CLASS
        SELECTED_CLASS = CLASSES.index(self.selected_optionmenu.get())
    def set_keybindings(self):
        self.bind_all('<Control-o>', lambda event: self.open_frames())
        self.bind_all('<Control-q>', self.quit_app)
        self.bind_all('<Escape>', lambda event: self.frame_canvas.cancel())
        self.bind_all("<Key>", self.hotkey)

        #figure out how to
    def hotkey(self, event):
        if event.char in selected_class_indexes_as_strs:
            selected_class = int(event.char) - 1
            print("Updating class label to ", selected_class, CLASSES[selected_class])
            self.selected_optionmenu.set(CLASSES[selected_class])
        elif event.char == "d":
            if len(self.frames) > 0:
                self.current_frame_index = (self.current_frame_index + 1)  % len(self.frames)
                self.frame_canvas.load_image(self.frames[self.current_frame_index])
                self.filename_label.config(text= "Current File: " +  self.frames[self.current_frame_index])
        elif event.char == "a":
            if len(self.frames) > 0:
                self.current_frame_index = (self.current_frame_index - 1) % len(self.frames)
                self.frame_canvas.load_image(self.frames[self.current_frame_index])
                self.filename_label.config(text="Current File: " + self.frames[self.current_frame_index])
        elif event.char == "c":
            self.frame_canvas.clear_labels()
        elif event.char == "w":
            self.frame_canvas.editing = not self.frame_canvas.editing
            cross_hair_color = "red" if self.frame_canvas.editing else "black"
            self.frame_canvas.itemconfig(self.frame_canvas.horizontal_dash_line, fill=cross_hair_color)
            self.frame_canvas.itemconfig(self.frame_canvas.vertical_dash_line, fill=cross_hair_color)
        else:
            print("not selected", event.char)

    def create_menu(self):
        menubar = tk.Menu(self)

        fileMenu = tk.Menu(menubar)
        menubar.add_cascade(label="File", underline=0, menu=fileMenu)
        fileMenu.add_command(label="Open Directory", underline=1, command=self.open_frames, accelerator="Ctrl+O")

        helpMenu = tk.Menu(menubar, tearoff=False)
        menubar.add_cascade(label="Help", underline=0, menu=helpMenu)
        helpMenu.add_command(label="Help", underline=1, command=self.show_help, accelerator="Ctrl+H")
        helpMenu.add_command(label="About", underline=1, command=self.about_app)

        self.config(menu=menubar)

    def open_frames(self):
        """Options are explained here: http://tkinter.unpythonic.net/wiki/tkFileDialog"""
        print("Opening Frames...")
        directory_name = tk.filedialog.askdirectory()
        extensions = [".jpg",".png"]
        if directory_name:
            self.file_path = directory_name
            self.current_frame_index = 0
            self.frames = []
            correct_file_format = True
            for f in os.scandir(self.file_path):
               if f.is_file():
                    if os.path.splitext(f.name)[1].lower() in extensions:
                        self.frames.append(f.path)
                        if len(os.path.splitext(f.name)[0].split("_")[-1]) != 6: #Make sure frames are labeled with 6 digit identifier
                            correct_file_format = False
            if not correct_file_format:
                print("Warning: Please make sure images frame file name has 6 digit identifier: <framename>_<xxxxxx>.ext")
            self.frames.sort()
            print('Open and do something with %s' % self.file_path)
            print("current images...\n", self.frames)
            self.frame_canvas.load_image(self.frames[self.current_frame_index])
            self.filename_label.config(text= "Current File: " +  self.frames[self.current_frame_index])

    def quit_app(self, event):
        sys.exit(0)

    def show_help(self):
        print('Go to the github: www.github.com')

    def about_app(self):
        about_text = "Matthew Saponaro\nmattsap@aiwhoo.com" + "\nVersion " + str(VERSION) + "\nCheck out our website: www.aiwhoo.com"
        about_dialog = tk.Toplevel(self)
        about_dialog.title('About App')
        about_dialog.bind('<Escape>', lambda event: about_dialog.destroy())
        about_dialog.bind('<Return>', lambda event: about_dialog.destroy())
        App.center_on_screen(about_dialog)
        tk.Message(about_dialog, text=about_text).pack(fill=tk.X, expand=tk.YES)
        button = tk.Button(about_dialog, text='Close', command=about_dialog.destroy).pack()

if __name__ == "__main__":
    app = App()
    app.resizable(False, False)
    app.title("LabelVision")
    app.mainloop()
