from flask import Flask, render_template_string
import requests

app = Flask(__name__)

# HTML模板，包含变量插值
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>放学快乐时光</title>
    <style>
        body {
            font-family: 'Arial Rounded MT Bold', 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            margin: 0;
            padding: 0;
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            overflow: hidden;
        }
        
        .container {
            background-color: rgba(255, 255, 255, 0.9);
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            padding: 40px;
            width: 80%;
            max-width: 800px;
        }
        
        h1 {
            color: #ff6b6b;
            font-size: 4rem;
            margin-bottom: 30px;
            text-shadow: 3px 3px 0 rgba(255, 107, 107, 0.2);
        }
        
        .music-info {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            font-size: 1.5rem;
            color: #333;
            box-shadow: inset 0 0 10px rgba(0,0,0,0.1);
        }
        
        .button-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 20px;
            margin-top: 30px;
        }
        
        .btn {
            padding: 15px 30px;
            border: none;
            border-radius: 50px;
            font-size: 1.1rem;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            min-width: 200px;
        }
        
        .btn:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
        }
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
</head>
<body>
    <div class="container">
        <h1>放学啦！</h1>
        
        <div class="music-info">
            <i class="fas fa-music"></i> 用户{{ user }} 点了歌曲《{{ music }}》
        </div>
        
        <div class="button-container">
            <button class="btn" style="background-color: #e74c3c; color: white;" onclick="window.open('https://www.xinhuanet.com/', '_blank')">
                <i class="fas fa-newspaper"></i> 新华网
            </button>
            
            <button class="btn" style="background-color: #3498db; color: white;" onclick="window.open('https://basic.smartedu.cn/', '_blank')">
                <i class="fas fa-graduation-cap"></i> 智慧中小学
            </button>
            
            <button class="btn" style="background-color: #2c3e50; color: white;" onclick="window.open('https://github.com/', '_blank')">
                <i class="fab fa-github"></i> Github
            </button>
            
            <button class="btn" style="background-color: #fb7299; color: white;" onclick="window.open('https://www.bilibili.com/', '_blank')">
                <i class="fas fa-tv"></i> 哔哩哔哩
            </button>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    # 默认值
    user = "匿名用户"
    music = "未指定歌曲"
    return render_template_string(HTML_TEMPLATE, user=user, music=music)

@app.route('/<user>/<music>')
def show_music_request(user, music):
    return render_template_string(HTML_TEMPLATE, user=user, music=music)

@app.route('/music')
def show_music():
    user = requests.args.get('user', '匿名用户')
    music = requests.args.get('music', '未指定歌曲')
    return render_template_string(HTML_TEMPLATE, user=user, music=music)

if __name__ == '__main__':
    app.run(debug=True)