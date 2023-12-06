import json

# 从 JSON 文件中读取数据
with open('data.json', 'r') as json_file:
    data = json.load(json_file)

# 打印读取到的数据
for key,value in data.items():
    print(value['title'])
