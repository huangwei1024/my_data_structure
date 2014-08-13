#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime
import sys
import platform
import os
import time

reload(sys)
sys.setdefaultencoding('utf-8')

def utf2local(s):
	if platform.system() == 'Windows':
		return s.decode('utf8').encode('gbk')
	return s

class Timer(object):  
	def __init__(self, name, verbose=True):  
		self.verbose = verbose  
		self.name = name
  
	def __enter__(self):  
		self.start = time.time()  
		return self  
  
	def __exit__(self, *args):  
		self.end = time.time()  
		self.secs = self.end - self.start  
		self.msecs = self.secs * 1000  # millisecs  
		if self.verbose:  
			print '[DEBUG] %s elapsed time: %f ms' % (self.name, self.msecs)

class EventLocker(object):
	def __init__(self, ev):
		self.ev = ev

	def __enter__(self):
		self.ev.set()
		return self

	def __exit__(self, *args):
		self.ev.clear()
		time.sleep(1)

class DebugLog(object):
	def __init__(self, filename = None, console = True, proc = False):
		print 'DebugLog in process', os.getpid(), 'sys.stdout =', type(sys.stdout)
		self.proc = proc
		self.sys_out = sys.stdout
		self.sys_err = sys.stderr
		self.console = console
		self.logfile = None
		if filename is not None:
			self.logfile = open(filename + str(os.getpid()) + '.log', 'w') if self.proc else open(filename + '.log', 'a+')
			# self.logfile = open(filename + '.log', 'a+')
			self.logfile.write('='*50 + '\n')
			self.logfile.write(str(datetime.now()) + '\n')
			self.logfile.write('='*50 + '\n')

		sys.stdout = self
		sys.stderr = self

	def write(self, stream):
		if self.console:
			if platform.system() == 'Windows':
				try:
					stream = utf2local(stream)
				except Exception:
					pass
			self.sys_out.write(stream)
		if self.logfile:
			self.logfile.write(stream)

	def flush(self):
		if self.console:
			self.sys_out.flush()
		if self.logfile:
			self.logfile.flush()

