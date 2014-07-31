#!/usr/bin/python
# -*- coding: utf-8 -*-

import Tkinter as tk
import ttk
import tkFont
from PIL import Image, ImageTk
import json

uni2utf = lambda x: x.encode('utf8')

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
		self.image = tk.Label(self, pady = 10, image = self.img)
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



class SelectBox(tk.Frame):

	def createWidgets(self):
		self.lable = tk.Label(self, text = '请选择登录账号\n', font = tkFont.Font(family = '黑体', size = 20, weight = tkFont.BOLD))
		self.lable.pack()

		fp = open('user.config', 'r')
		data = fp.read()
		fp.close()
		self.userJs = json.loads(data)['users']
		self.userList = []
		i = 1
		for u in self.userJs:
			if 'beizhu' in u:
				self.userList.append('%d.%s (%s)' % (i, uni2utf(u['name']), u['beizhu']) )
			else:
				self.userList.append('%d.%s' % (i, uni2utf(u['name'])) )
			i += 1

		self.userComb = ttk.Combobox(self, values = self.userList, font = tkFont.Font(family = 'Arial', size = 16))
		self.userComb.current(0)
		self.userComb.pack()
		
		self.ok = tk.Button(self, text = '确  定', width = 20, command = self.select_ok)
		self.ok.pack(pady = 15)

	def select_ok(self):
		select_index = self.userComb.current()
		info = self.userJs[select_index]

		for k, v in info.items():
			if isinstance(k, unicode):
				k = uni2utf(k)
			if isinstance(v, unicode):
				v = uni2utf(v)
			self.userInfo[k] = v

		self.root.quit()
		self.root.destroy()

	def __init__(self):
		self.root = tk.Tk()
		tk.Frame.__init__(self, self.root)

		self.root.title('选择登录账号')
		self.root.resizable(False, False)

		self.pack()
		self.createWidgets()
		self.userComb.focus_set()

		pos_center(self.root)

		self.userInfo = {}