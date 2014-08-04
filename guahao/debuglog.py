#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime
import sys
import platform
import os

reload(sys)
sys.setdefaultencoding('utf-8')


class DebugLog(object):
	def __init__(self, filename = None, console = True):
		print self, 'in process', os.getpid(), 'sys.stdout =', type(sys.stdout)
		self.buff = ''
		self.sys_out = sys.stdout
		self.sys_err = sys.stderr
		self.console = console
		self.logfile = None
		if filename is not None:
			self.logfile = open(filename + str(os.getpid()) + '.log', 'a+')
			self.logfile.write('='*50 + '\n')
			self.logfile.write(str(datetime.now()) + '\n')
			self.logfile.write('='*50 + '\n')

		sys.stdout = self
		sys.stderr = self

	def write(self, stream):
		if self.console:
			if platform.system() == 'Windows':
				self.sys_out.write(stream.decode('utf8').encode('gbk'))
			else:
				self.sys_out.write(stream)
		if self.logfile:
			self.logfile.write(stream)

	def flush(self):
		if self.console:
			self.sys_out.flush()
		if self.logfile:
			self.logfile.flush()

DebugLog('guahao', True)
