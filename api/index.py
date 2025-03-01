from flask import Flask
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# 导出 app 变量供 Vercel 使用
app.debug = False

# 确保这个文件被作为主程序运行时才启动服务器
if __name__ == '__main__':
    app.run() 