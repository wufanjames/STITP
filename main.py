#"coding=utf-8"
from list import *
import tornado.httpserver
import tornado.web
import tornado.ioloop
import tornado.options
import os.path
from tornado.options import define, options
from conDB import *
define("port", default=9000, type=int)

#基类
class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")

#登陆功能
class LoginHandler(tornado.web.RequestHandler):
    def get(self):
        if(list.flag == 0):
            m = '用户名或密码错误！'
        else:
            m = ''
        self.render('Login.html', m=m)
    def post(self):
        name = self.get_argument('username')
        pas = self.get_argument('password')
        identity=self.get_argument('identity')
        if(checkuser(name,pas,identity)):
            self.set_secure_cookie('user', name, expires_days=None)
        if(identity=='1'):
            self.redirect('/')
        else:
            self.redirect('/stu')


#教师版主页
class IndexHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
       realname=getuserinfo(self.current_user)
       checkid(realname)
       self.render('index.html', user=realname)
#学生版主页
class StuindexHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
       realname=getuserinfo(self.current_user)
       self.render('stuindex.html', user=realname)

#退出登陆
class LogoutHandler(tornado.web.RequestHandler):
    def get(self):
        self.clear_cookie('user')
        self.redirect('/')

#事务管理主页面
class Thingsman(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        checkid(getuserinfo(self.current_user))
        self.render('thm.html', user=getuserinfo(self.current_user))
class Device(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        checkid(getuserinfo(self.current_user))
        self.render('deviceindex.html')

#教学管理主页面
class Techman(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        checkid(getuserinfo(self.current_user))
        self.render('tem.html', user=getuserinfo(self.current_user))

#项目管理主页面
class Projman(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        checkid(getuserinfo(self.current_user))
        num=count()
        self.render('prm.html',number=num, user=getuserinfo(self.current_user))
#学生版，项目主页
class StuprmHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        num=count()
        self.render('stuprm.html',number=num, user=getuserinfo(self.current_user))

#注册功能
class RegistHandler(BaseHandler):
    def get(self):
        checkid(getuserinfo(self.current_user))
        self.render('regist.html',m='')
    def post(self):
        name = self.get_argument('username')
        pas = self.get_argument('password')
        realname=self.get_argument('realname')
        f=adduser(name, pas, realname)
        if f==1:
            self.render('registsuccess.html')
        else:
            self.render('regist.html',m='用户名被占用！')

#用户个人中心
class PersonalHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        userinformation=getuserinfo(self.get_current_user())
        if(userinformation[0].identity==1):
            identity="教师"
        else:
            identity="学生"
        self.render('personal.html', user=self.get_current_user(), userinfo=userinformation,m='',ID=identity)
#修改登陆密码
class ChangepassHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, id):
        self.render('changepass.html',user=getuserinfo(self.get_current_user()))
    def post(self, id):
        newpass=self.get_argument('pass')
        changepassword(id, newpass)
        self.render('personal.html',user=self.get_current_user(), userinfo=getuserinfo(self.get_current_user()),m='密码修改成功！')

#事务管理之设备主页
class D_IndexHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        checkid(getuserinfo(self.current_user))
        title = "todo"
        todos = getDevice()
        self.render("deviceindex.html", todos=todos, title=title)

#事务管理之新建设备信息
class D_NewHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        checkid(getuserinfo(self.current_user))
        title = self.get_argument("title")
        if not title:
            return None
        newEvent(title)
        self.redirect("/thm/device")

#事务管理之修改设备信息
class D_EditHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, id):
        checkid(getuserinfo(self.current_user))
        todos = editEvent1(id)
        todo = todos[0]
        if not todo:
            return None
        return self.render("deviceedit.html", todo=todo)
    def post(self, id):
        checkid(getuserinfo(self.current_user))
        todos = editEvent2(id)
        todo = todos[0]
        if not todo:
            return None
        title = self.get_argument("title")
        editEvent3(id, title)
        self.redirect("/thm/device")


#事务管理之删除设备信息
class D_DeleteHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, id):
        checkid(getuserinfo(self.current_user))
        todo = Dsearch(id)
        if not todo:
            return None
        delete(id)
        self.redirect("/thm/device")

#事务管理之完成设备任务
class D_FinishHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, id):
        checkid(getuserinfo(self.current_user))
        todo = Dsearch(id)
        if not todo:
            return None
        status = self.get_argument("status", "yes")
        if status == "yes":
            finished = 1
        elif status == "no":
            finished = 0
        else:
            return None
        finish(finished, id)
        self.redirect("/thm/device")

#事务管理之勤工俭学安排
class ThmworkerHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        checkid(getuserinfo(self.current_user))
        worker=workers()
        self.render('worker.html', work=worker)

#事务管理之勤工助学安排调整
class WorkerEdit(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        checkid(getuserinfo(self.current_user))
        self.render('workeredit.html')
    def post(self):
        date=self.get_argument('date')
        num=self.get_argument('num')
        name=self.get_argument('name')
        place=self.get_argument('place')
        changework(num, name , place, date)
        self.redirect('/thm/worker')

#事务管理之新建日志
class NewrecordHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        checkid(getuserinfo(self.current_user))
        self.render('newRe.html')
    def post(self):
        content=self.get_argument('content')
        saveRe(content)
        self.redirect('/thm/record/all')

#事务管理之查看全部日志
class Displayre(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        checkid(getuserinfo(self.current_user))
        contents=display()
        self.render('Allre.html', cont=contents)

#事务管理之查询日志
class Searchdiary(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        checkid(getuserinfo(self.current_user))
        self.render('searchre.html')
    def post(self):
        year=self.get_argument('year')
        month=self.get_argument('month')
        day=self.get_argument('day')
        if(len(month)==1):
            month="0"+month
        if(len(day)==1):
            day="0"+day
        date=year+'-'+month+'-'+day
        results=search(date)
        self.render('reresult.html', re=results)
#事务管理之导出日志内容
class OutrecordHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, input):
        checkid(getuserinfo(self.current_user))
        writedata()
        self.render('downloadre.html')
    def post(self, filename):
        filename=str(filename)
        self.set_header ('Content-Type', 'application/octet-stream')
        self.set_header ('Content-Disposition', 'attachment; filename='+filename)
        buf_size = 4096
        with open(filename, 'rb') as f:
            while True:
                data = f.read(buf_size)
                if not data:
                    break
                self.write(data)
        self.finish()

#项目信息管理之查询项目
class ProsearchHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('prosearch.html')
    def post(self):
        name=self.get_argument("name")
        re=Psearch(name)
        info=getuserinfo(self.current_user)
        if(info[0].identity==1):
            url='prm'
        else:
            url='stu'
        self.render('proresult.html',re=re, url=url, userinfo=info)

#项目信息管理之查看全部
class SeeallproHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        re=seeallpro()
        info=getuserinfo(self.current_user)
        if(info[0].identity==1):
            url='prm'
        else:
            url='stu'
        self.render('allpro.html',re=re, url=url, userinfo=info)

#项目信息管理之新建项目
class NewproHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        checkid(getuserinfo(self.current_user))
        self.render("newpro.html")
    def post(self):
        name=self.get_argument("name")
        num=self.get_argument("num")
        attr=self.get_argument("attribute")
        sub=self.get_argument("subject")
        newpro(name,num,attr,sub)
        self.redirect('/prm/all')

#项目信息管理之删除项目
class DeleteproHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, id):
        checkid(getuserinfo(self.current_user))
        Deletepro(id)
        self.redirect('/prm/all')

#教学管理之查看全部成绩
class AllscoreHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        checkid(getuserinfo(self.current_user))
        result=allscore()
        self.render('allscore.html',re=result)
#教学管理之查询成绩
class SearchscoreHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, way):
        checkid(getuserinfo(self.current_user))
        if(way=='1'):
            self.render('searchscorebynum.html')
        if(way=='2'):
            self.render('searchscorebyyear.html')
        if(way=='3'):
            self.render('searchscorebyterm.html')
    def post(self, way):
        if(way=='1'):
            stunum=self.get_argument('stunum')
            re=searchscorebynum(stunum)
        if(way=='2'):
            year1=self.get_argument('year1')
            year2=self.get_argument('year2')
            re=searchscorebyyear(year1, year2)
        if(way=='3'):
            year1=self.get_argument('year1')
            year2=self.get_argument('year2')
            term=self.get_argument('term')
            re=searchscorebyterm(year1, year2, term)
        self.render('scoreresult.html', re=re)
#学生查询个人成绩
class StuscoreHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        name=getuserinfo(self.current_user)[0].real_name
        result=stuscore(name)
        self.render('stuscore.html',re=result)
#教师端新建签到
class NewsignHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        checkid(getuserinfo(self.current_user))
        self.render('newsign.html')
    def post(self):
        sign=self.get_argument('signname')
        newsign(sign)
        sign=str(sign.encode('UTF-8'))
        signhistory(sign)
        signobj.setname(sign)
        self.redirect('/tem/sign/condition/0')
#教师端当前签到情况
class NowsignHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, id):
        checkid(getuserinfo(self.current_user))
        if(id=='0'):
            name=signobj.getname()
            num=signcount(name)
            re=getallsign(name)
        else:
            name=gethistory(id)[0]['name']
            num=signcount(name)
            re=getallsign(name)
        self.render('signcondition.html',number=num, name=name, re=re, id=id)

#学生端进行签到
class StusignHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('stusign.html',m='')
    def post(self):
        message='签到成功！！'
        signname=self.get_argument('signname')
        stunum=getuserinfo(self.current_user)[0]['name']
        stuname=getuserinfo(self.current_user)[0]['real_name']
        if(checkthesame(signobj.getname(), stunum)==False):
            stusign(signname,stunum, stuname)
        else:
            message='您已经签到成功，不需要再次签到！'
        self.render('stusign.html', m=message)
#历史签到（所有签到）
class SignhistoryHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        checkid(getuserinfo(self.current_user))
        re=getsignlist()
        self.render('signlist.html', re=re)

#学生端上传文件(提交报告)
class UploadFileHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('upload.html',m='')
    def post(self):
        #文件的暂存路径
        upload_path=os.path.join(os.path.dirname(__file__),'files')
        #提取表单中‘name’为‘file’的文件元数据
        file_metas=self.request.files['file']
        for meta in file_metas:
            filename=meta['filename']
            filepath=os.path.join(upload_path,filename)
            #有些文件需要以二进制的形式存储，实际中可以更改
            with open(filepath,'wb') as up:
                up.write(meta['body'])
            self.render('upload.html',m="报告提交成功！")



#主运行
if __name__ == "__main__":
    settings = {
    "template_path": os.path.join(os.path.dirname(__file__), "templates"),
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "cookie_secret": "pn6OqYE4RNi012c1pcF26gbDQTiEA07Ynniqz+TGyAw=",
    "xsrf_cookies": True, #开启伪造POST请求防护功能
    "login_url": "/login"
    }
    #路由表
    Handlers = [(r'/login', LoginHandler),
              (r'/', IndexHandler),
              (r'/stu', StuindexHandler),
              (r'/logout', LogoutHandler),
                (r'/regist', RegistHandler),
                (r'/thm',Thingsman),
                (r'/tem',Techman),
                (r'/prm',Projman),
                (r'/stu/prm',StuprmHandler),
                (r'/personal', PersonalHandler),
                (r'/password/(\d+)', ChangepassHandler),
                (r'/thm/device', D_IndexHandler),
                (r'/thm/device/new', D_NewHandler),
                (r'/thm/device/(\d+)/edit', D_EditHandler),
                (r'/thm/device/(\d+)/delete', D_DeleteHandler),
                (r'/thm/device/(\d+)/finish', D_FinishHandler),
                (r'/thm/worker', ThmworkerHandler),
                (r'/thm/worker/edit', WorkerEdit),
                (r'/thm/record/new', NewrecordHandler),
                (r'/thm/record/all', Displayre),
                (r'/thm/record/search', Searchdiary),
                (r'/thm/record/download/(.*)', OutrecordHandler),
                (r'/prm/new', NewproHandler),
                (r'/prm/all', SeeallproHandler),
                (r'/prm/search', ProsearchHandler),
                (r'/prm/delete/(\d+)', DeleteproHandler),
                (r'/tem/all', AllscoreHandler),
                (r'/tem/search/(\d+)', SearchscoreHandler),
                (r'/stu/score', StuscoreHandler),
                (r'/tem/sign/new', NewsignHandler),
                (r'/tem/sign/condition/(\d+)', NowsignHandler),
                (r'/tem/sign/history', SignhistoryHandler),
                (r'/stu/sign', StusignHandler),
                (r'/stu/upload', UploadFileHandler)
              ]
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers=Handlers, **settings )
    http_sever = tornado.httpserver.HTTPServer(app)
    http_sever.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()