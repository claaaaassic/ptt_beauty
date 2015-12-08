#-*- coding: utf-8 -*-
import telnetlib
import sys
import time
import requests
import shutil
import account


def login():

    username = account.username()
    password = account.password()

    tn = telnetlib.Telnet('ptt.cc')
    time.sleep(1)
    print('連接成功!!!', '\n')
    content = tn.read_very_eager().decode('big5','ignore')    #進站畫面

    while '系統過載' in content:
        print('系統過載請稍候...')
        tn = telnetlib.Telnet('ptt.cc')
        time.sleep(1)
        content = tn.read_very_eager().decode('big5','ignore')
        
    if "以 new 註冊:" in content:
        print("輸入帳號...")
        tn.write((username+"\r\n").encode('big5') )
        time.sleep(0.5)
        
        print("輸入密碼...")
        tn.write((password+"\r\n").encode('big5'))
        time.sleep(1)
        content = tn.read_very_eager().decode('big5','ignore')
        # print('\n\n\n' , content , '\n\n\n')
        
        if "密碼不對" in content:
            print("密碼不對或無此帳號。程式結束")
            sys.exit()
        if "您想刪除其他重複登入的連線嗎" in content:
            print("發現重複連線,刪除他...")
            tn.write("y\n".encode('big5') ) 
            time.sleep(5)
            content = tn.read_very_eager().decode('big5','ignore')

        while "任意鍵" in content:
            print("資訊頁面，按任意鍵繼續...")
            tn.write("\r\n".encode('big5') )
            time.sleep(1)
            content = tn.read_very_eager().decode('big5','ignore')
            time.sleep(2)

        if '編輯器自動復原' in content:
   
            print('編輯器自動復原：不復原')
            tn.write("qqq\n".encode('big5'))
            time.sleep(1)
            content = tn.read_very_eager().decode('big5','ignore')

    else:
        print("沒有可輸入帳號的欄位，網站可能掛了")
    print('='*30 , "登入完成", '='*30)
    return tn


def login_beauty( tn ):
    print('\n分組討論區')
    tn.write("\r\n".encode('big5') )
    time.sleep(0.5)
    
    print('\n生活娛樂館')
    tn.write("nnnnnnnnr".encode('big5') )
    time.sleep(1)
    
    print('\n聊天')
    tn.write("nnnnnnnnnnnnnnnnr".encode('big5') )
    time.sleep(1)
    
    print('\n進入beauty')
    tn.write("nr".encode('big5') )
    content = tn.read_very_eager().decode('big5','ignore')
    

    while "任意鍵" in content:
        print('請按任意鍵繼續')
        tn.write("\r\n".encode('big5') )
        content = tn.read_very_eager().decode('big5','ignore')
        time.sleep(0.5)      


def getfname(url):

    fname = url[19:30]
    if '/' in fname:
        print( 'fname have / : %s' % fname)
        return 0
    elif '(' in fname:
        print( 'fname have ( : %s' % fname )
        return 0 
    elif '[' in fname:
        print( 'fname have [ : %s' % fname)
        return 0
    elif '\x1b' in fname:
        print( 'fname have \x1b : %s' % fname)
        return 0
    elif len(fname) > 12 :
        print( 'too long fname : %s' % fname )
        return 0
    elif len(fname) < 10 :
        print( 'too short fname : ' % fname )
        return 0
    else :
        return fname


def download( fname , url ):
   
    res = requests.get( url, stream = True , timeout = 10.0 )          
    f = open( fname, 'wb' )
    shutil.copyfileobj( res.raw, f )
    f.close()
    del res
    return 0 



if __name__ == '__main__' :

    tn = login()
    login_beauty( tn )

    number = 32927 #17600
    print (tn.read_very_eager().decode('big5','ignore'))
    tn.write((str(number)+"\r\n").encode('big5') )     #跳至第幾項

    tn.write("r".encode('big5') )
    content = tn.read_very_eager().decode('big5','ignore')
    print(content, '\n\n\n')


    print( '\n download now !\n' )   
    while number > 15000 :
        tn.write( "b".encode( 'big5' ) )
        time.sleep(0.5)
        content = tn.read_very_eager().decode( 'big5' , 'ignore' )   #讀內文
        print(number , '\n')
        number = number - 1
        if '帥哥美女板' in content:
            tn.write( "kr".encode( 'big5' ) )
            time.sleep(0.5)
            content = tn.read_very_eager().decode( 'big5' , 'ignore' )
            
        if '正妹' in content:
            pass
        else:
            continue

        page_end = content.find('頁 (')                   #取頁數
        page_str = content[page_end-2:page_end]

        page = 0
        if page_str.isnumeric():
            page = int( page_str )
        if page > 4:
            page = 4
        else:
            page = 2
        

        count = 0
        while page > 0 :                                                #search page 1
            count = content.count( 'http://i.imgur.com/' ) + content.count( 'http://imgur.com/' ) + count     #pic count
            index = 0
            while count > 0 :
                count = count -1
                
                if 'http://imgur.com/' in content:
                    index = content.find( 'http://imgur.com/' , index)
                    url = 'http://i.imgur.com/' + content[ index+17 : index+24 ] + '.jpg'
                elif 'http://i.imgur.com/' in content:
                    index = content.find( 'http://i.imgur.com/' , index)
                    url = content[ index : index+26 ] + '.jpg'
                else:
                    index = index + 24
                    continue
                index = index + 24
               
                fname = getfname( url )
                print(fname)
                
                if fname == 0:
                    continue
                else:
                    download( fname , url )
                 

            tn.write( "PgDn".encode('big5') )
            time.sleep(0.5)
            content = tn.read_very_eager().decode('big5','ignore')
            page = page - 1
          

    print( "\n\n\n登出......" )

    tn.write("qqqqqqqqqg\r\ny\r\n".encode('big5') )            #登出
    time.sleep(1)
    tn.write("\r\n".encode('big5') )
    
