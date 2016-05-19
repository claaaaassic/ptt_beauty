#-*- coding: utf-8 -*-
# ContentData.py
import re

class ContentData:

	def __init__(self, _content, _id):
		self.content = _content
		self.id = _id
		self.title = ''
	
	
		# 尋找標題 ## patton 還沒有打得很完美
	def title(self):
		tmp = re.findall('\[.{6}\].{1,60}', self.content)
		if tmp == None:
			return self.title
		else:
			self.title = tmp[0]
			return self.title


		# 尋找內文中的頁數號碼
	def searchPage(self):
	    tmp = re.search('(?<=[/])[0-9]{1,2}(?= 頁 \()', self.content) 
	    if tmp == None:
	        self.page = 2
	    else:
	        self.page = tmp.group(0)
	    return self.page


	    # 翻頁後文章內容新增進 content
	def addContent(self, contents):
		self.content = self.content + contents


		# 尋找可下載的 url 紀錄格式為 list
	def searchUrl(self):
		return re.findall('http://i?\.?imgur.com/[a-zA-Z0-9]{6,8}',self.content)


		# 去除怪異字元 # *[1;33m 這類的格式還沒做處理
	def contentReplace(self):
	    self.content = self.content.replace('','*')
	    self.content = self.content.replace('','')

	    
 