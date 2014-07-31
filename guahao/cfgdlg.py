#!/usr/bin/python
# -*- coding: utf-8 -*-

import Tkinter as tk
import tkFont
from PIL import Image, ImageTk
import json

def pos_center(root):
	screen_width = root.winfo_screenwidth()
	screen_height = root.winfo_screenheight()

	root.update_idletasks()
	root.deiconify()
	# print root.winfo_width(), root.winfo_height()
	root.geometry('+%s+%s' % ((screen_width - root.winfo_width())/2-200, (screen_height - root.winfo_height())/2-200))    #center window on desktop
	root.deiconify()


class ConfigDialog(tk.Frame):
	def __init__(self):
		self.root = tk.Tk()
		tk.Frame.__init__(self, self.root)

		self.root.title('省妇保挂号配置')
		self.root.resizable(False, False)

		self.pack()
		self.createWidgets()
		pos_center(self.root)

	def createWidgets(self):
		pass


if __name__ == '__main__':
	# ConfigDialog().mainloop()

	a = {'user':[
	{'name':'俞婷','id':'330624198611118304','password':'521521','yiyuan':'浙江大学医学院附属妇产科医院','keshi':'普通产科'},
	{'name':'胡路茶','id':'341021198807209866','password':'19880720hlc','yiyuan':'浙江大学医学院附属妇产科医院','keshi':'普通产科'},
	]}
	b = json.dumps(a,indent=4,ensure_ascii=False)
	# print b
	fp = open('tt.txt', 'w')
	fp.write(b)
	fp.close()

	# fp = open('tt.txt', 'r')
	# b = fp.read()
	# fp.close()
	# js = json.loads(b)
	# # print js
	# print json.dumps(js, 'gbk')
