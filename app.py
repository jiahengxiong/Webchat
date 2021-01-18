#-*-coding:utf-8-*-
import os
import tornado.websocket
import tornado.web
import tornado.ioloop
import time
from tornado.options import define, options, parse_command_line
define('port', default=80, type=int)
user_online = []
user_list=[]
class LoginHandler(tornado.web.RequestHandler):

    def get(self):
        self.render('login.html')

    def post(self):
        # 获取登录用户信息
        username = self.get_argument('username')
        user_list.append(username)
        self.set_secure_cookie('username', username)
        self.render('chat.html', username=username,userlist=str(user_list))



class ChatHandler(tornado.websocket.WebSocketHandler):

    # 用于存放连接的对象




    def open(self, *args, **kwargs):
        user_online.append(self)
        username = self.get_secure_cookie('username').decode('utf-8')
        for line in open("news.txt"):
            self.write_message(line)
        for user in user_online:
            # 当进入chat.html页面时，会主动触发该函数
            if user==self:
                user.write_message('系统提示:【您已进入聊天室(%s)】<以上为历史消息>' % (time.ctime()))
            else:
                # username = self.get_cookie('username')
                user.write_message('系统提示:【%s已进入聊天室(%s)】' % (username,time.ctime()))

    def on_message(self, message):
        # 接收前端传的数据
        username = self.get_secure_cookie('username').decode('utf-8')
        f=open('news.txt','a')
        d='%s>>:%s(%s)' % (username,message,time.ctime())
        f.write(d+'\n')
        f.close()
        for user in user_online:
            user.write_message(d)

    def on_close(self):
        # 移除连接对象
        username = self.get_secure_cookie('username').decode('utf-8')
        user_online.remove(self)
        user_list.remove(username)
        for user in user_online:

            user.write_message('系统提示:【%s已退出聊天室(%s)】' % (username,time.ctime()))




def make_app():
    return tornado.web.Application(handlers=[
        (r'/', LoginHandler),
        (r'/chat/', ChatHandler),
    ],
    template_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'),
    static_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static'),
    cookie_secret='agdfiuwetr9w4689rfhjdc'
    )

if __name__ == '__main__':
    parse_command_line()
    app = make_app()
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


