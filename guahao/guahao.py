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
import os
import time
import random
import datetime
import multiprocessing
import traceback

import msgbox
import debuglog

nowtime = lambda : str(datetime.datetime.now())
rndistr = lambda : str(random.randint(1000000000, 9999999999))
utf2local = debuglog.utf2local

# http://guahao.zjol.com.cn/update/Area.xml

# ERROR|10000001平台前置通讯异常,该号不能预约 
# ERROR|交易接口,验证码校验失败,该号不能预约
# ERROR|操作失败,您的预约过于频繁,请稍候再试,该号不能预约

# 浙江大学医学院附属妇产科医院 --【普通产科】
ck1 = ('http://guahao.zjol.com.cn/DepartMent.Aspx?ID=9294', '普通产科')
# 浙江大学医学院附属妇产科医院 --【产科名医】
ck2 = ('http://guahao.zjol.com.cn/DepartMent.Aspx?ID=9272', '产科名医')
# 浙江大学医学院附属妇产科医院 --【产科专家】
ck3 = ('http://guahao.zjol.com.cn/DepartMent.Aspx?ID=9273', '产科专家')
# 浙江大学医学院附属妇产科医院 --【产科资深专家】
ck4 = ('http://guahao.zjol.com.cn/DepartMent.Aspx?ID=10635', '产科资深专家')

# 浙江大学医学院附属第二医院 --【眼科名医门诊】孙朝晖 
yk = ('http://guahao.zjol.com.cn/DepartMent.Aspx?ID=10102', '眼科名医门诊')

# 测试科室
ck_test = ('http://guahao.zjol.com.cn/DepartMent.Aspx?ID=9137', '测试科室')


cks = [ck1, ck2, ck3, ck4, yk, ck_test]
chanke_Referer, chanke_Name = cks[0]
chanke_Choice = 0
doctorname_Choice = ''
user_info = {}
user_qh_cnt = 0

yzm_filename = 'yyzm.png'
loginyzm_filename = 'yzm.png'
yzm_filename_f = 'hyid%s.png'

yanzhenma_URL_f = 'http://guahao.zjol.com.cn/ashx/getyzm.aspx?k=7173&t=yy&hyid=%s'
login_URL_f = 'http://guahao.zjol.com.cn/ashx/LoginDefault.ashx?idcode=%s&pwd=%s&txtVerifyCode=%s'

headers = {"Content-type": "application/x-www-form-urlencoded",
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
sgList = []
cookieDict = {'pgv_pvi': rndistr(), 
				'pgv_si': rndistr(),
				'BAIDU_DUP_lcr': 'https://www.google.com.hk/',
				'CNZZDATA30020775': 'cnzz_eid%3D833334187-1405072273-null%26ntime%3D' + rndistr(),
}
yyQueue = None
firstQueue = True
httpClient = None

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

def http_gzip(data):
	compressedstream = StringIO.StringIO(data)
	gzipper = gzip.GzipFile(fileobj=compressedstream)
	return gzipper.read()

def make_cookies(cookieDict):
	return '; '.join(['%s=%s' % x for x in cookieDict.items()])

def is_valid_login_yzm(code):
	return len(code) == 4 and all([x.isdigit() for x in code])

# @profile
def refresh_yy(que, headers):
	global sgList
	global httpClient

	info = {}
	cur_choose = 0

	while True:
		try:
			with Timer('refresh_yy GET sg'):
				sg = step_1(httpClient, headers)
				if sg is None:
					break

			with Timer('refresh_yy GET dlist'):
				dlist = step_2(httpClient, sg, headers)
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
				sgList = sgList[1:] # 下个预约日
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
				
			sgList = sgList[1:] # 下个预约日
			# sgList = [] # for debug
			if len(sgList) == 0:
				break
			# time.sleep(1)

		except httplib.CannotSendRequest:
			traceback.print_exc()
			print '[refresh_yy] 重连服务器'
			with Timer('refresh_yy re-connect'):
				httpClient.close()
				httpClient = httplib.HTTPConnection("guahao.zjol.com.cn", 80)
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
				httpClient.close()
				httpClient = httplib.HTTPConnection("guahao.zjol.com.cn", 80)
			cur_choose -= 1
			continue

	print '[refresh_yy] OK', len(que)
	return que

def step_0(httpClient, usr, pwd):

	# get cookie, ASP.NET_SessionId
	cj = cookielib.CookieJar()
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj), urllib2.HTTPHandler())
	req = urllib2.Request('http://guahao.zjol.com.cn/Default.Aspx')
	f = opener.open(req)
	data = f.read()
	for cookie in cj:
		cookieDict[cookie.name] = cookie.value
		print cookie.name, cookie.value
		
	for i in xrange(10):
		# get login yzm png
		headers['Cookie'] = make_cookies(cookieDict)
		httpClient.request("GET", '/VerifyCodeCH.aspx', headers=headers)
		response = httpClient.getresponse()
		encoding = response.getheader('Content-Encoding')
		data = response.read()

		if response.status != 200:
			print 'step 0. GET login yzm error', response.status, response.reason
			return False

		if encoding == 'gzip':
			data = http_gzip(data)

		fp = open(loginyzm_filename, 'wb')
		fp.write(data)
		fp.close()

		while True:
			msg = '登录验证码\n'
			dlg = msgbox.InputBox(title ='登录', imgfile = loginyzm_filename, msg = msg)
			dlg.mainloop()
			yzm = dlg.code
			del dlg

			print '账户登录验证码输入为', yzm
			if not is_valid_login_yzm(yzm):
				print '验证码应该是4位数字，请检查'
				continue
			break
		

		# login
		login_URL = login_URL_f % (usr, pwd, yzm)
		httpClient.request("GET", login_URL, headers=headers)
		response = httpClient.getresponse()
		data = response.read()

		if response.status != 200:
			print 'step 0. GET login error', response.status, response.reason
			return False

		dlist = data.split('|')
		if len(dlist) == 2:
			cookieDict['UserId'] = dlist[1]
			headers['Cookie'] = make_cookies(cookieDict)
			return True
		else:
			print data

	return False

def step_1(httpClient, headers):
	global sgList

	if len(sgList) > 0:
		return sgList[0]

	httpClient.request("GET", headers["Referer"], headers=headers)
	response = httpClient.getresponse()
	encoding = response.getheader('Content-Encoding')
	data = response.read()

	if response.status != 200:
		print 'step 1. GET Error', response.status, response.reason
		return None

	if encoding == 'gzip':
		data = http_gzip(data)

	# find doctor
	if len(doctorname_Choice) > 0:
		reg = r'<td height="45px">.*?<b class="red12">(?P<name>%s)</b>(?P<yy>.*?)</tr>' % doctorname_Choice
		result = ""
		match = re.search(reg, data, re.DOTALL)
		if match:
			result = match.group("yy")
		if len(result) != 0:
			data = result
		else:
			print '没有指定医生 %s!' % doctorname_Choice
			return None

	sgList = re.findall(r"javascript:showDiv\('(?P<sg>[^']*)'\)", data)
	if len(sgList) == 0:
		print '没有可预约的!'
		return None
	return sgList[0]

def step_2(httpClient, sg, headers):
	body = urllib.urlencode({'sg': sg})
	httpClient.request("POST", "/ashx/gethy.ashx", body, headers)
	response = httpClient.getresponse()
	data = response.read()

	if response.status != 200:
		print 'step 2. gethy POST Error', response.status, response.reason
		return None

	dlist = data.split('#')
	if len(dlist) < 12:
		print 'step 2. gethy POST Response Error', data
		return None
	return dlist

def step_3(httpClient, yanzhenma_URL, yzm_filename, headers):
	httpClient.request("GET", yanzhenma_URL, headers=headers)
	response = httpClient.getresponse()
	encoding = response.getheader('Content-Encoding')
	data = response.read()

	if response.status != 200:
		print 'step 3. GET yzm error', response.status, response.reason
		return False

	if encoding == 'gzip':
		data = http_gzip(data)

	fp = open(yzm_filename, 'wb')
	fp.write(data)
	fp.close()
	return True

# @profile
def check(httpClient):
	global firstQueue
	global yzm_filename
	global user_info
	global user_qh_cnt
	global yyQueue

	while len(yyQueue) > 0:
		try:
			# 读顺序配置
			yy_choose = 1 if firstQueue else 0
			if len(yyQueue) == 1:
				yy_choose = 0
			else:
				if len(user_info) > 0 and len(user_info['qh_shunxu']) > 0:
					for i in xrange(len(user_info['qh_shunxu'])):
						yy_choose = user_info['qh_shunxu'][(i + user_qh_cnt) % len(user_info['qh_shunxu'])] -1
						if yy_choose < len(yyQueue):
							user_qh_cnt += i + 1
							break
				else:
					if len(yyQueue) > 10:
						# 号子多时前3个随机
						yy_choose = random.randint(1 if firstQueue else 0, min(1, len(yyQueue) - 1))

			yy_choose = yy_choose % len(yyQueue)
			info = yyQueue[yy_choose]
			yyQueue = yyQueue[yy_choose+1:]
			firstQueue = False

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

			# 下载验证码
			with Timer('GET yanzhenma'):
				yanzhenma_URL = info['yanzhenma_URL']
				if not step_3(httpClient, yanzhenma_URL, yzm_filename, headers):
					return False
			
			# yzm = raw_input('input %s code (empty use OCR):' % yzm_filename)

			msg = '\n'.join([patient, hospital, office, doctor, date]) + '\n'
			msg += '-'*20 + '\n'
			msg += '一共有%d个号子\n选择了第%d个\n' % (n_orders, cur_choose)
			msg += ''.join([number, '号/', time_s])
			dlg = msgbox.InputBox(title ='预约', imgfile = yzm_filename, msg = msg)
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
				httpClient.request("POST", '/ashx/TreadYuyue.ashx', body, headers)
				response = httpClient.getresponse()
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
				httpClient.close()
				httpClient = httplib.HTTPConnection("guahao.zjol.com.cn", 80)
			return False

		except httplib.BadStatusLine:
			traceback.print_exc()
			return False

		except Exception:
			traceback.print_exc()
			print '重连服务器'
			with Timer('re-connect'):
				httpClient.close()
				httpClient = httplib.HTTPConnection("guahao.zjol.com.cn", 80)
			return False

# @profile
def main(user, passw):
	global yyQueue
	global yyEvent
	global httpClient
	global headers

	with Timer('login'):
		login_ok = step_0(httpClient, user, passw)

	if not login_ok:
		print '登录不成功，请重试'
	else:
		print '开始刷号子', chanke_Name

		# yyProcess = multiprocessing.Process(target=refresh_yy, args=(yyEvent, yyQueue, headers))
		# yyProcess.start()
		# yyEvent.set()

		with Timer('refresh_yy'):
			yyQueue = refresh_yy([], headers)

		try:
			errcnt = 0
			errmax = args.n
			while True:
				print '-'*50
				print nowtime(), '第%d次尝试%s...' % (errcnt, chanke_Name)

				with Timer('check'):
					if check(httpClient):
						print '!!!!成功预约%s!!!!' % chanke_Name
						dlg = msgbox.MsgBox('成功预约', '成功预约\n' + chanke_Name)
						dlg.mainloop()
						del dlg
						break

				if len(yyQueue) == 0:
					with Timer('refresh_yy'):
						yyQueue = refresh_yy([], headers)
				# time.sleep(1)
				errcnt += 1
				if errmax > 0 and errcnt >= errmax:
					break
		finally:
			print '='*50
			print '抢号程序结束'
			# yyProcess.terminate()

import argparse
def parseArgs():
	parser = argparse.ArgumentParser(description=utf2local("省妇保挂号程序"),\
		formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument('-ks', type=int, default=5, help=utf2local(''.join(['%d.%s' % (x[0],x[1][1]) for x in zip([i for i in xrange(len(cks))], cks)])))
	parser.add_argument('-n', type=int, default=0, help=utf2local('尝试次数，0表示无限尝试'))
	parser.add_argument('-d', '--docname', type=str, default='', help=utf2local('指定医生名字'))
	parser.add_argument('-c', '--config', action='store_true', help=utf2local('是否读取配表'))
	args = parser.parse_args()
	return args

if __name__ == '__main__':
	random.seed(time.time())
	multiprocessing.freeze_support()
	yyQueue = multiprocessing.Queue(1000)
	yyEvent  = multiprocessing.Event()

	args = parseArgs()
	print args

	chanke_Choice = args.ks
	chanke_Referer, chanke_Name = cks[args.ks]
	yzm_filename = str(time.time() + random.random() * 100000000) + '.png'
	if args.docname:
		doctorname_Choice = args.docname
	headers["Referer"] = chanke_Referer

	httpClient = httplib.HTTPConnection("guahao.zjol.com.cn", 80)

	# 配表加载
	if args.config:
		while len(user_info) == 0:
			dlg = msgbox.SelectBox()
			dlg.mainloop()
			user_info = dlg.userInfo
			del dlg
		print '选择了用户', user_info['name']
		print user_info['yiyuan'], user_info['keshi'], user_info['yishen']

		for x in cks:
			if x[1] == user_info['keshi']:
				chanke_Referer, chanke_Name = x
				headers["Referer"] = chanke_Referer
				break
		doctorname_Choice = user_info['yishen']
		
		user = user_info['id']
		passw = user_info['password']
	else:
		user = '33100319861024003X'
		passw = 'huangwei'

	# import profile
	# profile.run('main(user, passw)')
	main(user, passw)

