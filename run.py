import xlwt
import sys
import json
from datetime import datetime
from huaweiresearchsdk.bridge import BridgeClient
from huaweiresearchsdk.config import BridgeConfig, HttpClientConfig
from huaweiresearchsdk.model.table import FilterCondition, FilterOperatorType, SearchTableDataRequest, FilterLogicType

def get_connection():
    bridgeconfig = BridgeConfig("product",config["accessKey"],config["secretKey"])
    # 连接超时时间，单位s，不设置则默认30s
    connect_timeout = 20
    # 等待接口返回超时时间，单位s，不设置则默认30s
    read_timeout = 20
    # 是否失败重试，默认不重试
    retry_on_fail = True
    # 初始化HttpClientConfig类
    httpconfig = HttpClientConfig(connect_timeout, read_timeout, retry_on_fail)
    bridgeclient = BridgeClient(bridgeconfig, httpconfig)
    return bridgeclient

def get_project_info():
    info = client.get_bridgedata_provider().list_projects()[0]
    dic = {}
    dic["id"] = info["projectId"]
    dic["code"]=info["projectCode"]
    return dic

def get_config_info():
    with open("config.json", 'r',encoding='utf8') as file:
        # 从 JSON 文件中加载对象
        data = json.load(file)
        return data

def get_fields(config_field):
    res_fields = list()
    for _,v in enumerate(config_field):
        res_fields.append(v["name"])
    return res_fields

def get_timeset(config):
    res=set()
    for _,f in enumerate(config):
        if "istime" in f:
            res.add(f["name"])
    return res

def get_table_id(table):
    return table["table_id"]

def process_extinfo(data,field,set):
    if field in set:
        try:
            # 尝试将字符串转换为 datetime 对象
            res=datetime.fromtimestamp(float(data)/1000)
            return str(res)
        except ValueError:
            # 转换失败，不是有效的时间戳
            return str(data)
    return str(data)

if __name__ == "__main__":

    config=get_config_info()
    tables=config["tables"]
    query_field=config["queryField"]
    client = get_connection()
    project_info = get_project_info()
    p_id=project_info["id"]

    flag=True
    while flag:
        def rows_processor(rows, totalCnt):
            print("totalCnt: ",totalCnt, "len(rows): ",len(rows))
            rs.extend(rows)

        def process(table_id ,fields , w_pos_col):
            condition = [FilterCondition(query_field, FilterOperatorType.EQUALS, userid)]
            sorted_fields=[{"name":"externalid","type":"desc"}]
            req=SearchTableDataRequest(table_id,filters=condition, desired_size=10000,sorts=sorted_fields,include_fields=fields,giveup_when_more_than=200000,project_id=p_id)
            client.get_bridgedata_provider().query_table_data(req,rows_processor)

            #写入sheet表
            w_pos_row=1
            for data in rs:
                for i,field in enumerate(fields):
                    names=field.split(".")
                    
                    #处理非空数据
                    if names[0] in data:
                        res_to_w=""
                        nextlevel_data=data[names[0]]
                        res_to_w=nextlevel_data
                        for j in range(1,len(names)):
                            next_level=names[j]
                            res_to_w=nextlevel_data[next_level]
                            nextlevel_data=res_to_w
                        res_to_w=process_extinfo(res_to_w,field,timeset)
                        ws.write(w_pos_row,i+w_pos_col,res_to_w)
                w_pos_row+=1
            #写完后清理数据
            rs.clear()

        #开始执行
        userid=input("输入查询信息：")

        if(userid == ""):
            print("未输入查询信息，请重新执行！")
            sys.exit(1)

        wb=xlwt.Workbook()
        ws=wb.add_sheet('sheet1')

        start_col=0
        #用于存储拉取的数据
        rs = list()
        timeset=set()
        for i,table in enumerate(tables):
            #读取配置文件中的表列名
            fields = table["fields"]
            timeset=timeset.union(get_timeset(fields))
            print("process table: ",table["table_name"])
            #写表头
            for j,title in enumerate(fields):
                ws.write(0,start_col+j,title["alias"])

            #写实体数据
            process(get_table_id(table),get_fields(fields),start_col)
            start_col+=len(fields)
        
        wb.save(userid+'.xls')
        cot=input("按任意键退出。 输入y/Y继续操作！")
        if(cot.lower() != "y"):
            flag=False
#1300-0008199133