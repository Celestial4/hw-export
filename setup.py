import subprocess
import os
import sys
import re

def find_sdk():
    for root, dirs, files in os.walk("."):
        for i,f in enumerate(files):
            if f.endswith(".whl") and f.startswith("huawei"):
                return f
            else:
                if i == len(files):
                    print("没有找到华为sdk，请将sdk文件放置在该文件夹下。")
                    sys.exit(1)
                else:
                    continue     

def install_sdk():
    command=f"pip install {find_sdk()}"
    subprocess.run(command)
    subprocess.run("pip install xlwt")

def fix_sdk_bug():

    py_path=os.environ.get("pythonpath")
    file_path=os.path.join(py_path,"Lib\site-packages\huaweiresearchsdk\service\HiResearchDataService.py")

    pattern = r", encoding=\"utf8\""

    with open(file_path, 'r',encoding='utf-8') as file:
        content=file.read()
    update=re.sub(pattern,"",content)
    
    with open(file_path, 'w',encoding='utf-8') as file:
        content=file.write(update)

install_sdk()
fix_sdk_bug()
print("环境安装完毕！")
sys.exit(0)