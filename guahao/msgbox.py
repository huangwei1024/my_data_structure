#!/usr/bin/python
# -*- coding: utf-8 -*-

import Tkinter as tk
import tkFont
from PIL import Image, ImageTk

def pos_center(root):
	screen_width = root.winfo_screenwidth()
	screen_height = root.winfo_screenheight()

	root.update_idletasks()
	root.deiconify()
	# print root.winfo_width(), root.winfo_height()
	root.geometry('+%s+%s' % ((screen_width - root.winfo_width())/2-200, (screen_height - root.winfo_height())/2-200))    #center window on desktop
	root.deiconify()

class MsgBox(tk.Frame):

	def createWidgets(self):
		self.lable = tk.Label(self, text = self.msg, font = tkFont.Font(family = '黑体', size = 20, weight = tkFont.BOLD))
		self.lable.pack()

	def __init__(self, title = '', msg = ''):
		self.root = tk.Tk()
		tk.Frame.__init__(self, self.root)

		self.msg = msg

		self.root.title(title)
		self.root.resizable(False, False)

		self.pack()
		self.createWidgets()

		pos_center(self.root)

class InputBox(tk.Frame):

	def createWidgets(self):
		self.lable = tk.Label(self, text = self.msg, font = tkFont.Font(family = '黑体', size = 20, weight = tkFont.BOLD))
		self.lable.pack()

		self.img = ImageTk.PhotoImage(file = self.imgfile)
		self.image = tk.Label(self, image = self.img)
		self.image.pack()

		self.input = tk.Entry(self, width = 10, font = tkFont.Font(family = 'Arial', size = 20, weight = tkFont.BOLD))
		self.input.pack()
		
		self.contents = tk.StringVar()
		self.contents.set("")
		self.input.config(textvariable = self.contents)
		self.input.bind('<Key-Return>', self.input_contents)

	def input_contents(self, event):
		self.code = self.contents.get()
		self.root.quit()
		self.root.destroy()

	def __init__(self, title = '', imgfile = '', msg = ''):
		self.root = tk.Tk()
		tk.Frame.__init__(self, self.root)

		self.imgfile = imgfile
		self.code = ''
		self.msg = msg

		self.root.title(title)
		self.root.resizable(False, False)

		self.pack()
		self.createWidgets()
		self.input.focus_set()

		pos_center(self.root)

