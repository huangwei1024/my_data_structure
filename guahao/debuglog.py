#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


class DebugLog(object):
	def __init__(self, filename = None, console = True):
		self.buff = ''
		self.sys_out = sys.stdout
		self.sys_err = sys.stderr
		self.console = console
		self.logfile = None
		if filename is not None:
			self.logfile = open(filename + '.log', 'a+')
			self.logfile.write('='*50 + '\n')
			self.logfile.write(str(datetime.now()) + '\n')
			self.logfile.write('='*50 + '\n')

		sys.stdout = self
		sys.stderr = self

	def write(self, stream):
		if self.console:
			self.sys_out.write(stream)
		if self.logfile:
			self.logfile.write(stream)

DebugLog('guahao', True)
