import time
from gevent import monkey
monkey.patch_all()  # recv accept time.sleep -> 非阻塞模式
import socket
import re
import gevent
import sys
# import mini_framework
# 完成一种模拟, 不需要写死导入具体的模块


"""
web服务器 = TCP服务器 + HTTP协议<nginx C语言>

1.0 返回固定数据Hello world
2.0 返回固定页面
3.0 根据用户的需求返回指定的页面
4.0 协程多任务
5.0 面向对象封装

"""


class HTTPServer(object):
    def __init__(self, port, method):
        """初始化操作"""
        # 创建TCP套接字
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # 设置端口重用的选项
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # 绑定 监听
        server_socket.bind(('', port))
        server_socket.listen(128)

        # 创建 一个属性
        self.server_socket = server_socket
        self.application = method
    def start(self):
        # 接受客户端连接
        while True:
            client_socket, client_addr = self.server_socket.accept()
            print("接受到来自%s的连接请求" % str(client_addr))
            # 创建并且启动一个协程 对客户端的请求进行处理
            # client_handler(client_socket, client_addr)
            gevent.spawn(self.client_handler, client_socket, client_addr)

    def client_handler(self, client_socket, client_addr):
        """处理和客户端相关的请求  回复响应报文数据"""
        # 接收请求报文
        request_data = client_socket.recv(4096)
        if not request_data:
            print("客户端%s 已经断开了连接" % str(client_addr))
            return

        # print(request_data)
        # 对请求报文进行切割
        request_str_data = request_data.decode()
        data_list = request_str_data.split("\r\n")
        # print(data_list)

        # 列表的第0个元素就是请求行 获取  GET /index2.html HTTP/1.1
        request_line = data_list[0]
        # print(request_line)

        # 从请求行中获取到 资源请求路径
        result = re.match(r"\w+\s+(\S+)", request_line)
        if not result:
            print("用户%s请求报文格式错误" % str(client_addr))
            return

        # 获取到分组中的数据就是用户请求的资源路径
        path_info = result.group(1)
        print("获取用户资源请求路径%s" % path_info)

        # 当用户请求一个网页的时候 baidu.com ---> baidu.com/ --> 获取主页
        if path_info == '/':
            path_info = '/index.html'

        response_header = "Server: HMPython31WS 1.0\r\n"
        if path_info.endswith(".html"):
            # 请求动态资源

            # 在这里访问 self.status程序会崩溃 boom
            # response_line = "HTTP/1.1 %s\r\n" % self.status
            # 拼接响应报文
            envi = {
                "PATH_INFO": path_info
            }
            # 按照wsgi协议规定调用了框架的一个通用接口
            response_body = self.application(envi,self.start_response)
            response_line = "HTTP/1.1 %s\r\n" % self.status

            # 遍历列表
            for item in self.reponse_headers:
                response_header += "%s:%s\r\n" % (item[0], item[1])

            response_data = (response_line + response_header + "\r\n" + response_body).encode()
            client_socket.send(response_data)
            # 关闭
            client_socket.close()
        else:
            # 静态资源
            # 回复响应报文
            try:
                # ./static/index.html     ./static/home/python/Desktop/亲爱的.jpg
                with open("./static" + path_info, "rb") as file:
                    file_data = file.read()
                response_body = file_data
            except Exception as e:
                response_line = "HTTP/1.1 404 Not Found\r\n"
                response_body = "ERORR" + str(e)
                response_data = response_line + response_header + "\r\n" + response_body
                client_socket.send(response_data.encode())
            else:
                response_line = "HTTP/1.1 200 OK\r\n"

                # 拼接响应报文
                response_data = (response_line + response_header + "\r\n").encode() + response_body
                client_socket.send(response_data)

            finally:
                # 关闭套接字
                client_socket.close()

    def start_response(self,status, response_headers):
        print("*"*100)
        self.status = status
        self.reponse_headers = response_headers
        print(status)
        print(response_headers)


def main():
    print(sys.argv)
    # 判断用户输入的参数的个数
    if 4 != len(sys.argv):
        print("你的打开方式不对 python3 web.py 8080")
        return
    # 第一个元素就是端口-字符串类型  健壮性-鲁棒性
    if not sys.argv[1].isdigit():
        print("你的打开方式不对 python3 web.py 8080")
        return

    port = int(sys.argv[1])

    # 内建方法
    module_name = sys.argv[2]
    method_name = sys.argv[3]
    # 根据模块名完成动态导入
    # 需要添加搜索路径
    sys.path.insert(0,"./flask")
    module = __import__(module_name)
    print(module)
    print(module.application)
    # 指定需要获取属性的对象和属性的名称
    app_method = getattr(module, method_name)
    print(app_method)

    # 创建一个HTTP服务
    http_server = HTTPServer(port,app_method)

    # 启动HTTP服务
    http_server.start()





if __name__ == '__main__':
    main()