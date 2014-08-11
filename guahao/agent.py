#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib
import urllib2 
import httplib
import cookielib
import zlib
import StringIO
import gzip
import re
import random
import datetime
import multiprocessing
import traceback

import msgbox
import debuglog
from debuglog import Timer, EventLocker, DebugLog

nowtime = lambda : str(datetime.datetime.now())
rndistr = lambda : str(random.randint(1000000000, 9999999999))
utf2local = debuglog.utf2local

yzm_filename_f = 'hyid%s.png'
yanzhenma_URL_f = 'http://guahao.zjol.com.cn/ashx/getyzm.aspx?k=7173&t=yy&hyid=%s'
login_URL_f = 'http://guahao.zjol.com.cn/ashx/LoginDefault.ashx?idcode=%s&pwd=%s&txtVerifyCode=%s'



def http_gzip(data):
	compressedstream = StringIO.StringIO(data)
	gzipper = gzip.GzipFile(fileobj=compressedstream)
	return gzipper.read()

def make_cookies(cookieDict):
	return '; '.join(['%s=%s' % x for x in cookieDict.items()])

class Agent(multiprocessing.Process):
	def __init__(self, args):
		multiprocessing.Process.__init__(self, args=args)
		self.event, self.okEvent = args

	def setInfo(self, cookieDict, chanke_Referer, chanke_Name, doctorname_Choice, errmax):
		self.yzm_filename = 'yyzm.png'
		self.loginyzm_filename = 'yzm.png'
		self.chanke_Referer = ''
		self.chanke_Name = ''

		self.headers = {"Content-type": "application/x-www-form-urlencoded",
					"Accept": "*/*",
					"Accept-Encoding": "gzip,deflate,sdch",
					"Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
					"Host": "guahao.zjol.com.cn",
					"Origin": "http://guahao.zjol.com.cn",
					"Connection": "keep-alive",
					"Referer": chanke_Referer,
					"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2024.2 Safari/537.36",
					"X-Requested-With": "XMLHttpRequest",
		}
		self.sgList = []
		self.cookieDict = {'pgv_pvi': rndistr(), 
						'pgv_si': rndistr(),
						'BAIDU_DUP_lcr': 'https://www.google.com.hk/',
						'CNZZDATA30020775': 'cnzz_eid%3D833334187-1405072273-null%26ntime%3D' + rndistr(),
		}
		self.cookieDict.update(cookieDict)
		self.headers['Cookie'] = make_cookies(self.cookieDict)
		self.httpClient = httplib.HTTPConnection("guahao.zjol.com.cn", 80)
		self.firstQueue = True
		self.errmax = errmax
		self.doctorname_Choice = doctorname_Choice

	def step_1(self):
		if len(self.sgList) > 0:
			return self.sgList[0]

		self.httpClient.request("GET", self.headers["Referer"], headers=self.headers)
		response = self.httpClient.getresponse()
		encoding = response.getheader('Content-Encoding')
		data = response.read()

		if response.status != 200:
			print 'step 1. GET Error', response.status, response.reason
			return None

		if encoding == 'gzip':
			data = http_gzip(data)

		# find doctor
		if len(self.doctorname_Choice) > 0:
			reg = r'<td height="45px">.*?<b class="red12">(?P<name>%s)</b>(?P<yy>.*?)</tr>' % self.doctorname_Choice
			result = ""
			match = re.search(reg, data, re.DOTALL)
			if match:
				result = match.group("yy")
			if len(result) != 0:
				data = result
			else:
				print '没有指定医生 %s!' % self.doctorname_Choice
				return None

		self.sgList = re.findall(r"javascript:showDiv\('(?P<sg>[^']*)'\)", data)
		if len(self.sgList) == 0:
			print '没有可预约的!'
			return None
		return self.sgList[0]

	def step_2(self, sg):
		body = urllib.urlencode({'sg': sg})
		self.httpClient.request("POST", "/ashx/gethy.ashx", body, self.headers)
		response = self.httpClient.getresponse()
		data = response.read()

		if response.status != 200:
			print 'step 2. gethy POST Error', response.status, response.reason
			return None

		dlist = data.split('#')
		if len(dlist) < 12:
			print 'step 2. gethy POST Response Error', data
			return None
		return dlist

	def step_3(self, yanzhenma_URL):
		self.httpClient.request("GET", yanzhenma_URL, headers=self.headers)
		response = self.httpClient.getresponse()
		encoding = response.getheader('Content-Encoding')
		data = response.read()

		if response.status != 200:
			print 'step 3. GET yzm error', response.status, response.reason
			return False

		if encoding == 'gzip':
			data = http_gzip(data)

		fp = open(self.yzm_filename, 'wb')
		fp.write(data)
		fp.close()
		return True

	def refresh_yy(self):

		que = []
		info = {}
		cur_choose = 0

		while True:
			try:
				with Timer('refresh_yy GET sg'):
					sg = self.step_1()
					if sg is None:
						break

				with Timer('refresh_yy GET dlist'):
					dlist = self.step_2(sg)
					if dlist is None:
						continue

				hospital = dlist[1]
				office = dlist[2]
				doctor = dlist[3]
				patient = dlist[6]
				date = dlist[8]
				mgenc = dlist[12]
				orders = dlist[11].split('$')[1:]

				if len(orders) == 0:
					self.sgList = self.sgList[1:] # 下个预约日
					continue

				info['hospital'] = hospital
				info['office'] = office
				info['doctor'] = doctor
				info['patient'] = patient
				info['date'] = date
				info['mgenc'] = mgenc
				info['n_orders'] = len(orders)

				cur_choose = 0
				while cur_choose < len(orders):
					order = orders[cur_choose]
					cur_choose += 1
					info['cur_choose'] = cur_choose

					hyid, number, time, flag = order.split('|')
					yanzhenma_URL = yanzhenma_URL_f % hyid
					# yzm_filename = yzm_filename_f % hyid
					yzm_filename = yzm_filename_f % 'yzm'
					if flag == '1':
						# 该号被禁止抢
						continue

					info['number'] = number
					info['time'] = time
					info['time_s'] = '%s:%s' % (time[:2], time[2:])
					info['hyid'] = hyid
					info['yzm_filename'] = yzm_filename
					info['yanzhenma_URL'] = yanzhenma_URL

					que.append(info.copy())
				
				break # 只取一个预约日
				# sgList = sgList[1:] # 下个预约日
				# if len(sgList) == 0:
				# 	break

			except httplib.CannotSendRequest:
				traceback.print_exc()
				print '[refresh_yy] 重连服务器'
				with Timer('refresh_yy re-connect'):
					self.httpClient.close()
					self.httpClient = httplib.HTTPConnection("guahao.zjol.com.cn", 80)
				cur_choose -= 1
				continue

			except httplib.BadStatusLine:
				traceback.print_exc()
				cur_choose -= 1
				continue

			except Exception:
				traceback.print_exc()
				print '[refresh_yy] 重连服务器'
				with Timer('refresh_yy re-connect'):
					self.httpClient.close()
					self.httpClient = httplib.HTTPConnection("guahao.zjol.com.cn", 80)
				cur_choose -= 1
				continue

		print '[refresh_yy] OK', len(que)
		return que

	def check(self):
		with Timer('refresh_yy'):
			yyQueue = self.refresh_yy()

		if self.event.is_set():
			import time
			time.sleep(1)
			return False

		while len(yyQueue) > 0:
			try:
				# 读顺序配置
				yy_choose = 1 if self.firstQueue else 0
				if len(yyQueue) == 1:
					yy_choose = 0
				else:
					# if len(user_info) > 0 and len(user_info['qh_shunxu']) > 0:
					# 	for i in xrange(len(user_info['qh_shunxu'])):
					# 		yy_choose = user_info['qh_shunxu'][(i + user_qh_cnt) % len(user_info['qh_shunxu'])] -1
					# 		if yy_choose < len(yyQueue):
					# 			user_qh_cnt += i + 1
					# 			break
					# else:
					if len(yyQueue) > 10:
						# 号子多时前3个随机
						yy_choose = random.randint(1 if self.firstQueue else 0, min(1, len(yyQueue) - 1))

				yy_choose = yy_choose % len(yyQueue)
				info = yyQueue[yy_choose]
				yyQueue = yyQueue[yy_choose+1:]
				self.firstQueue = False

				hospital = info['hospital']
				office = info['office']
				doctor = info['doctor']
				patient = info['patient']
				date = info['date']
				mgenc = info['mgenc']
				cur_choose = info['cur_choose']
				hyid = info['hyid']
				number = info['number']
				time = info['time']
				time_s = info['time_s']
				yzm_filename = info['yzm_filename']
				n_orders = info['n_orders']

				print ' '.join([patient, hospital, office, doctor, date])
				print '一共有%d个号子 选择了第%d个' % (n_orders, cur_choose)

				with EventLocker(self.event):

					# 下载验证码
					with Timer('GET yanzhenma'):
						yanzhenma_URL = info['yanzhenma_URL']
						if not self.step_3(yanzhenma_URL):
							return False
					
					# yzm = raw_input('input %s code (empty use OCR):' % yzm_filename)

					msg = '\n'.join([patient, hospital, office, doctor, date]) + '\n'
					msg += '-'*20 + '\n'
					msg += '一共有%d个号子\n选择了第%d个\n' % (n_orders, cur_choose)
					msg += ''.join([number, '号/', time_s])
					dlg = msgbox.InputBox(title ='预约', imgfile = yzm_filename, msg = msg)
					with Timer('your input'):
						dlg.mainloop()
					yzm = dlg.code
					del dlg

					if len(yzm) != 5:
						# yzm = 'zzzzz'
						return False
					print '验证码输入为', yzm

					lgcfas = hyid
					xh = number
					qhsj = time
					sg = mgenc

					# step 4.
					with Timer('POST TreadYuyue'):
						body = urllib.urlencode({'sg':sg, 'lgcfas':lgcfas, 'yzm':yzm, 'xh':xh, 'qhsj':qhsj})
						self.httpClient.request("POST", '/ashx/TreadYuyue.ashx', body, self.headers)
						response = self.httpClient.getresponse()
						data = response.read()

						print data
						if response.status != 200:
							print 'step 4. POST TreadYuyue error', response.status, response.reason
							return False
						
						rlst = data.split('|')
						if len(rlst) == 0 or rlst[0] == 'ERROR':
							return False

					return True

			except httplib.CannotSendRequest:
				traceback.print_exc()
				print '重连服务器'
				with Timer('re-connect'):
					self.httpClient.close()
					self.httpClient = httplib.HTTPConnection("guahao.zjol.com.cn", 80)
				return False

			except httplib.BadStatusLine:
				traceback.print_exc()
				return False

			except Exception:
				traceback.print_exc()
				print '重连服务器'
				with Timer('re-connect'):
					self.httpClient.close()
					self.httpClient = httplib.HTTPConnection("guahao.zjol.com.cn", 80)
				return False


	def run(self):
		print self.pid, 'running...'
		DebugLog('proc', True)

		errcnt = 0
		while not self.okEvent.is_set():
			print '-'*50
			print nowtime(), self.pid, '第%d次尝试%s...' % (errcnt, self.chanke_Name)

			with Timer('check'):
				if self.check():
					self.okEvent.set()
					print '!!!!成功预约%s!!!!' % self.chanke_Name
					dlg = msgbox.MsgBox('成功预约', '成功预约\n' + self.chanke_Name)
					dlg.mainloop()
					del dlg
					break

			errcnt += 1
			if self.errmax > 0 and errcnt >= self.errmax:
				break



