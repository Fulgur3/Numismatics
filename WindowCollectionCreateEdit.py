from tkinter import *
from PIL import Image, ImageTk
from tkinter.messagebox import askyesno, showinfo, showwarning

from GUI.EntryWithPlaceholder import EntryWithPlaceholder
from GUI.TextWithPlaceholder import TextWithPlaceholder
from Connection import *
from Utils import *
from Definitions import *
from WindowMode import WindowMode


class WindowCollectionCreateEdit(Toplevel):
    def __init__(self, controller, window_mode):
        Toplevel.__init__(self)
        self.mode = window_mode

        self.controller = controller
        self.collections_page = controller.controller
        self.username = controller.username

        self.title('New collection')
        self.geometry('500x900+300+100')
        self.resizable(False, False)
        self.configure(bg="white")

        img = Image.open(PATH_IMAGE_EMPTY)
        img = img.resize((400, 400), Image.ANTIALIAS)
        self.image = ImageTk.PhotoImage(img)
        self.collection_image = Label(self, image=self.image, bg='white', borderwidth=0)
        self.collection_image.grid(row=0, column=1, sticky="w", pady=(20, 20))
        self.image_value = None

        self.name_entry = EntryWithPlaceholder(self, "Collection name")
        self.name_entry.grid(row=1, column=1, sticky="w", pady=(20, 0))

        br = Frame(self, width=400, height=2, bg='black')
        br.grid(row=2, column=1, sticky="w", pady=(0, 20))

        self.description = TextWithPlaceholder(self, placeholder="Description", width=40, height=5)
        self.description.grid(column=1, row=3, sticky="w", pady=(20, 0))

        br2 = Frame(self, width=400, height=2, bg='black')
        br2.grid(row=4, column=1, sticky="w", pady=(0, 20))

        frame_btn = Frame(self, bg="white", width=400, height=200)
        frame_btn.grid(row=5, column=1)
        self.delete_btn = Button(
            frame_btn, width=30, pady=7, text='Delete', bg='#95e07b', fg='white', border=0,
            font=('Microsoft YaHei UI Light', 11), command=lambda: self.delete()
        )
        self.delete_btn.grid(row=0, column=1, sticky="w", pady=(20, 20))
        if self.mode == WindowMode.CREATE_NEW:
            self.delete_btn.grid_remove()
        if self.mode == WindowMode.CREATE_NEW:
            text = "Create"
        else:
            text = "Save"
        self.create_save_btn = Button(
            frame_btn, width=30, pady=7, text=text, bg='#95e07b', fg='white', border=0,
            font=('Microsoft YaHei UI Light', 11), command=lambda: self.create_save()
        )
        self.create_save_btn.grid(row=1, column=1, sticky="w", pady=(20, 20))
        frame_btn.grid_columnconfigure(0, weight=1)
        frame_btn.grid_columnconfigure(2, weight=1)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)

        self.collection_image.bind("<Button-1>", self.set_image)

        self.is_general = False
        if text == 'Save':
            self.load()

    def create_save(self):
        name = self.name_entry.get_text()
        if self.mode == WindowMode.CREATE_NEW:
            if name == GENERAL_COLLECTION_NAME:
                showwarning('Info', 'You can\'t create one more \'' + GENERAL_COLLECTION_NAME + '\' collection')
                return
            connection.create_collection(
                self.username, name, self.description.get_text(), self.image_value
            )
            self.controller.load_collections()
        elif self.mode == WindowMode.EDIT:
            if not self.is_general and name == GENERAL_COLLECTION_NAME:
                showwarning('Info', 'You can\'t set \'' + GENERAL_COLLECTION_NAME + '\' name for this collection')
                return
            connection.update_collection(
                self.controller.collection_id, name, self.description.get_text(), self.image_value
            )
            self.controller.load_collection_info()
        self.destroy()

    def delete(self):
        name = connection.get_collection_name(self.controller.collection_id)
        if name == GENERAL_COLLECTION_NAME:
            showwarning("Info", "You can't delete your \'" + GENERAL_COLLECTION_NAME + "\' collection")
            return
        answer = askyesno('Collection delete confirmation', 'Are you sure? Information about all tokens will be lost')
        if answer:
            connection.delete_collection(self.controller.collection_id)
            self.collections_page.show_frame("PageHome")
            self.destroy()

    def set_image(self, e):
        if self.name_entry.get_text() == GENERAL_COLLECTION_NAME:
            return
        file = open_image()
        if not file:
            return
        img = Image.open(file)
        img = img.resize((400, 400), Image.ANTIALIAS)
        self.image = ImageTk.PhotoImage(img)
        self.collection_image.configure(image=self.image)
        file = open(file, 'rb')
        file = io.BytesIO(file.read())
        file.seek(0, os.SEEK_END)
        self.image_value = file.getvalue()

    def load(self):
        rs = connection.get_collection(self.controller.collection_id)
        self.name_entry.set_text(rs[0])
        if rs[0] == GENERAL_COLLECTION_NAME:
            self.name_entry.config(state=DISABLED)
            self.is_general = True
            self.image_value = get_general_image_bytes()
            img = Image.open(PATH_IMAGE_COLLECTION_GENERAL)
            img = img.resize((400, 400), Image.ANTIALIAS)
            self.image = ImageTk.PhotoImage(img)
            self.collection_image.configure(image=self.image)
        if rs[1] is not None:
            self.description.set_text(rs[1])
        if rs[2] is not None:
            img = rs[2].read()
            pre_img = io.BytesIO(img)
            img = Image.open(pre_img)
            img = img.resize((400, 400), Image.ANTIALIAS)
            self.image = ImageTk.PhotoImage(img)
            self.collection_image.configure(image=self.image)
            self.image_value = rs[2]
