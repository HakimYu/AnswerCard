import os
import re

dir_path = os.path.dirname(os.path.abspath(__file__)) +'/pic' # 指定目录路径
file_exts = ["jpg", "jpeg", "png", "bmp"]  # 指定文件扩展名

for file_name in os.listdir(dir_path):
    try:
        file_ext = file_name.split(".")[-1].lower()
        if file_ext in file_exts:
            new_name = re.sub(r"\D", "", file_name.split(".")[0]) + "." + file_ext
            os.rename(os.path.join(dir_path, file_name), os.path.join(dir_path, new_name))
    except Exception as e:
        print(file_name)

print("完成！")