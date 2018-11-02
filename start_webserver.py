#encoding:utf-8
import requests
import json
import web
import os
import pandas as pd
import math
"""
author:hc
time:2018-11-2
"""


# URL映射
urls = (
    '/', 'Index',
    '/request', 'RequestData',
    '/view/(/d+)', 'View',
    '/local', 'Local',
    '/delete/(/d+)', 'Delete',
    '/edit/(/d+)', 'Edit',
    '/login', 'Login',
    '/pagechange', 'pageChange',
    '/url_notfond', 'url_NotFond',
    '/params_notfond', 'paramsError',
)
app = web.application(urls, globals())
# 模板公共变量
t_globals = {
    'datestr': web.datestr,
    'cookie': web.cookies,
}
# 指定模板目录，并设定公共模板
render = web.template.render('templates/')
# 创建输入表单
input_url_form = web.form.Form(
        web.form.Textbox('request_url'),
        web.form.Textbox('params'),
        web.form.Textbox('data_type'),
        web.form.Button('submit')
    )
input_path_form = web.form.Form(
        web.form.Textbox('local_url'),
        web.form.Textbox('file_name'),
        web.form.Textbox('data_type'),
        web.form.Button('submit')
    )
# 首页类
class Index:
    def GET(self):
        form1 = input_url_form()
        form2 = input_path_form()

        return render.index(form1,form2)

# request 类
class RequestData:
    def POST(self):
        request_res= web.input(request_url=None,params=None)
        request_url = request_res["request_url"]
        request_params = request_res["params"]
        data_type = request_res["data_type"]
        step = 10
        params_str = ""
        for k,v in json.loads(request_params).items():
            params_str = params_str + "&" + str(k) + "=" + str(v)
        r = requests.get(url=request_url,params=params_str)
        res=r.content
        if r.status_code == 404:
            raise web.seeother('/url_notfond')
        elif r.status_code == 200:
            res_data = json.loads(res)["data"]
            if len(res_data) == 0:
                raise web.seeother('/params_notfond')
        global data
        data = res_data
        if data_type == "essay":
            i = 0
            global page_num
            page_num = math.ceil(len(data) / step)
            global page_list
            page_list = range(0, len(data), step)
            return render.online_essay_view(data,page_num,page_list,i)
        elif data_type == "filter": #TODO
            return render.online_essay_view(data,page_num,page_list)

#本地数据类
class Local:
    def POST(self):
        local_path= web.input(request_url=None,params=None)
        local_url = local_path["local_url"]
        file_name = local_path["file_name"]
        data_type = local_path["data_type"]
        file_type = local_path["file_type"]
        if local_url[-1] != "/":
            local_url = local_url+"/"
        if not os.path.exists(local_url):
            raise web.seeother('/url_notfond')

        if not os.path.exists(local_url+file_name):
            raise web.seeother('/params_notfond')
        global data
        step = 10
        if file_type == "json":
            with open(local_url+file_name,"r") as f:
                data_dict = json.load(f)
            if data_type == "essay":
                data = []
                i = 0
                for k in data_dict.keys():
                    data.append(data_dict[k])
                global page_num
                page_num = int(math.ceil(len(data)*1.0 / step))
                global page_list
                page_list = range(0, len(data), step)
                return render.local_essay_view(data,page_num,page_list,i)
            elif data_type == "filter":
                i = 0
                data = data_dict
                global page_num
                page_num = int(math.ceil(len(data)*1.0 /step))
                global page_list
                page_list = range(0,len(data),step)
                return render.local_filter_view(data,page_num,page_list,i)
        elif file_type == "csv":
            df = pd.read_csv(local_url+file_name)
            if data_type == "filter":
                list_name = [column for column in df]
                data = []
                for i in range(0, len(df)):
                    line = {}
                    for key in list_name:
                        line[key] = df.iloc[i][key]
                    data.append(line)
                i = 0
                global page_num
                page_num = int(math.ceil(len(data)*1.0 / step))
                global page_list
                page_list = range(0, len(data), step)
                return render.local_filter_view_csv(data, page_num, page_list, i)

# 换页类
class pageChange:
    def GET(self):
        pageChange_info = web.input()
        i = pageChange_info["i"]
        aim = pageChange_info["aim"]
        max_page = pageChange_info["max_page"]
        file_name = pageChange_info["fn"]
        if int(i) == int(float(max_page))-1 and aim == "next" :
            i = int(i)
        elif aim == "next":
            i = int(i) + 1
        elif (int(i) == 0 and aim =="pre") or aim == "first":
            i = 0
        elif aim == "pre":
            i = int(i) - 1
        elif aim == "all":
            i = int(-1)
        if file_name == "lfv":
            return render.local_filter_view(data, page_num, page_list,i)
        elif file_name == "lfvc":
            return render.local_filter_view_csv(data, page_num, page_list, i)
        elif file_name == "lev":
            return render.local_essay_view(data, page_num, page_list, i)
        elif file_name == "oev":
            return render.online_essay_view(data, page_num, page_list, i)

# 定义404错误显示内容
class url_NotFond:
    def GET(self):
        re_path = "/"
        return render.url_notfond_view(re_path)
class paramsError:
    def GET(self):
        re_path = "/"
        return render.params_notfond_view(re_path)

# 系统内路由出错
def notfound():
    return web.notfound("Sorry, the page you were looking for was not found.")
app.notfound = notfound
# 运行
if __name__ == '__main__':
    app.run()