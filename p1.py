#from html.parser import HTMLParser
from HTMLParser import HTMLParser
import requests,re,os,json,sys

class MyHTMLParser(HTMLParser,object):
    def __init__(self):
         super(MyHTMLParser,self).__init__()
         self.flag = False
         self.pl_iter = 0
         self.data_item = ''
         self.section = ''
         self.fin_data = {}; self.fin_data['header'] = {}
         # handle special cases
         self.tseF = False
         self.tseRC = 0
         self.cshF = False
         self.cshRC = 0
         self.depF = False
         self.depRC = 0
         self.stdF = False
         self.stdRC = 0


    def handle_starttag(self, tag, attrs):
        if tag == 'option':
            #print(attrs)
            for a,v in attrs:
                if 'selected' in str(a):
                    for suffix in ['income-statement','balance-sheet','cash-flow']:
                        if attrs[0][1].endswith(suffix):
                           #print(tag,suffix)
                           self.section = suffix
                           self.fin_data[self.section] = {}
                           self.fin_data[self.section]['period'] = period
                           break
        elif tag == 'span':
            for a,v in attrs:
                if a == 'class':
                    if v in ('companyName','tickerName','exchangeName'):
                        self.data_item = v
                elif a == 'id':
                    if v in ('quote_val'):
                        self.data_item = v
        if self.flag:
            pass
            #print("start tag:", tag)


    def handle_data(self, data):
        if self.tseRC == 0:
           m1 = re.search('Total Shareholders[.]*',data)
           try:
              if m1 is not None:
                 if self.tseRC == 0:
                     self.tseF = True
                     self.tseRC += 1 
                     #print(data)
           except:
              print "Unexpected error:", sys.exc_info()
              raise
              
        if self.cshRC == 0:
           m1 = re.search('[.]*Short Term Investments',data)
           try:
              if m1 is not None:
                 if self.cshRC == 0:
                     self.cshF = True
                     self.cshRC += 1 
                     #print(data)
           except:
              print "Unexpected error:", sys.exc_info()
              raise
           
        if self.depRC == 0:
           m1 = re.search('[.]*Amortization Expense',data)
           try:
              if m1 is not None:
                 if self.depRC == 0:
                     self.depF = True
                     self.depRC += 1 
                     #print(data)
           except:
              print "Unexpected error:", sys.exc_info()
              raise
              
        if self.stdRC == 0:
           m1 = re.search('ST Debt[.]*',data)
           try:
              if m1 is not None:
                 if self.stdRC == 0:
                     self.stdF = True
                     self.stdRC += 1 
                     #print(data)
           except:
              print "Unexpected error:", sys.exc_info()
              raise      
                 
             
        if 'Fiscal year' in data:
            self.flag = True
            self.pl_iter = 6
            #print("data  :", data)
            m = re.search('USD[ a-zA-Z]+',data)
            self.fin_data[self.section]['Data Unit'] = m.group(0)
            self.data_item = 'Year'
        elif self.data_item in ('companyName','tickerName','exchangeName','quote_val'):
            self.fin_data['header'][self.data_item] = data
            self.data_item = ''
        elif data in ['Sales/Revenue', 'Depreciation & Amortization Expense',\
                'EBIT', 'Interest Expense', 'Pretax Income', 'Income Tax',\
                'EPS (Diluted)', 'Diluted Shares Outstanding',\
                'Cash & Short Term Investments','Long-Term Note Receivable',\
                'Intangible Assets','Other Long-Term Investments',\
                'ST Debt & Current Portion LT Debt',\
                'Long-Term Debt',\
                'Total Shareholders\' Equity',\
                'Net Operating Cash Flow','Capital Expenditures','Cash Dividends Paid - Total']\
                  or self.tseF or self.cshF or self.depF or self.stdF:
            self.flag = True
            self.data_item = data
            self.pl_iter = 6
            if self.tseF and self.section == 'balance-sheet':      
               self.pl_iter += 1
               self.data_item += '\' Equity'
               #print(data)
               self.tseF = False
            elif self.stdF and self.section == 'balance-sheet':      
               self.pl_iter += 1
               self.data_item += '& Current Portion LT Debt'
               #print(data)
               self.stdF = False
            elif self.cshF and self.section == 'balance-sheet':     
               self.data_item = 'Cash &' + self.data_item
               #print(data)
               self.cshF = False
            elif self.depF and self.section == 'income-statement':     
               self.data_item = 'Depreciation &' + self.data_item
               #print(data)
               self.depF = False     

        if self.flag:
            if self.pl_iter >= 6:
                self.pl_iter -= 1
            elif self.pl_iter > 0:
                if data != ' ':
                    #print("data  :", data)
                    if self.pl_iter == 4:
                        if data != '-':
                            self.fin_data[self.section][self.data_item] = data
                        else:
                            self.fin_data[self.section][self.data_item] = '0'
                    self.pl_iter -= 1
                    if self.pl_iter == 0:
                        self.flag = False

if len(sys.argv) == 1:
    print ("Ticker symbol not present")
    sys.exit()

ticker = sys.argv[1].upper()
period = 'annual'
web_data = ''

try:
   parser = MyHTMLParser()
except:
   print "Unexpected error:", sys.exc_info()
   raise

euid = str(os.geteuid())
if euid == '10106':
    filedir = os.path.expandvars('$HOME/project/webapp1/data/')
    data_file = filedir+'p1_data_'+ticker+'_'+euid+'.txt'
    try:
        with open(data_file) as f:
            web_data = f.read()
    except FileNotFoundError:
        with open(data_file,'w') as f:
            for s in ['income-statement','balance-sheet','cash-flow']:
                url = 'http://quotes.wsj.com/'+ticker+'/financials/annual/'+s
                page = requests.get(url)
                #print(page.text)
                f.write(page.text)
                web_data += page.text
else:
    for s in ['income-statement','balance-sheet','cash-flow']:
        url = 'http://quotes.wsj.com/'+ticker+'/financials/annual/'+s
        page = requests.get(url)
        #print(repr(page.text))
        web_data += page.text

parser.feed(web_data)
parser.close()
"""
#print('{} sections'.format(len(parser.fin_data)))
for key,val in parser.fin_data.items():
    #print('Data from {}'.format(key))
    for a,b in val.items():
        print(key,a,':',b)
"""
print(json.dumps(parser.fin_data))
