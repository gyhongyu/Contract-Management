# 导入应用工厂函数
from app import create_app

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    # 启动开发服务器
    app.run(debug=True)