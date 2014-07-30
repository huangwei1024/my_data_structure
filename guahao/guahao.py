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
from PIL import Image

import msgbox


utf2gbk = lambda x: x.decode('utf8').encode('gbk')
utf2uni = lambda x: x.decode('utf8')
gbk2utf = lambda x: x.decode('gbk').encode('utf8')
rndistr = lambda : str(random.randint(1000000000, 9999999999))

# 浙江大学医学院附属妇产科医院 --【普通产科】
ck1 = ('http://guahao.zjol.com.cn/DepartMent.Aspx?ID=9294', '【普通产科】')
# 浙江大学医学院附属妇产科医院 --【产科名医】
ck2 = ('http://guahao.zjol.com.cn/DepartMent.Aspx?ID=9272', '【产科名医】')
# 浙江大学医学院附属妇产科医院 --【产科专家】
ck3 = ('http://guahao.zjol.com.cn/DepartMent.Aspx?ID=9273', '【产科专家】')
# 测试科室
ck_test = ('http://guahao.zjol.com.cn/DepartMent.Aspx?ID=197', '测试科室')

# 浙江大学医学院附属第二医院 --【眼科名医门诊】孙朝晖 
yk = ('http://guahao.zjol.com.cn/DepartMent.Aspx?ID=10102', '【眼科名医门诊】')

cks = [ck1, ck2, ck3, yk, ck_test]
chanke_Referer, chanke_Name = cks[0]
chanke_Choice = 0
doctorname_Choice = ''

yzm_filename = 'yyzm.png'
loginyzm_filename = 'yzm.png'


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
				# 'Hm_lvt_e480108ab2cee67da5ec65023fd1b941': ','.join([rndistr() for i in xrange(3)]), 
				# 'Hm_lpvt_e480108ab2cee67da5ec65023fd1b941': rndistr(),
				# 'Hm_lvt_419cfa1cc17e2e1dc6d4f431f8d19872': ','.join([rndistr() for i in xrange(4)]), 
				# 'Hm_lpvt_419cfa1cc17e2e1dc6d4f431f8d19872': rndistr(),
				'CNZZDATA30020775': 'cnzz_eid%3D833334187-1405072273-null%26ntime%3D' + rndistr(),
}
httpClient = httplib.HTTPConnection("guahao.zjol.com.cn", 80)
autoOCR = False



def http_gzip(data):
	compressedstream = StringIO.StringIO(data)
	gzipper = gzip.GzipFile(fileobj=compressedstream)
	return gzipper.read()

def get_cookies():
	return '; '.join(['%s=%s' % x for x in cookieDict.items()])

# def ocr_scan(filename, allnum = False, delA = False):
# 	img = Image.open(filename)
# 	if delA:
# 		r, g, b, a = img.split()
# 		img = Image.merge("RGB", (r, g, b))
# 	# newname = '_%f.bmp' % random.random() * 100000000
# 	# img.save(newname)

# 	code = image_to_string(img).strip()
# 	clist = []
# 	for i in code:
# 		if allnum:
# 			if i.isdigit():
# 				clist.append(i)
# 		else:
# 			if i.isalnum():
# 				clist.append(i)
# 	print '[OCR DEBUG]', code
# 	return ''.join(clist)

def is_valid_login_yzm(code):
	return len(code) == 4 and all([x.isdigit() for x in code])

def step_0(usr, pwd):
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
		headers['Cookie'] = get_cookies()
		httpClient.request("GET", '/VerifyCodeCH.aspx', headers=headers)
		response = httpClient.getresponse()
		if response.status != 200:
			print 'step 0. GET login yzm error', response.status, response.reason
			return False

		encoding = response.getheader('Content-Encoding')
		data = response.read()
		if encoding == 'gzip':
			data = http_gzip(data)

		fp = open(loginyzm_filename, 'wb')
		fp.write(data)
		fp.close()


		if not autoOCR:
			while True:
				dlg = msgbox.InputBox(title ='登录', imgfile = loginyzm_filename, msg = '登录验证码\n')
				dlg.mainloop()
				yzm = dlg.code
				del dlg

				if len(yzm) == 0:
					yzm = ocr_code

				print u'账户登录验证码输入为', yzm
				if not is_valid_login_yzm(yzm):
					print u'验证码应该是4位数字，请检查'
					continue
				break
		else:
			if not is_valid_login_yzm(yzm):
				continue

		# login
		login_URL = login_URL_f % (usr, pwd, yzm)
		httpClient.request("GET", login_URL, headers=headers)
		response = httpClient.getresponse()
		if response.status != 200:
			print 'step 0. GET login error', response.status, response.reason
			return False

		data = response.read()
		dlist = data.split('|')

		if len(dlist) == 2:
			cookieDict['UserId'] = dlist[1]
			headers['Cookie'] = get_cookies()
			return True
		else:
			print utf2gbk(data)

	return False

def step_1():
	global sgList

	if len(sgList) > 0:
		return sgList[0]

	# step 1
	headers["Referer"] = chanke_Referer

	httpClient.request("GET", chanke_Referer, headers=headers)
	response = httpClient.getresponse()
	if response.status != 200:
		print 'step 1. GET Error', response.status, response.reason
		return False

	encoding = response.getheader('Content-Encoding')
	data = response.read()
	if encoding == 'gzip':
		data = http_gzip(data)
	sgList = re.findall(r"javascript:showDiv\('(?P<sg>[^']*)'\)", data)
	if len(sgList) == 0:
		print u'没有可预约的!'
		return None
	return sgList[0]

def check():
	global sgList
	global yzm_filename

	try:
		sg = step_1()
		if sg is None:
			return False

		# step 2
		body = urllib.urlencode({'sg': sg})
		httpClient.request("POST", "/ashx/gethy.ashx", body, headers)
		response = httpClient.getresponse()
		if response.status != 200:
			print 'step 2. POST Error', response.status, response.reason
			return False
		data = response.read()

		dlist = data.split('#')
		if len(dlist) < 12:
			print 'step 2. POST Response Error', data
			return False
# 		var s = msg.split('#');
#       var sfz = s[5];
#       var xm = s[6];
#       var yymc = s[1];
#       var ksmc = s[2];
#       var ysmc =s[3];
#       var ghf = s[10];
#       var jzrq=s[8];
#       var mgenc=s[12];
		hospital = dlist[1]
		office = dlist[2]
		doctor = dlist[3]
		patient = dlist[6]
		date = dlist[8]
		mgenc = dlist[12]
		orders = dlist[11].split('$')[1:]

		print u' '.join([utf2uni(x) for x in [patient, hospital, office, doctor, date]])
		print u'一共有',len(orders),u'个号子'

		if len(orders) == 0:
			sgList = sgList[1:] # 下个预约日
			return False
		
		if True:
			order = orders[0] # 第一个号子
			if len(orders) > 1:
				order = orders[1]

			# step 3
			hyid, number, time, flag = order.split('|')
			print number, u'号 /', time[:2], ':', time[2:], hyid
			yanzhenma_URL = yanzhenma_URL_f % hyid

			httpClient.request("GET", yanzhenma_URL, headers=headers)
			response = httpClient.getresponse()
			if response.status != 200:
				print 'step 3. GET yzm error', response.status, response.reason
				return False

			encoding = response.getheader('Content-Encoding')
			data = response.read()
			if encoding == 'gzip':
				data = http_gzip(data)

			fp = open(yzm_filename, 'wb')
			fp.write(data)
			fp.close()

			# yzm = raw_input('input %s code (empty use OCR):' % yzm_filename)

			msg = '\n'.join([patient, hospital, office, doctor, date]) + '\n'
			msg += '-'*20 + '\n'
			msg += '一共有' + str(len(orders)) + '个号子\n'
			msg += ''.join([number, '号/', time[:2], ':', time[2:]])
			dlg = msgbox.InputBox(title ='预约', imgfile = yzm_filename, msg = msg)
			dlg.mainloop()
			yzm = dlg.code
			del dlg

			if len(yzm) == 0:
				yzm = 'xxxxx' # ocr_code
			print u'验证码输入为', yzm

			lgcfas = hyid
			xh = number
			qhsj = time
			sg = mgenc

			# step 4.
			body = urllib.urlencode({'sg': sg, 'lgcfas':lgcfas, 'yzm':yzm, 'xh':xh, 'qhsj':qhsj})
			httpClient.request("POST", '/ashx/TreadYuyue.ashx', body, headers)
			response = httpClient.getresponse()

			if response.status != 200:
				print 'step 4. POST TreadYuyue error', response.status, response.reason
				print response.read()
				return False

			data = response.read()
			print utf2uni(data)
			rlst = data.split('|')
			if len(rlst) == 0 or rlst[0] == 'ERROR':
				# print response.getheaders()
				return False

		return True

		# print response.status, response.reason
		# print response.getheaders()
		# print response.read()

	except Exception:
		import traceback
		traceback.print_exc()
		print 'httpClient sock',httpClient.sock
		return False

import argparse

def parseArgs():
	parser = argparse.ArgumentParser(description=utf2gbk("省妇保挂号程序"),\
		formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument('ks', type=int, help=utf2gbk(''.join(['%d.%s' % (x[0],x[1][1]) for x in zip([i for i in xrange(len(cks))], cks)])))
	parser.add_argument('-n', type=int, default=10, help=utf2gbk('尝试次数，0表示无限尝试，默认10次'))
	parser.add_argument('-d', '--docname', type=str, default=None, help=utf2gbk('指定医生名字'))
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
	
	login_ok = step_0('341822200510110021', '20051011')
	if not login_ok:
		print u'登录不成功，请重试'
	else:
		print u'开始刷号子', utf2uni(chanke_Name)

		errcnt = 0
		errmax = args.n
		while True:
			print '-'*50
			print time.time(), u'第%d次尝试%s...' % (errcnt, utf2uni(chanke_Name))
			if check():
				print u'!!!!成功预约%s!!!!' % utf2uni(chanke_Name)
				dlg = msgbox.MsgBox('成功预约', '成功预约\n' + chanke_Name)
				dlg.mainloop()
				del dlg
				break
			# time.sleep(1)
			errcnt += 1
			if errmax > 0 and errcnt >= errmax:
				break
