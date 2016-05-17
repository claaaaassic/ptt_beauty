#-*- coding: utf-8 -*-
import telnetlib
import requests
import shutil
import re
import time
import sys

import account


def login():

    tn = telnetlib.Telnet('ptt.cc')
    print '連接成功!!!'
    time.sleep(1)
    content = tn.read_very_eager().decode('big5','ignore')    #進站畫面   

    while '上方為使用者心情點播留言區，不代表本站立場' not in content.encode('utf-8'):

        while '系統過載' in content.encode('utf-8'):
            print('系統過載請稍候...')
            tn = telnetlib.Telnet('ptt.cc')
            content = tn.read_very_eager().decode('big5','ignore')
            time.sleep(1)

        if "以 new 註冊:" in content.encode('utf-8'):
            print 'login'
            # username = raw_input("username：")
            username = account.username()
            tn.write((username+"\r\n").encode('big5') )
            time.sleep(1)
            
            # password = raw_input("password：")
            password = account.password()
            tn.write((password+"\r\n").encode('big5'))
            time.sleep(1)
            content = tn.read_very_eager().decode('big5','ignore')


        if "密碼不對" in content.encode('utf-8'):
            print("密碼不對或無此帳號。程式結束")
            sys.exit()

        if "您想刪除其他重複登入的連線嗎" in content.encode('utf-8'):
            print("發現重複連線,刪除他...")
            tn.write("y\n".encode('big5') ) 
            time.sleep(1)
            content = tn.read_very_eager().decode('big5','ignore')
            print content

        while "任意鍵" in content.encode('utf-8'):
            print("資訊頁面，按任意鍵繼續...")
            tn.write("\r\n".encode('big5') )
            time.sleep(1)
            content = tn.read_very_eager().decode('big5','ignore')

        if '編輯器自動復原' in content.encode('utf-8'):
            print('編輯器自動復原：不復原')
            tn.write("q\n".encode('big5'))
            time.sleep(1)
            content = tn.read_very_eager().decode('big5','ignore')

        if '要刪除以上錯誤嘗試的記錄嗎' in content.encode('utf-8'):
            print '刪除以上錯誤嘗試的記錄'
            print re.findall('[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+',content)
            tn.write("y\n".encode('big5'))
            time.sleep(1)
            content = tn.read_very_eager().decode('big5','ignore')

    print '登入成功'
    return tn



def login_beauty( tn ):
    print '分組討論區'
    tn.write("\r\n".encode('big5') )
    time.sleep(1)
    
    print '生活娛樂館'
    tn.write("nnnnnnnnr".encode('big5') )
    time.sleep(1)
    
    print '聊天'
    tn.write("nnnnnnnnnnnnnnnnr".encode('big5') )
    time.sleep(1)
    
    print '進入beauty'
    tn.write("nr".encode('big5') )
    time.sleep(1)
    content = tn.read_very_eager().decode('big5','ignore')
    

    while "任意鍵" in content.encode('utf-8'):
        print '請按任意鍵繼續' 
        tn.write("\r\n".encode('big5'))
        time.sleep(0.5)
        content = tn.read_very_eager().decode('big5','ignore')
        printContent(content)



def download( url ):
   
    tmp = re.findall('(?<=imgur.com/)[a-zA-Z0-9]+',url)
    fname = tmp[0] + '.jpg'
    res = requests.get( url + '.jpg' , stream = True , timeout = 10.0 )         
    f = open( fname, 'wb' )
    shutil.copyfileobj( res.raw , f )
    f.close()
    del res


def content_replace(content):
    content = content.replace('','*')
    content = content.replace('','')
    # content = content.replace('<em>','')
    # content = content.replace('</em>','')
    # content = content.replace('&hellip;','...')
    # content = content.replace('&lt;','<')
    # content = content.replace('&ctdot;','...')
    # content = content.replace('&amp;','&')
    # content = content.replace('&mdash;','—')
    # content = content.replace('&nbsp;','')
    return content


def searchPage(content):
    tmp = re.search('(?<=[/])[0-9]{1,2}(?= 頁 \()',content) 
    if tmp == None:
        page = 2
    else:
        page = tmp.group(0)
    return page


def printContent(content):
    print content_replace(content.encode('utf-8'))


# *[1;33m 這類的格式要做處理
# def fontcolor_replace(content):
#     return 

def main():

    start = time.time()

    tn = login()
    login_beauty( tn )

    # number_start = int(raw_input("輸入起始頁碼："))
    # number_end = int(raw_input("輸入結束頁碼："))

    number_start = 36421
    number_range = 50

    tn.write((str(number_start)+"\r\n").encode('big5') )     # 跳至第幾項 
    time.sleep(1)
    tn.write("r".encode('big5') )  # 進入
    time.sleep(1)
    content = tn.read_very_eager().decode('big5','ignore')


    print 'download now !' 
    for i in range(searchPage(content)):                                               #search page 1
        url_list = re.findall('http://i?.?imgur.com/[a-zA-Z0-9]+',content) 

        for url in url_list:
            download(url)
            print 'url : ' + url + '.jpg'
             
        tn.write( "PgDn".encode('big5') )
        time.sleep(1)
        content = tn.read_very_eager().decode('big5','ignore')

   
    for i in range(number_range):        

        tn.write( "b".encode( 'big5' ) )
        time.sleep(1)
        content = tn.read_very_eager().decode( 'big5' , 'ignore' )   #讀內文
        printContent(content)
     
        while '請按任意鍵繼續' in content.encode('utf-8'):
            tn.write( "\nkr".encode( 'big5' ) )
            time.sleep(1)
            content = tn.read_very_eager().decode( 'big5' , 'ignore' )
                
        for i in range(searchPage(content)):       
            url_list = re.findall('http://i?.?imgur.com/[a-zA-Z0-9]+',content) 

            for url in url_list:
                download(url)
                 
            tn.write( "PgDn".encode('big5') )
            time.sleep(1)
            content = tn.read_very_eager().decode('big5','ignore')
          

    print "log out......" 

    tn.write("qqqqqqqqqg\r\ny\r\n".encode('big5') )            #登出
    time.sleep(1)
    tn.write("\r\n".encode('big5') )

    end = time.time()
    print end-start

if __name__ == '__main__' :  
    main()
