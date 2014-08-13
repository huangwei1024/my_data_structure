#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib
import urllib2 
import httplib
import cookielib
import zlib
import StringIO
import gzip
import os
import time
import random
import datetime
import multiprocessing

import msgbox
import debuglog
from debuglog import Timer, DebugLog


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
firstQueue = True
httpClient = None
errmax = 0


def http_gzip(data):
	compressedstream = StringIO.StringIO(data)
	gzipper = gzip.GzipFile(fileobj=compressedstream)
	return gzipper.read()

def make_cookies(cookieDict):
	return '; '.join(['%s=%s' % x for x in cookieDict.items()])

def is_valid_login_yzm(code):
	return len(code) == 4 and all([x.isdigit() for x in code])


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

import agent

# @profile
def main(user, passw):
	procs = []
	event = multiprocessing.Event()
	okEvent = multiprocessing.Event()

	with Timer('login'):
		login_ok = step_0(httpClient, user, passw)

	if not login_ok:
		print '登录不成功，请重试'
	else:
		print '开始刷号子', chanke_Name

		try:
			for i in xrange(5):
				proc = agent.Agent(args=(event, okEvent))
				proc.setInfo(cookieDict, chanke_Referer, chanke_Name, doctorname_Choice, errmax)
				procs.append(proc)

			for proc in procs:
				proc.start()

			print 'pid', os.getpid()
			print 'procs', [x.pid for x in procs]

			okEvent.wait()
			print 'okEvent wait end!'

		except Exception:
			pass

		finally:
			print '='*50
			print '抢号程序结束'
			for proc in procs:
				proc.terminate()

import argparse
def parseArgs():
	parser = argparse.ArgumentParser(description=utf2local("省妇保挂号程序"),\
		formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument('-ks', type=int, default=5, help=utf2local(''.join(['%d.%s' % (x[0],x[1][1]) for x in zip([i for i in xrange(len(cks))], cks)])))
	parser.add_argument('-n', type=int, default=0, help=utf2local('尝试次数，0表示无限尝试'))
	parser.add_argument('-d', '--docname', type=str, default='', help=utf2local('指定医生名字'))
	parser.add_argument('-c', '--config', action='store_false', default=True, help=utf2local('是否读取配表'))
	args = parser.parse_args()
	print args

	return args

if __name__ == '__main__':
	DebugLog('guahao', True)
	random.seed(time.time())
	multiprocessing.freeze_support()

	args = parseArgs()
	errmax = args.n
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

