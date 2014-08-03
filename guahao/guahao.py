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
import threading
import traceback

import msgbox
import debuglog

nowtime = lambda : str(datetime.datetime.now())
rndistr = lambda : str(random.randint(1000000000, 9999999999))

# http://guahao.zjol.com.cn/update/Area.xml

# 浙江大学医学院附属妇产科医院 --【普通产科】
ck1 = ('http://guahao.zjol.com.cn/DepartMent.Aspx?ID=9294', '【普通产科】')
# 浙江大学医学院附属妇产科医院 --【产科名医】
ck2 = ('http://guahao.zjol.com.cn/DepartMent.Aspx?ID=9272', '【产科名医】')
# 浙江大学医学院附属妇产科医院 --【产科专家】
ck3 = ('http://guahao.zjol.com.cn/DepartMent.Aspx?ID=9273', '【产科专家】')
# 测试科室
ck_test = ('http://guahao.zjol.com.cn/DepartMent.Aspx?ID=9137', '测试科室')

# 浙江大学医学院附属第二医院 --【眼科名医门诊】孙朝晖 
yk = ('http://guahao.zjol.com.cn/DepartMent.Aspx?ID=10102', '【眼科名医门诊】')

cks = [ck1, ck2, ck3, yk, ck_test]
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
httpClient = httplib.HTTPConnection("guahao.zjol.com.cn", 80)
yyProcess = None
yyQueue = multiprocessing.Queue(100)
yyEvent  = multiprocessing.Event()


def http_gzip(data):
	compressedstream = StringIO.StringIO(data)
	gzipper = gzip.GzipFile(fileobj=compressedstream)
	return gzipper.read()

def make_cookies(cookieDict):
	return '; '.join(['%s=%s' % x for x in cookieDict.items()])

def is_valid_login_yzm(code):
	return len(code) == 4 and all([x.isdigit() for x in code])

import Queue
def put_que(dlist, ev, que):
	try:
		dlist = dlist
		que.put_nowait(dlist)
	except Queue.Full:
		# print 'put_que is FULL', ttt
		ev.clear()
		while not que.empty():
			que.get()
		que.put(dlist)
		ev.set()

def get_que(ev, que):
	ev.wait()
	ret = que.get()
	empty = False
	while not empty:
		try:
			ret = que.get_nowait()
		except Queue.Empty:
			empty = True
	# print 'get_que', ret[0]
	return ret

def refresh_yy(ev, que, headers):
	global sgList

	httpClient = httplib.HTTPConnection("guahao.zjol.com.cn", 80)

	while True:
		try:
			sg = step_1(httpClient, headers)
			if sg is None:
				time.sleep(1)
				continue

			# step 2
			body = urllib.urlencode({'sg': sg})
			httpClient.request("POST", "/ashx/gethy.ashx", body, headers)
			response = httpClient.getresponse()
			data = response.read()

			if response.status != 200:
				print '[refresh_yy] gethy POST Error', response.status, response.reason
				continue

			dlist = data.split('#')
			if len(dlist) < 12:
				print '[refresh_yy] gethy POST Response Error', data
				continue

			orders = dlist[11].split('$')[1:]
			if len(orders) == 0:
				sgList = sgList[1:] # 下个预约日
			else:
				put_que(dlist, ev, que)

		except Exception:
			traceback.print_exc()
			httpClient.close()
			print '[refresh_yy] 重连服务器'
			httpClient = httplib.HTTPConnection("guahao.zjol.com.cn", 80)


def step_0(usr, pwd):
	global httpClient

	# get cookie, ASP.NET_SessionId
	cj = cookielib.CookieJar()
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj), urllib2.HTTPHandler())
	req = urllib2.Request('http://guahao.zjol.com.cn/Default.Aspx')
	f = opener.open(req)
	data = f.read()
	for cookie in cj:
		cookieDict[cookie.name] = cookie.value
		
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

	# step 1
	headers["Referer"] = chanke_Referer

	httpClient.request("GET", chanke_Referer, headers=headers)
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
		reg = r'<td height="45px"><a href="DoctorInfo\.Aspx[^<]*<b class="red12">(?P<name>%s)</b>(?P<yy>.*?)</tr>' % doctorname_Choice
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

def check():
	global sgList
	global yzm_filename
	global httpClient
	global user_info
	global user_qh_cnt
	global yyQueue

	try:
		dlist = get_que(yyEvent, yyQueue)
		if dlist is None or len(dlist) == 0:
			return False

		hospital = dlist[1]
		office = dlist[2]
		doctor = dlist[3]
		patient = dlist[6]
		date = dlist[8]
		mgenc = dlist[12]
		orders = dlist[11].split('$')[1:]

		print ' '.join([patient, hospital, office, doctor, date])
		print '一共有',len(orders), '个号子'

		# 读顺序配置
		cur_choose = 1
		if len(user_info) > 0 and len(user_info['qh_shunxu']) > 0:
			for i in xrange(len(user_info['qh_shunxu'])):
				cur_choose = user_info['qh_shunxu'][(i + user_qh_cnt) % len(user_info['qh_shunxu'])] -1
				if cur_choose < len(orders):
					user_qh_cnt += i + 1
					break
		else:
			cur_choose = random.randint(1, min(3, len(orders) - 1))

		# 一次预取3个号子验证码
		for i in xrange(3):
			cur_choose += i
			if cur_choose >= len(orders):
				cur_choose = random.randint(0, len(orders) - 1)
			order = orders[cur_choose]

			# step 3
			hyid, number, time, flag = order.split('|')
			print '选择了第%d个' % cur_choose
			print number, '号 /', time[:2], ':', time[2:], hyid
			yanzhenma_URL = yanzhenma_URL_f % hyid
			yzm_filename = yzm_filename_f % hyid

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

			# yzm = raw_input('input %s code (empty use OCR):' % yzm_filename)

			msg = '\n'.join([patient, hospital, office, doctor, date]) + '\n'
			msg += '-'*20 + '\n'
			msg += '一共有%d个号子\n选择了第%d个\n' % (len(orders), cur_choose + 1)
			msg += ''.join([number, '号/', time[:2], ':', time[2:]])
			dlg = msgbox.InputBox(title ='预约', imgfile = yzm_filename, msg = msg)
			dlg.mainloop()
			yzm = dlg.code
			del dlg

			if len(yzm) == 0:
				yzm = 'xxxxx'
			print '验证码输入为', yzm

			lgcfas = hyid
			xh = number
			qhsj = time
			sg = mgenc

			# step 4.
			body = urllib.urlencode({'sg': sg, 'lgcfas':lgcfas, 'yzm':yzm, 'xh':xh, 'qhsj':qhsj})
			httpClient.request("POST", '/ashx/TreadYuyue.ashx', body, headers)
			response = httpClient.getresponse()
			data = response.read()

			if response.status != 200:
				print 'step 4. POST TreadYuyue error', response.status, response.reason
				print response.read()
				continue
			
			print data
			rlst = data.split('|')
			if len(rlst) == 0 or rlst[0] == 'ERROR':
				continue

			return True

		return False


	except httplib.CannotSendRequest, e:
		traceback.print_exc()
		httpClient.close()
		print '重连服务器'
		httpClient = httplib.HTTPConnection("guahao.zjol.com.cn", 80)
		return False

	except httplib.BadStatusLine, e:
		traceback.print_exc()
		return False

	except Exception:
		import traceback
		traceback.print_exc()
		return False

import argparse

def parseArgs():
	parser = argparse.ArgumentParser(description="省妇保挂号程序",\
		formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument('-ks', type=int, default=4, help=''.join(['%d.%s' % (x[0],x[1][1]) for x in zip([i for i in xrange(len(cks))], cks)]))
	parser.add_argument('-n', type=int, default=0, help='尝试次数，0表示无限尝试，默认10次')
	parser.add_argument('-d', '--docname', type=str, default='', help='指定医生名字')
	args = parser.parse_args()
	return args

if __name__ == '__main__':
	args = parseArgs()
	print args

	chanke_Choice = args.ks
	chanke_Referer, chanke_Name = cks[args.ks]
	yzm_filename = str(time.time() + random.random() * 100000000) + '.png'
	if args.docname:
		doctorname_Choice = args.docname

	# while len(user_info) == 0:
	# 	dlg = msgbox.SelectBox()
	# 	dlg.mainloop()
	# 	user_info = dlg.userInfo
	# 	del dlg
	# print '选择了用户', user_info['name']
	# print user_info['yiyuan'], user_info['keshi'], user_info['yishen']
	
	# login_ok = step_0(user_info['id'], user_info['password'])
	login_ok = step_0('33100319861024003X', 'huangwei')
	if not login_ok:
		print '登录不成功，请重试'
	else:
		print '开始刷号子', chanke_Name

		yyProcess = multiprocessing.Process(target=refresh_yy, args=(yyEvent, yyQueue, headers))
		yyProcess.start()
		yyEvent.set()

		errcnt = 0
		errmax = args.n
		while True:
			print '-'*50
			print nowtime(), '第%d次尝试%s...' % (errcnt, chanke_Name)
			if check():
				print '!!!!成功预约%s!!!!' % chanke_Name
				dlg = msgbox.MsgBox('成功预约', '成功预约\n' + chanke_Name)
				dlg.mainloop()
				del dlg
				break
			# time.sleep(1)
			errcnt += 1
			if errmax > 0 and errcnt >= errmax:
				break

		yyProcess.terminate()


