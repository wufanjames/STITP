#"coding=utf-8"
import time
import list
import torndb
from tornado.httpclient import HTTPError
#con = MySQLdb.connect('localhost', 'root', 'testpassword', 'stitp')
#cur = con.cursor() #获取操作游标
db = torndb.Connection(host = 'localhost',database ='stitp',user = 'root',password = 'testpassword')

#获取当前系统时间
def GetNowTime():
    return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))

#Md5加密
def md5(str):
    import hashlib
    m = hashlib.md5()
    m.update(str)
    return m.hexdigest()

#注册功能数据库交互
def adduser(username,password, realname):
    password=md5(password)
    sql = "insert into userlist (name,password, real_name) values ('%s','%s','%s')" % (username, password, realname)
    sql2="select * from userlist where name='%s'"%(username)
    r=db.query(sql2)
    if(len(r)==0):
        db.execute(sql)
        flag=1
    else:
        flag=0
    return flag

#登陆功能数据库交互
def checkuser(username, password, identity):
    password=md5(password)
    sql = "select * from userlist where name='%s' and password='%s' and identity=%s" % (username, password, int(identity))
    result=db.query(sql)
    if(len(result) == 0):
        list.flag = 0
        return False
    else:
        list.flag = 1
        return True

#获取用户信息
def getuserinfo(name):
    sql="select * from userlist where name='%s'"%(name)
    re=db.query(sql)
    return re
#修改登陆密码
def changepassword(id, newpass):
    sql="update userlist set password=%s where id=%s"%(newpass,int(id))
    db.execute(sql)

#事务管理之设备主页
def getDevice():
    todos = db.query("select * from todo order by post_date desc")
    return todos

#事务管理之新建设备信息
def newEvent(title):
    time=GetNowTime()
    title=str(title.encode('UTF-8'))
    sql="insert into todo (title,post_date,finished) values ('%s','%s',0)"%(title, time)
    db.execute(sql)

#事务管理之修改设备信息
def editEvent1(id):
    todos = db.query("select * from todo where id=%s", int(id))
    return todos
def editEvent2(id):
    todos = db.query("select * from todo where id=%s", int(id))
    return todos
def editEvent3(id,title):
    time=GetNowTime()
    db.execute("update todo set title=%s, post_date=%s where id=%s",title, time,int(id))

#事务管理之删除设备信息
def Dsearch(id):
    todo = db.query("select * from todo where id=%s", int(id))
    return todo
def delete(id):
    db.execute("delete from todo where id=%s", int(id))

#事务管理之完成设备任务
def finish(finished,id):
    sql="update todo set finished=%s where id=%s"%(finished, int(id))
    db.execute(sql)

#事务管理之勤工俭学安排
def workers():
    workers=db.query("select * from worker")
    return workers

def changework(num, name, place, date):
    sql="update worker set num='%s', name='%s', place='%s' where date=%s"%(num, name,place,int(date))
    db.execute(sql)

#事务管理之建立日志
def saveRe(content):
    time=GetNowTime()
    sql="insert into dailyrecord (content,time) values ('%s','%s')"%(content,time)
    db.execute(sql)
#查看全部日志
def display():
    sql="select * from dailyrecord"
    contents=db.query(sql)
    return contents
#查询日志
def search(date):
    sql="select * from dailyrecord where time REGEXP '^%s'"%(date)
    results=db.query(sql)
    return results
#日记内容写入后台文件
def writedata():
    sql="select * from dailyrecord"
    results=db.query(sql)
    f = None
    if not results:
        return
    try:
        f = file('text.txt', 'w')
        for r in results:
            f.write(str(r.time.encode('UTF-8')))
            f.write('\n')
            f.write(str(r.content.encode('UTF-8')))
            f.write('\n')
            f.write('========================================>\n')
    except:
        raise
    finally:
        if f:
            f.close()


#项目信息管理
#查询项目
def Psearch(name):
    sql="select * from project where projectname='%s'"%(name)
    results=db.query(sql)
    return results
#查看全部
def seeallpro():
    sql="select * from project"
    results=db.query(sql)
    return results
def count():
    sql="select count(*) from project"
    num=db.query(sql)
    return num
#新建项目
def newpro(name, num, attribute, subject):
    sql="insert into project (projectname, projectnum, attribute, subject) values ('%s','%s','%s','%s')"%(name, num,attribute, subject)
    db.execute(sql)
#删除项目
def Deletepro(id):
    db.execute("delete from project where id=%s", int(id))


#教学管理
#全部成绩
def allscore():

    sql="select * from score"
    result=db.query(sql)
    return result
#查询成绩
#按学号
def searchscorebynum(num):
    sql="select * from score where stunum = '%s'"%num
    result=db.query(sql)
    return result
#按学年
def searchscorebyyear(year1, year2):
    key=year1+'-'+year2
    sql="select * from score where year= '%s'"%key
    result=db.query(sql)
    return result
#按学期
def searchscorebyterm(year1, year2, term):
    key=year1+'-'+year2
    sql="select * from score where year= '%s' and term=%s"%(key,int(term))
    result=db.query(sql)
    return result
#学生查询个人成绩
def stuscore(name):
    sql="select * from score where stuname='%s'"%(name)
    result=db.query(sql)
    return result
#教师端新建签到
def newsign(name):
    sql="CREATE TABLE %s (signid INT NOT NULL AUTO_INCREMENT, stunum VARCHAR(20) NULL, stuname  VARCHAR(10) NULL,PRIMARY KEY (signid))"%(name)
    db.execute(sql)
#学生端进行签到
def stusign(name,stunum,stuname):
    sql="insert into %s (stunum, stuname) values ('%s','%s')"%(name,stunum,stuname)
    db.execute(sql)
#签到计数
def signcount(name):
    sql="select count(*) from %s"%name
    num=db.query(sql)
    return num
#获取所有已经签到者的信息
def getallsign(name):
    sql="select * from %s"%name
    re=db.query(sql)
    return re
#检查是否重复签到
def checkthesame(dbname,username):
    sql="select * from %s where stunum='%s'"%(dbname, username)
    r=db.query(sql)
    if(len(r)==0):
        return False
    else:
        return True
#将签到记录保存
def signhistory(name):
    time=GetNowTime()
    sql="insert into signhistory (name,time) values ('%s','%s')"%(name,time)
    db.execute(sql)
#获取历史签到
def getsignlist():
    sql="select * from signhistory"
    re=db.query(sql)
    return re
#获取指定签到历史
def gethistory(id):
    sql="select name from signhistory where id=%s"%(int(id))
    re=db.query(sql)
    return re
#身份校验
def checkid(userinfo):
    if(userinfo[0].identity==2):
       raise HTTPError(403)

