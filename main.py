import tkinter as tk
import cv2 as cv
from PIL import Image, ImageTk
# import main

# TODO
# 1. [DONE] Figure out how to add the functionality of moving the grid while it is selected without adding it as another overlay
# 2. Figure out how to overlay the grid image on top of the actual image. figure out how to put the grid below the buckle but above the paper (see whiteboard)
# 3. Add functionality to turn off the above feature (in case this does not work on site and everything is default method)
# 4. Create outlines for the rest of the buckles and knives
# 5. Figure out github version publishing and .exe publication
#   a. as a sub-point for the one above, change all the paths to be relative
# 6. Modularize code and put it into separate classes
# 7. DOCUMENT CODE!!


class GUI:
    def __init__(self):
        # dictionary of the images
        self.paths = {
            "Grid": r"grid.png",
            "Center": r"crosshair.png",
            "Wavy Plate": r"test1.png",
            "Plain Plate": r"Plain Plate.png",
            "Big Bolster": r"Big Bolster.png",
            "Small Bolster": r"Small Bolster.png"
        }

        # sets up the tk gui object
        self.overlay_canvas = None
        self.window = tk.Tk()
        self.window.title('EzCAD Helper')

        # 2 columns, one for the video, one for the buttons
        self.window.columnconfigure(0, weight=5)
        self.window.columnconfigure(1, weight=1)
        self.window.rowconfigure(0, weight=1)

        # creates a video_div box
        self.video_div = tk.Frame(self.window, bg="blue")
        self.video_div.grid(row=0, column=0, sticky="nsew")
        self.tk_videostream = tk.Label(self.video_div)

        # dropdown option creation
        self.dropdown_div = tk.Frame(self.window)  # create the dropdown div
        self.dropdown_div.grid(row=0, column=1, sticky="nsew")  # the dropdown is on the right column

        # create the dropdown object and pack it
        self.option = tk.StringVar()  # the variable that holds the dropdown value
        self.option.set("Select an Option")  # default value
        self.overlay_choices = ['Center', 'Wavy Plate', 'Plain Plate', 'Big Bolster', 'Small Bolster',
                                'Grid']  # choice array
        self.item_dropdown = tk.OptionMenu(self.dropdown_div, self.option, *self.overlay_choices)
        self.item_dropdown.pack(fill="both", padx=10)
        self.option.trace("w", self.change)

        # Creates the hide option and functionality
        self.hidden_option = False
        self.menu_button = tk.Button(self.video_div, command=self.hide_sidebar, text="Show")
        self.menu_button.place(in_=self.video_div, relx=1, rely=0, relwidth=.15, relheight=.075, anchor="ne")

        # pack the videostream object as well
        self.tk_videostream.pack(fill="both", expand=True)

        # sets up the capture object
        self.cap = cv.VideoCapture(0, cv.CAP_DSHOW)

        # the overlay image is the buckle outline
        self.overlay_path = r"crosshair.png"
        self.overlay = None
        self.modifiable_object = self.overlay
        try:
            # the overlay is the regular image, which we then resize and store in overlay_resized
            self.overlay = Image.open(self.overlay_path).convert('RGBA')
            # print(self.overlay.size)
            self.overlay_resized = self.overlay.resize(
                (int(self.overlay.size[0] * 0.6), int(self.overlay.size[1] * 0.6)))
            self.modifiable_object = self.overlay_resized
        except Exception as e:
            print(f"Error loading overlay: {e}")

        # gets the video stream for sizing purposes once at startup
        ret, frame = self.cap.read()
        cv_image = cv.cvtColor(frame, cv.COLOR_BGR2RGBA)
        self.video = Image.fromarray(cv_image)

        # default size of an overlay image
        self.img_size_x = 307
        self.img_size_y = 173

        # gets the x and y size of the video stream frame
        self.canvas_size_x = self.video.size[0]
        self.canvas_size_y = self.video.size[1]

        # center of the canvas
        self.center = (int((self.canvas_size_x / 2.) - (self.img_size_x / 2.)),
                       int((self.canvas_size_y / 2.) - (self.img_size_y / 2.)))

        # default data of the overlay image
        self.img_pos_x = self.center[0]
        self.img_pos_y = self.center[1]
        self.scale = 1.0

        # sets the geometry of the window to be 100 pixels longer than half of the resolution
        self.window.geometry(f"{int(float(self.canvas_size_x) * 0.5)}x{int(float(self.canvas_size_y) * 0.5)}")

        # binds for moving the overlay image
        self.window.bind("<Left>", self.move_left)
        self.window.bind("<Right>", self.move_right)
        self.window.bind("<Up>", self.move_up)
        self.window.bind("<Down>", self.move_down)
        self.window.bind("<space>", self.center_outline)
        self.window.bind("=", self.resize)
        self.window.bind("+", self.resize)
        self.window.bind("_", self.resize)
        self.window.bind("-", self.resize)

        # Red grid overlay
        self.grid = Image.open(self.paths.get('Grid')).convert('RGBA')
        self.resized_grid = self.grid.resize((self.canvas_size_x, self.canvas_size_y))

        # Checkbox to toggle grid
        self.grid_toggle_val = tk.BooleanVar(value=True)
        self.grid_checkbox = tk.Checkbutton(self.dropdown_div, text='Grid', variable=self.grid_toggle_val,
                                            command=self.toggle_grid)
        self.grid_checkbox.pack()
        # if the camera never opened, throw an error
        if not self.cap.isOpened():
            print('error opening camera')
            exit()
        # self.video_with_grid = main.VideoWithGrid()

    def change(self, *args):
        print(self.option.get())
        if self.option.get() == "Grid":
            self.modifiable_object = self.resized_grid
        else:
            self.overlay_path = self.paths.get(self.option.get())
            self.overlay = Image.open(self.overlay_path).convert('RGBA')
            self.overlay_resized = self.overlay.resize((int(self.overlay.size[0]), int(self.overlay.size[1])))
            self.modifiable_object = self.overlay_resized
            print('here')
        self.img_size_x = self.modifiable_object.size[0]
        self.img_size_y = self.modifiable_object.size[1]
        self.center_outline(None)

    def hide_sidebar(self):
        print(self.hidden_option)
        if self.hidden_option:
            self.dropdown_div.grid_remove()
            self.menu_button.configure(text="Show")
        else:
            self.dropdown_div.grid(row=0, column=1)
            self.menu_button.configure(text="Hide")
        self.hidden_option = not self.hidden_option

    def toggle_grid(self):
        print(self.grid_toggle_val)
        if self.grid_toggle_val:
            self.resized_grid = self.resized_grid.resize((1, 1))
        else:
            print(self.resized_grid.size)
            self.resized_grid = self.grid.resize((self.canvas_size_x, self.canvas_size_y))
            print(self.resized_grid)

        self.grid_toggle_val = not self.grid_toggle_val

    def run(self):
        self.video_stream()
        self.window.mainloop()

    def move_left(self, event):
        self.img_pos_x -= 1.

    def move_right(self, event):
        self.img_pos_x += 1.

    def move_up(self, event):
        self.img_pos_y -= 1.

    def move_down(self, event):
        self.img_pos_y += 1.

    def center_outline(self, event):
        self.img_pos_x = (self.canvas_size_x / 2.) - (self.img_size_x / 2.)
        self.img_pos_y = (self.canvas_size_y / 2.) - (self.img_size_y / 2.)

    def resize(self, event):
        print(event.keysym)
        # depending on the key (+) or (-), sets the scale multiplier
        if event.keysym == "equal":
            self.scale = 1.01
        elif event.keysym == "minus":
            self.scale = 0.99
        elif event.keysym == "underscore":
            self.scale = 0.9
        elif event.keysym == "plus":
            self.scale = 1.1
        else:
            self.scale = 1.

        # saves the current position
        og_x_size = self.img_size_x
        og_y_size = self.img_size_y

        # multiplies by scale factor
        self.img_size_x *= self.scale
        self.img_size_y *= self.scale

        # resizes
        self.modifiable_object = self.overlay_resized.resize((int(self.img_size_x), int(self.img_size_y)))

        # places back at the original position to mimic scaling happening from origin
        self.img_pos_x -= ((self.img_size_x - og_x_size) / 2.)
        self.img_pos_y -= ((self.img_size_y - og_y_size) / 2.)

    def video_stream(self):
        # get the frame
        ret, frame = self.cap.read()
        # self.video_with_grid.captureVideo()
        # buckle = self.video_with_grid.result
        if not ret:
            print('break')
            self.cleanup()
            return
        try:
            # cv_image is the image processed from cv library
            cv_image = cv.cvtColor(frame, cv.COLOR_BGR2RGBA)
            cv_image = cv.flip(cv_image, -1)

            # convert cv-image to PIL Image object
            img = Image.fromarray(cv_image)

            # If the overlay exists
            if self.overlay:
                # the overlay is the regular image, which we then resize and store in overlay_resized
                self.overlay = Image.open(self.overlay_path).convert('RGBA')

                # Overlay canvas is a new image that is the size of the videostream
                self.overlay_canvas = Image.new('RGBA', img.size, (0, 0, 0, 0))

                # Position the image will appear at
                position = (int(self.img_pos_x), int(self.img_pos_y))

                # Paste the overlay image to the canvas
                self.overlay_canvas.paste(self.resized_grid, (0, 0), self.resized_grid)
                self.overlay_canvas.paste(self.modifiable_object, position, self.modifiable_object)

                #  is both images
                combined = Image.alpha_composite(img.convert('RGBA'), self.overlay_canvas)

            else:
                combined = img

            # update the size of the window
            self.window.update_idletasks()

            # scale the size of the window to be proportional to the window
            width = max(1, self.video_div.winfo_width())
            height = max(1, self.video_div.winfo_height())
            combined = combined.resize((width, height))

            # imgTk object created
            imgtk = ImageTk.PhotoImage(combined)

            # puts the image into the window
            # self.tk_videostream.grid(row=0, column=0)
            self.tk_videostream.imgtk = imgtk
            self.tk_videostream.configure(image=imgtk)
            self.tk_videostream.grid(row=0, column=0, sticky="nsew")
            # print('x: ', self.img_pos_x, 'y: ', self.img_pos_y, 'x-scale: ', self.img_size_x, 'y-scale: ',
            # self.img_size_y)
            self.tk_videostream.after(5, self.video_stream)

        except Exception as e:
            print(e)
            self.cleanup()

    def cleanup(self):
        try:
            self.cap.release()
            self.window.quit()
            exit()
        except Exception as e:
            print(f'Error with cleanup: {e}')


if __name__ == '__main__':
    g = GUI()
    g.run()
