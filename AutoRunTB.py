import win32gui
from win32.lib import win32con
import time
import win32process
import datetime
from commctrl import LVM_GETITEMTEXT, LVM_GETITEMCOUNT
import os
import queue
import requests
import json
import platform
import win32api
import global_TB
import sendemail

def wx_msg(corp_id, secret,agentid,msg):
    values = {'corpid' :corp_id,
              'corpsecret':secret
              }
    req = requests.post('https://qyapi.weixin.qq.com/cgi-bin/gettoken',params=values)
    token = json.loads(req.text)["access_token"]
    #try:
    dict_arr = {"touser": "@all",
                "toparty": "@all",
                "msgtype": "text",
                "agentid": agentid,
                "text": {"content": msg},
                "safe": "0"}
    data = json.dumps(dict_arr,ensure_ascii=False,indent=2,sort_keys=True).encode('utf-8')
    reqs = requests.post("https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token="+token,data)
    
def Log(text):
    if global_TB.username == 'sqltxt' or global_TB.username == 'gentle':
        f = open(global_TB.mylog,'a')
        f.write(str(global_TB.status)+'\t'+datetime.datetime.now().strftime('[%H:%M:%S]')+'\t'+text+'\n')
        f.close()
        wx_msg(global_TB.corp_id,global_TB.secret,global_TB.agentid,str(global_TB.status)+'\t'+datetime.datetime.now().strftime('[%H:%M:%S]')+'\t'+text)
    
def handle_window(hwnd,extra):#global_TB.TB_handle句柄
    if win32gui.IsWindowVisible(hwnd):
        if extra in win32gui.GetWindowText(hwnd):
            global_TB.TB_handle= hwnd

def GetTV_Host():
    TV = win32gui.FindWindow('#32770','TeamViewer')
    #print(hex(TV))
    ID = win32gui.FindWindowEx(TV,0,'Edit',None)
    #print(hex(ID))
    PW = win32gui.FindWindowEx(TV,ID,'Edit',None)
    #print(hex(PW))
    
    ID_buf_size = win32gui.SendMessage(ID, win32con.WM_GETTEXTLENGTH, 0, 0) + 1  # 要加上截尾的字节  
    #print(buf_size)
    ID_str_buffer = win32gui.PyMakeBuffer(win32gui.SendMessage(ID, win32con.WM_GETTEXTLENGTH, 0, 0) + 1)  # 生成buffer对象
    #print(str_buffer)
    win32api.SendMessage(ID, win32con.WM_GETTEXT, ID_buf_size, ID_str_buffer)  # 获取buffer  
    ID_address, ID_length = win32gui.PyGetBufferAddressAndLen(ID_str_buffer) 
    IDstr = win32gui.PyGetString(ID_address, ID_length) 
    
    PW_buf_size = win32gui.SendMessage(PW, win32con.WM_GETTEXTLENGTH, 0, 0) + 1  # 要加上截尾的字节  
    #print(buf_size)
    PW_str_buffer = win32gui.PyMakeBuffer(win32gui.SendMessage(PW, win32con.WM_GETTEXTLENGTH, 0, 0) + 1)  # 生成buffer对象
    #print(str_buffer)
    win32api.SendMessage(PW, win32con.WM_GETTEXT, PW_buf_size, PW_str_buffer)  # 获取buffer  
    PW_address, PW_length = win32gui.PyGetBufferAddressAndLen(PW_str_buffer) 
    PWstr = win32gui.PyGetString(PW_address, PW_length) 
    
    return IDstr[:-1]+'\n'+PWstr[:-1]

# 编号0
def Kill():
    global_TB.times = 0 #登录次数清零
    try:
        global_TB.status = 0
        if 85700<=int(time.strftime("%I%M%S")) <= 85703:
            if "TradeBlazer.exe" in os.popen('tasklist /FI "IMAGENAME eq TradeBlazer.exe"').read():
                os.system('TASKKILL /F /IM TradeBlazer.exe')
                os.system('TASKKILL /F /IM TBDataCenter.exe')                
                Log('进程清零')
                global_TB.TB_handle= 0
                global_TB.Accounts = 0
                global_TB.Monitor_handle = 0
                time.sleep(5)                
    except Exception as e:
        Log(str(e))

# 编号1、2
def TBStar_TBLogin(un,pw):
    try:
        global_TB.status = 1 
        if "TradeBlazer.exe" not in os.popen('tasklist /FI "IMAGENAME eq TradeBlazer.exe"').read():
            #打开TB
            handle = win32process.CreateProcess(global_TB.path+'TradeBlazer.exe','',None,None,0,win32process.CREATE_NO_WINDOW,None,global_TB.path,win32process.STARTUPINFO())#打开TB,获得其句柄
            time.sleep(21)
            Log('打开TB')
            #数据重置
            win32gui.PostMessage(win32gui.FindWindowEx(win32gui.FindWindow('#32770',None),0,'Button','数据重置'),win32con.BM_CLICK,1,0)
            time.sleep(1)
            win32gui.PostMessage(win32gui.FindWindowEx(win32gui.FindWindow('#32770','数据重置'),0,'Button','重置(&R)'),win32con.BM_CLICK,1,0)
            time.sleep(1)
            win32gui.PostMessage(win32gui.FindWindowEx(win32gui.FindWindow('#32770','确认'),0,'Button','是(&Y)'),win32con.BM_CLICK,1,0)
            time.sleep(1)
            win32gui.PostMessage(win32gui.FindWindowEx(win32gui.FindWindow('#32770','提示'),0,'Button','确定'),win32con.BM_CLICK,1,0)
            time.sleep(1)
            #登录框
            win32gui.SendMessage(win32gui.FindWindowEx(win32gui.FindWindowEx(win32gui.FindWindow('#32770',None),0,'ComboBox',None),0,'Edit',None),win32con.WM_SETTEXT,0,un)
            time.sleep(1)
            win32gui.SendMessage(win32gui.FindWindowEx(win32gui.FindWindow('#32770',None),0,'Edit',None),win32con.WM_SETTEXT,0,pw)
            time.sleep(1)
            win32gui.SendMessage(win32gui.FindWindowEx(win32gui.FindWindow('#32770',None),0,'Button','登录(&L)'),win32con.BM_CLICK,1,0)
            ##global global_TB.status
            global_TB.status = 2
            Log(str('登录柜台'))
            time.sleep(28)
        #取得TB句柄
            win32gui.EnumWindows(handle_window,'交易开拓者')
        #time.sleep(2)
        #取得帐户列表数目
            global_TB.Accounts = win32gui.SendMessage(win32gui.FindWindowEx(win32gui.FindWindowEx(win32gui.FindWindowEx(global_TB.TB_handle,win32gui.FindWindowEx(global_TB.TB_handle,0,'AfxControlBar110',None),'AfxControlBar110',None),0,None,'帐户管理'),0,'SysListView32',None),LVM_GETITEMCOUNT)
            global_TB.Trade = 0
    except Exception as e:
        Log(str(e))

# 编号11、10 
def AccountLogin_LoginFail():
    try:
        global_TB.status = 10
        if global_TB.TB_handle!=0:
            times=1
            while win32gui.SendMessage(win32gui.FindWindowEx(win32gui.FindWindowEx(win32gui.FindWindowEx(global_TB.TB_handle,win32gui.FindWindowEx(global_TB.TB_handle,0,'AfxControlBar110',None),'AfxControlBar110',None),0,None,'帐户管理'),0,'SysListView32',None),LVM_GETITEMCOUNT)<1:
                if global_TB.Accounts == 0:
                    Log('柜台关闭')
                    global_TB.status = 11
                    win32gui.PostMessage(global_TB.TB_handle,win32con.WM_COMMAND, win32gui.GetMenuItemID(win32gui.GetSubMenu(win32gui.GetMenu(global_TB.TB_handle),7),17),0)#帐户登录
                    win32gui.SendMessage(win32gui.FindWindowEx(win32gui.FindWindow('#32770','帐户登录'),0,'Button','登录(&L)'),win32con.WM_ACTIVATE,win32con.WA_ACTIVE,0)#激活窗口
                    time.sleep(4)
                    win32gui.SendMessage(win32gui.FindWindowEx(win32gui.FindWindow('#32770','帐户登录'),0,'Button','登录(&L)'),win32con.BM_CLICK,1,0)
                    times = times + 1
                    Log(str(times)+' 次登录')
                    time.sleep(15)
                    global_TB.Accounts = win32gui.SendMessage(win32gui.FindWindowEx(win32gui.FindWindowEx(win32gui.FindWindowEx(global_TB.TB_handle,win32gui.FindWindowEx(global_TB.TB_handle,0,'AfxControlBar110',None),'AfxControlBar110',None),0,None,'帐户管理'),0,'SysListView32',None),LVM_GETITEMCOUNT)
                    global_TB.Trade = 0
                elif times >150:
                    break;
    except Exception as e:
        Log(str(e))

# 编号3     
def TradeStar():
    if global_TB.TB_handle!=0 and global_TB.Accounts>0 and global_TB.Monitor_handle == 0 and global_TB.Trade == 0:
        try:
            global_TB.status = 3
            win32gui.PostMessage(global_TB.TB_handle,win32con.WM_COMMAND, win32gui.GetMenuItemID(win32gui.GetSubMenu(win32gui.GetMenu(global_TB.TB_handle),0),22),0)#启动所有自动交易            
            Log('启动交易')            
            global_TB.Trade = 1
            time.sleep(1)
        except Exception as e:
            Log(str(e))

# 编号4
def MonitorStar():
    if win32gui.FindWindow('#32770','自动交易头寸监控器') == 0:
        try:
            global_TB.status = 4
            if global_TB.TB_handle!=0 and global_TB.Accounts>0 and global_TB.Monitor_handle == 0 and global_TB.Trade == 1: 
                win32gui.PostMessage(global_TB.TB_handle,win32con.WM_COMMAND, win32gui.GetMenuItemID(win32gui.GetSubMenu(win32gui.GetMenu(global_TB.TB_handle),7),11),0)#监控器
                #print (st)            
                Log('打开监控')
                time.sleep(10)
            #取得监控器句柄
            global_TB.Monitor_handle = win32gui.FindWindow('#32770','自动交易头寸监控器')
        except Exception as e:
            Log(str(e))

# 编号5   
def SaveWorkSpace():
    try:
        global_TB.status = 5
        if global_TB.TB_handle!=0:            
            win32gui.PostMessage(global_TB.TB_handle,win32con.WM_COMMAND, win32gui.GetMenuItemID(win32gui.GetSubMenu(win32gui.GetMenu(global_TB.TB_handle),0),9),0)#保存所有工作区
            Log('保存工作区')
        time.sleep(2)
    except Exception as e:
        Log(str(e))

# 编号6
def MonitorClose():
    try:
        global_TB.status = 6
        if global_TB.Monitor_handle!=0:            
            win32gui.PostMessage(win32gui.FindWindow('#32770','自动交易头寸监控器'),win32con.WM_CLOSE,0,0)
            time.sleep(1)
            win32gui.SendMessage(win32gui.FindWindowEx(win32gui.FindWindow('#32770','确认 '),0,'Button','是(&Y)'),win32con.WM_ACTIVATE,win32con.WA_ACTIVE,0)#激活窗口
            time.sleep(2)
            win32gui.SendMessage(win32gui.FindWindowEx(win32gui.FindWindow('#32770','确认 '),0,'Button','是(&Y)'),win32con.BM_CLICK,0,0)
            #
            global_TB.Monitor_handle = 0
            Log('关闭监控')
            time.sleep(2)
    except Exception as e:
        Log(str(e))

# 编号7
def TradeStop():
    try:
        global_TB.status = 7
        if global_TB.TB_handle!=0:            
            win32gui.PostMessage(global_TB.TB_handle,win32con.WM_COMMAND, win32gui.GetMenuItemID(win32gui.GetSubMenu(win32gui.GetMenu(global_TB.TB_handle),0),23),0)#停止所有自动交易
            #global global_TB.Trade
            global_TB.Trade = 0
            Log('停止交易')
            time.sleep(2)
    except Exception as e:
        Log(str(e))

# 编号8
def TBClose():
    try:
        global_TB.status = 8
        if global_TB.TB_handle!=0:
            #win32gui.PostMessage(global_TB.TB_handle,win32con.WM_COMMAND, win32gui.GetMenuItemID(win32gui.GetSubMenu(win32gui.GetMenu(global_TB.TB_handle),0),27),0)#退出程序(菜单方式）
            win32gui.PostMessage(global_TB.TB_handle,win32con.WM_CLOSE,0,0)
            time.sleep(2)
            win32gui.SendMessage(win32gui.FindWindowEx(win32gui.FindWindow('#32770','确认'),0,'Button','是(&Y)'),win32con.WM_ACTIVATE,win32con.WA_ACTIVE,0)#激活窗口
            time.sleep(2)
            win32gui.SendMessage(win32gui.FindWindowEx(win32gui.FindWindow('#32770','确认'),0,'Button','是(&Y)'),win32con.BM_CLICK,1,0)            
            Log('关闭TB')
            global_TB.times = 0#登录次数清零
            global_TB.status = 0#状态清零
            #
            global_TB.TB_handle= 0
            global_TB.Accounts = 0
            global_TB.Rubber_times = 1
            wx_msg(global_TB.corp_id,global_TB.secret,global_TB.agentid,global_TB.username+'\n'+GetTV_Host())
    except Exception as e:
        Log(str(e))
    global_TB.Expired_times = 0
    global_TB.Rubber_times = 1

# 编号9
def Expired():
    try:
        global_TB.status = 9
        if global_TB.Expired_times == 0:            
            if datetime.datetime.now()>datetime.datetime.strptime(global_TB.ExpirationDate,"%Y-%m-%d"):
                win32gui.MessageBox(0, '程序已经过期,请联系13299962008', '过期提示', win32con.MB_OK) 
                print(datetime.datetime.now())
                print("过期日"+global_TB.ExpirationDate)
                try:
                    sys.exit()
                except:
                    Log("过期日"+global_TB.ExpirationDate)
            elif datetime.datetime.now()<=datetime.datetime.strptime(global_TB.ExpirationDate,"%Y-%m-%d") and datetime.datetime.strptime(global_TB.ExpirationDate,"%Y-%m-%d")-datetime.datetime.now()<datetime.timedelta(12):
                win32gui.MessageBox(0, '程序即将过期,请联系13299962008', '警告', win32con.MB_OK) 
                Log("即将过期,过期日:"+global_TB.ExpirationDate)
    except Exception as e:
        Log(str(e))
    global_TB.Expired_times = 1


# 编号20
def ShutdownR():
    ver = platform.platform()
    try:
        global_TB.status = 20
        if 'Windows-7' in ver:
            os.system('shutdown -r')
            Log('周末重启系统')
            time.sleep(60)
            wx_msg(global_TB.corp_id,global_TB.secret,global_TB.agentid,global_TB.username+'\n'+GetTV_Host())
        else:
            Log('非WIN7系统周末不重启')
            wx_msg(global_TB.corp_id,global_TB.secret,global_TB.agentid,global_TB.username+'\n'+GetTV_Host())
    except Exception as e:
        Log(str(e))

# 编号40
def Rubber():
    global_TB.status = 40
    try:
        if global_TB.username != 'sqltxt' or global_TB.username != 'gentle':
            if global_TB.Rubber_times ==1:
                for fname in os.listdir(global_TB.path):#for循环 清除目录下所有LOG_文件
                    if 'LOG_' in fname:
                        Log('清扫:'+fname)
                        os.remove(global_TB.path+fname)
                        global_TB.Rubber_times = 0
                        #写入空文件
                        #f = open(global_TB.mylog,'a')
                        #f.write('\n')
                        #f.close()
    except Exception as e:
        Log(str(e))
#导出公式并邮寄
def Expot_fbk():
    while win32gui.FindWindow('#32770','导入/导出公式')==0:
        win32gui.EnumWindows(handle_window,'交易开拓者')
        if win32gui.FindWindow('#32770','自动交易头寸监控器') != 0:
            time.sleep(2)
            win32gui.ShowWindow(win32gui.FindWindow('#32770','自动交易头寸监控器'),win32con.SW_MINIMIZE)
            time.sleep(1)
            
        win32gui.BringWindowToTop(global_TB.TB_handle)
        win32gui.ShowWindow(win32gui.FindWindowEx(win32gui.FindWindowEx(win32gui.FindWindowEx(global_TB.TB_handle,None,'AfxControlBar110','PanelFrame'),None,0,'PanelFrame'),None,'AfxWnd110',None),win32con.SW_MAXIMIZE)

        win32gui.PostMessage(global_TB.TB_handle,win32con.WM_COMMAND, win32gui.GetMenuItemID(win32gui.GetSubMenu(win32gui.GetMenu(global_TB.TB_handle),1),1),0)#面板 F3
        time.sleep(3)
        pos=win32gui.GetWindowRect(win32gui.FindWindowEx(win32gui.FindWindowEx(win32gui.FindWindowEx(global_TB.TB_handle,None,'AfxControlBar110','PanelFrame'),None,0,'PanelFrame'),None,'AfxWnd110',None))
        win32api.SetCursorPos([int((pos[0]+pos[2])/2),pos[3]-35])
        time.sleep(1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0,0,0)
        time.sleep(1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0,0,0)
        time.sleep(1)

        win32api.SetCursorPos([int((pos[0]+pos[2])/2),pos[1]+255])
        time.sleep(1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0,0,0)
        time.sleep(1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0,0,0)
        time.sleep(3)
        
    win32gui.PostMessage(win32gui.FindWindowEx(win32gui.FindWindow('#32770','导入/导出公式'),None,'Button','下一步(&N) >'),win32con.BM_CLICK,1,0)
    time.sleep(1)
    win32gui.PostMessage(win32gui.FindWindowEx(win32gui.FindWindowEx(win32gui.FindWindow('#32770','导出公式'),None,'#32770','导出公式'),None,'Button','>>'),win32con.BM_CLICK,1,0)
    time.sleep(1)
    win32gui.PostMessage(win32gui.FindWindowEx(win32gui.FindWindow('#32770','导出公式'),None,'Button','下一步(&N) >'),win32con.BM_CLICK,1,0)
    time.sleep(1)
    win32gui.PostMessage(win32gui.FindWindowEx(win32gui.FindWindowEx(win32gui.FindWindow('#32770','导出公式'),None,'#32770','导出公式'),None,'Button','浏览(&O)...'),win32con.BM_CLICK,1,0)
    time.sleep(1)
    win32gui.SendMessage(win32gui.FindWindowEx(win32gui.FindWindowEx(win32gui.FindWindowEx(win32gui.FindWindowEx(win32gui.FindWindowEx(win32gui.FindWindow('#32770','保存公式备份文件'),None,'DUIViewWndClassName',None),None,'DirectUIHWND',None),None,'FloatNotifySink',None),None,'ComboBox',None),None,'Edit',None),win32con.WM_SETTEXT,0,str(int(time.strftime("%Y%m%d"))))#%H%M%S
    time.sleep(1)
    win32gui.PostMessage(win32gui.FindWindowEx(win32gui.FindWindow('#32770','保存公式备份文件'),None,'Button','保存(&S)'),win32con.BM_CLICK,1,0)
    time.sleep(1)
    win32gui.PostMessage(win32gui.FindWindowEx(win32gui.FindWindow('#32770','导出公式'),None,'Button','完成'),win32con.BM_CLICK,1,0)
    time.sleep(1)
    win32gui.PostMessage( win32gui.FindWindowEx(win32gui.FindWindow('#32770','提示'),None,'Button','确定'),win32con.BM_CLICK,1,0)
    time.sleep(1)

if __name__=='__main__':
    f = open(global_TB.mylog,'a')
    f.write('\n')
    f.write('\t'+datetime.datetime.now().strftime('[%H:%M:%S]')+'\tAutoRunTB启动'+'\n')
    f.close()
    wx_msg(global_TB.corp_id,global_TB.secret,global_TB.agentid,datetime.datetime.now().strftime('[%H:%M:%S]')+'\tAutoRunTB启动')
    global_TB.status = 0
    global_TB.times = 0
    win32gui.EnumWindows(handle_window,'交易开拓者')
    while 1:
        if datetime.datetime.now().weekday()<6:
            if not (23500<int(time.strftime("%H%M%S"))< 85000 or 171400<int(time.strftime("%H%M%S"))< 204500):
                global_TB.TB_handle=0
                win32gui.EnumWindows(handle_window,'交易开拓者')                
                global_TB.Monitor_handle = win32gui.FindWindow('#32770','自动交易头寸监控器')
                #杀进程
                Kill()
                #TB未打开
                if global_TB.TB_handle==0:
                    TBStar_TBLogin(global_TB.username,global_TB.password)
                else:
                    print (global_TB.TB_handle)
                    global_TB.Accounts = win32gui.SendMessage(win32gui.FindWindowEx(win32gui.FindWindowEx(win32gui.FindWindowEx(global_TB.TB_handle,win32gui.FindWindowEx(global_TB.TB_handle,0,'AfxControlBar110',None),'AfxControlBar110',None),0,None,'帐户管理'),0,'SysListView32',None),LVM_GETITEMCOUNT)
                    #帐户未登录,监控器打开
                    if global_TB.Accounts ==0 and global_TB.Monitor_handle!=0:
                        MonitorClose()
                    #帐户未登录,监控器关闭
                    elif global_TB.Accounts == 0 and global_TB.Monitor_handle==0:
                        AccountLogin_LoginFail()
                        TradeStar()
                        MonitorStar()
                    #帐户已登录,监控器关闭
                    elif global_TB.Accounts!=0 and global_TB.Monitor_handle==0:
                        TradeStar()
                        MonitorStar()
                    #帐户以及登录,监控器打开
                    else:
                        TradeStar()                
            else:
                SaveWorkSpace()
                MonitorClose()
                TradeStop()
                TBClose()
                Rubber()
                print('闭盘状态'+datetime.datetime.now().strftime('[%H:%M:%S]'))
                print("global_TB.TB_handle:"+str(global_TB.TB_handle))
                print("global_TB.Accounts:"+str(global_TB.Accounts))
                print("global_TB.Monitor_handle:"+str(global_TB.Monitor_handle))
            
        else:
            if int(time.strftime("%H%M%S")) == 235959:
                Export_fbk()#导出公式
                sendemail.send()
                os.remove('C:/Users/Administrator/Documents/tbv5321_x64_portable/'+str(int(time.strftime("%Y%m%d")))+'.fbk')
                print('周日快乐'+datetime.datetime.now().strftime('[%H:%M:%S]'))
                ShutdownR()
        #TV测试
        #if 211500<int(time.strftime("%H%M%S"))< 211800:
            #wx_msg(global_TB.corp_id,global_TB.secret,global_TB.agentid,global_TB.username+'\n'+GetTV_Host())
        #导出测试
        if 194000<int(time.strftime("%H%M%S"))< 194010:
            Export_fbk()
        time.sleep(15)
