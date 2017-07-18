#!/usr/bin/python

print("Content-Type: text/plain\n")

import cgi,sys
form = cgi.FieldStorage()
symbol = form.getfirst('symbol')
if symbol is not None:
    sys.argv.append(symbol)
#sys.path.insert(0,'/data/data/com.termux/files/home/project/webapp1')
sys.path.insert(0,'/home/neotruss/public_html')
import p1
