import time
import re
from pymysql import connect
from urllib import parse


g_path_func = {}
# 希望在装饰器函数中完成 资源路径和 函数一一对应
def route(path_info):
    def set_fun(func):
        # 完成路径和函数的一一对应的关系  "/index.py"  --> index
        # "/index.py"  --> index
        g_path_func[path_info] = func
        def call_func():

            return func()

        return call_func

    return set_fun



@route(r"/index.html")  # route("/idnex.py")  返回值 是set_fun 作为装饰器函数 装饰index, index = set_fun(index)
def index(pattern, path_info):
    # 打开首页模板
    # open 打开文件路径相对的是运行的主模块
    with open("./templates/index.html",encoding="utf-8") as f:
        content = f.read()
    # 从mysql中获取数据
    conn = connect(host="localhost", user="root", password="root",
                 database="ttt", port=3306,charset='utf8')
    cur = conn.cursor()
    sql = "select * from info"
    cur.execute(sql)
    ret = cur.fetchall()
    html_templates = """<tr>
                            <td>%s</td>
                            <td>%s</td>
                            <td>%s</td>
                            <td>%s</td>
                            <td>%s</td>
                            <td>%s</td>
                            <td>%s</td>
                            <td>%s</td>
                            <td>
                                <input type="button" value="添加" id="toAdd" name="toAdd" systemidvaule="%s">
                            </td>
                        </tr>"""
    # 给数据的数据添加标签<tr><td>全新好</td></tr>
    html = ""
    for item in ret:
        html += html_templates % (item[0],item[1],item[2],item[3],item[4],item[5],item[6],item[7],item[1])

    content = re.sub(r"\{%content%\}",html,content)
    cur.close()
    conn.close()

    return content


@route(r"/center.html")
def center(pattern, path_info):
    # 打开center.html模板文件
    with open("./templates/center.html", encoding="utf-8") as f:
        content = f.read()
    # 从数据库中获取数据
    conn = connect(host="localhost", user="root", password="root",
                   database="ttt", port=3306, charset='utf8')
    cur = conn.cursor()
    sql = "select i.code,i.short,i.chg,i.turnover,i.price,i.highs,f.note_info from info as i inner join focus as f on i.id = f.info_id"
    cur.execute(sql)
    ret = cur.fetchall()
    html_templates = """<tr>
                           <td>%s</td>
                           <td>%s</td>
                           <td>%s</td>
                           <td>%s</td>
                           <td>%s</td>
                           <td>%s</td>
                           <td>%s</td>
                           <td>
                               <a type="button" class="btn btn-default btn-xs" href="/update/%s.html"> <span class="glyphicon glyphicon-star" aria-hidden="true"></span> 修改 </a>
                           </td>
                           <td>
                               <input type="button" value="删除" id="toDel" name="toDel" systemidvaule="%s">
                           </td>
                       </tr>"""
    # 给数据的数据添加标签<tr><td>全新好</td></tr> # 将数据的数据添加tr和td标签
    html = ""
    for item in ret:
        html += html_templates % (item[0], item[1], item[2], item[3], item[4], item[5], item[6],item[0],item[0])
    # 通过正则将{%content%} 进行替换
    content = re.sub(r"{%content%}",html,content)

    cur.close()
    conn.close()

    # 返回数据
    return content


# /add/000050.html
# 正则表达式能够对应n个访问的路径, 路由的功能更加强大
@route(r"/add/([\d]{6}).html")
def add(pattern, path_info):
    # 点击添加按钮: 将点击的股票信息添加关注的数据表中
    # 路径中包含了股票代码
    ret = re.match(pattern,path_info)
    code = ret.group(1)
    print(code)
    conn = connect(host="localhost", user="root", password="root",
                   database="ttt", port=3306, charset='utf8')
    cur = conn.cursor()

    # 在插入数据之前 需要判断该股票的信息是否在focus表中存在, 已知code
    sql = "select * from focus where info_id = (select id from info where code = %s)"
    # 执行sql语句
    ret = cur.execute(sql, [code])
    if ret > 0:
        cur.close()
        conn.close()
        return "请不要重复关注股票哟"

    print("$"*100)
    sql = "insert into focus (info_id) select id from info where code = %s"
    cur.execute(sql, [code])
    # 如果是数据的更新操作需要commit
    conn.commit()
    # 关闭
    cur.close()
    conn.close()

    return "恭喜你, 关注%s股票成功" % code


@route(r"/del/([\d]{6}).html")
def unfocus(pattern, path_info):
    ret = re.match(pattern, path_info)
    code = ret.group(1)
    print(code)
    # 通过code 在focus 表中删除指定的数据
    conn = connect(host="localhost", user="root", password="root",
                   database="ttt", port=3306, charset='utf8')
    cur = conn.cursor()

    # 在插入数据之前 需要判断该股票的信息是否在focus表中存在, 已知code
    sql = "delete from focus where info_id = (select id from info where code = %s)"
    cur.execute(sql, [code])
    # 提交
    conn.commit()
    cur.close()
    conn.close()
    return "取消关注%s股票成功" % code


@route(r"/update/([\d]{6}).html")
def update(pattern, path_info):
    """
    显示股票更新的页面
    :return:
    """
    ret = re.match(pattern, path_info)
    code = ret.group(1)
    print(code)
    # 1. 打开模板
    with open("./templates/update.html",encoding="utf-8") as f:
        content = f.read()
    # 2. 从数据库中查找数据 已知code
    conn = connect(host="localhost", user="root", password="root",
                   database="ttt", port=3306, charset='utf8')
    cur = conn.cursor()
    sql = "select note_info from focus where info_id = (select id from info where code = %s)"
    cur.execute(sql, [code])
    ret = cur.fetchone()  # 返回的是元组(xx,), 没有数据 返回None
    if ret:
        note_info = ret[0]
        # 3. 替换数据
        content = re.sub(r"{%code%}",code,content)
        content = re.sub(r"{%note_info%}",note_info,content)

    # 4. 返回数据
    # 关闭
    cur.close()
    conn.close()
    return content

# 将中文变成成%E9%BB%91%E9%A9%AC%E8%82%A1放到了URL中, 编码之后的结果能够被解码
# 在url地址中不能够存在中文和空格, 如果存在需要进行url编码
@route(r"/update/([\d]{6})/(.*).html")
def update_stockinfo(pattern, path_info):
    ret = re.match(pattern, path_info)
    code = ret.group(1)
    note_info = ret.group(2)
    note_info = parse.unquote(note_info)
    print(code)
    print(note_info)

    # 更新数据库的focus表
    conn = connect(host="localhost", user="root", password="root",
                  database="ttt", port=3306, charset='utf8')
    cur = conn.cursor()
    sql = "update focus set note_info = %s where info_id = (select id from info where code = %s)"
    ret = cur.execute(sql, [note_info,code]) # ret是受影响的行数
    if ret == 0:
        # 没有数据收到影响, 更新失败
        conn.rollback()
    else:
        # 数据更新需要提交
        conn.commit()

    cur.close()
    conn.close()

    return "恭喜你, 已经更新了技能包, 即将走向人生巅峰"



# 外界通用的调用方法
def application(environ, start_response):
    path_info = environ["PATH_INFO"]
    for pattern,func in g_path_func.items():
        # 进行匹配
        ret = re.match(pattern,path_info)
        if ret:
            # 匹配到结果
            start_response('200 OK', [('Content-Type', 'text/html;charset=utf-8'), ("Framework", "Flask v3.0")])
            return func(pattern,path_info)
    else:
        start_response('404 Not Found', [('Content-Type', 'text/html;charset=utf-8')])
        return "sorry not found your page.... %s" % time.ctime()

