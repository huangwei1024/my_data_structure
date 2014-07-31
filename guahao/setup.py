#!/usr/bin/python
# -*- coding: utf-8 -*-

from distutils.core import setup  
import py2exe
setup(
console=[{
	"script": "guahao.py", 
	"icon_resources": [(1, "16.ico")],
}],
data_files= [
	(".", ["user.config"])
]) 
