#-*- coding: utf-8 -*-
import telnetlib
import requests
import shutil
import re
import time
import sys

import account
import ContentData


HOST = 'ptt.cc'
number_start = 36000
search_range = 10


def login():

    tn = telnetlib.Telnet(HOST)
    print 'connect ptt.cc'
    time.sleep(2)
    content = tn.read_very_eager().decode('big5','ignore')    #進站畫面   


    while '上方為使用者心情點播留言區，不代表本站立場' not in content.encode('utf-8'):

        while '系統過載' in content.encode('utf-8'):
            print('系統過載請稍候...')
            tn = telnetlib.Telnet('ptt.cc')
            content = tn.read_very_eager().decode('big5','ignore')
            time.sleep(2)


        if u"以 new 註冊:" in content:
            print 'username'
            username = account.username()
            tn.write((username+"\r\n").encode('big5'))
            time.sleep(1)
            
            print 'password'
            password = account.password()
            tn.write((password+"\r\n").encode('big5'))
            time.sleep(6)
            content = tn.read_very_eager().decode('big5','ignore')

 
        if u"密碼不對" in content:
            print("密碼不對或無此帳號。程式結束")
            sys.exit()

        if u"您想刪除其他重複登入的連線嗎" in content:
            print("發現重複連線,刪除他...")
            tn.write("Y\r\n".encode('big5')) 
            time.sleep(20)
            content = tn.read_very_eager().decode('big5','ignore')

        if u"任意鍵" in content:
            print("資訊頁面，按任意鍵繼續...")
            tn.write("\r\n".encode('big5'))
            time.sleep(2)
            content = tn.read_very_eager().decode('big5','ignore')

        if u'編輯器自動復原' in content:
            print('編輯器自動復原：不復原')
            tn.write("q\n".encode('big5'))
            time.sleep(2)
            content = tn.read_very_eager().decode('big5','ignore')

        if u'要刪除以上錯誤嘗試的記錄嗎' in content:
            print '刪除以上錯誤嘗試的記錄'
            print re.findall('[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+',content)
            tn.write("y\n".encode('big5'))
            time.sleep(2)
            content = tn.read_very_eager().decode('big5','ignore')

    print '登入成功'
    return tn



def login_beauty( tn ):
    print '分組討論區'
    tn.write("\r\n".encode('big5') )
    time.sleep(2)
    
    print '生活娛樂館'
    tn.write("nnnnnnnnr".encode('big5') )
    time.sleep(2)
    
    print '聊天'
    tn.write("nnnnnnnnnnnnnnnnr".encode('big5') )
    time.sleep(2)
    
    print '進入beauty'
    tn.write("nr".encode('big5') )
    time.sleep(2)
    content = tn.read_very_eager().decode('big5','ignore')
    

    while "任意鍵" in content.encode('utf-8'):
        print '請按任意鍵繼續' 
        tn.write("\r\n".encode('big5'))
        time.sleep(2)
        content = tn.read_very_eager().decode('big5','ignore')
        print content.encode('utf-8')



def download(contentData):

    for url in contentData.searchUrl():
        url = url + '.jpg'
        tmp = re.findall('(?<=imgur.com/)[a-zA-Z0-9]+.jpg',url)
        fname = tmp[0]

        print url

        try:
            res = requests.get( url , stream = True , timeout = 10.0 )   
            f = open( fname, 'wb' )
            shutil.copyfileobj( res.raw , f )   # 寫入圖片
            f.close()
            del res      
        except:
            a , b , c = sys.exc_info()
            log = open(time.strftime('%Y%m%d_%H%M%S') + '.txt','w')     # 例外事件的 log
            log.write(time.strftime('%Y/%m/%d_%H:%M:%S') + '\n')
            log.write('例外類型 : ' + str(a) + '\n')
            log.write('例外訊息 : ' + str(b) + '\n')
            log.write('traceback物件 : ' + str(c) + '\n') 
            log.write('id : ' + str(contentData.id) + '\n')
            log.write('url : ' + str(url))
            log.close()
            continue

    

def main():

    start = time.time()

    tn = login()

    login_beauty( tn )

    tn.write((str(number_start)+"\r\n").encode('big5') )     # 設定初始頁數 跳至第幾項 
    time.sleep(2)
    tn.write("r".encode('big5') )  # 進入
    time.sleep(2)
    content = tn.read_very_eager().decode('big5','ignore')


    print 'download now !' 
  
    for i in range(number_start,number_start + search_range):

        print 'page : ' + str(i)

        if i == number_start:       # 第一次進入時不用翻頁
            pass
        else:
            tn.write("f".encode( 'big5' ))   #往後翻
            # tn.write("b".encode( 'big5' ))   #往前翻
            time.sleep(2)
            content = tn.read_very_eager().decode( 'big5' , 'ignore' )   #讀內文

         
        while '請按任意鍵繼續' in content.encode('utf-8'):         # 在遇到已刪除文章的情況下預設會跳回目錄，所以輸入 b 會回到進版畫面 
            tn.write( "\nkr".encode( 'big5' ) )                    # \nkr 可以跳到刪除文章的下一篇
            time.sleep(2)
            content = tn.read_very_eager().decode( 'big5' , 'ignore' )
        
        
        contentData = ContentData.ContentData(content,i)
        contentData.contentReplace()                            # 去掉奇怪字元
        

        for page in range(contentData.searchPage()):            # 翻幾次頁
            if page == 1:
                pass
            else:
                tn.write( "PgDn".encode('big5') )
                time.sleep(2)
                contentData.addContent( tn.read_very_eager().decode('big5','ignore') )

        download(contentData)

    print "log out......" 

    tn.write("qqqqqqqqqg\r\ny\r\n".encode('big5') )            #登出
    time.sleep(2)
    tn.write("\r\n".encode('big5') )

    end = time.time()
    print '運行時間 : ' + str(end-start)


if __name__ == '__main__' :  
    main()
