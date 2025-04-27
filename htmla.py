from flask import Flask, render_template_string
import requests

app = Flask(__name__)

# HTML模板，包含变量插值
HTML_TEMPLATE = """
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>放学</title>
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
            position: relative;
            overflow: hidden;
        }
        
        .container::before {
            content: "";
            position: absolute;
            top: -10px;
            left: -10px;
            right: -10px;
            bottom: -10px;
            background: linear-gradient(45deg, #ff9a9e, #fad0c4, #fbc2eb, #a6c1ee);
            background-size: 400% 400%;
            z-index: -1;
            border-radius: 30px;
            animation: gradientBG 15s ease infinite;
            filter: blur(20px);
            opacity: 0.7;
        }
        
        @keyframes gradientBG {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        h1 {
            color: #ff6b6b;
            font-size: 4rem;
            margin-bottom: 30px;
            text-shadow: 3px 3px 0 rgba(255, 107, 107, 0.2);
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        
        .subtitle {
            color: #666;
            font-size: 1.5rem;
            margin-bottom: 40px;
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
            display: flex;
            align-items: center;
            justify-content: center;
            min-width: 200px;
        }
        
        .btn:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
        }
        
        .btn i {
            margin-right: 10px;
            font-size: 1.3rem;
        }
        
        .btn-xinhua {
            background-color: #e74c3c;
            color: white;
        }
        
        .btn-edu {
            background-color: #3498db;
            color: white;
        }
        
        .btn-github {
            background-color: #2c3e50;
            color: white;
        }
        
        .btn-bilibili {
            background-color: #fb7299;
            color: white;
        }
        
        .confetti {
            position: absolute;
            width: 10px;
            height: 10px;
            background-color: #f00;
            border-radius: 50%;
            animation: fall 5s linear infinite;
        }
        
        @keyframes fall {
            to { transform: translateY(100vh) rotate(360deg); }
        }
        
        @media (max-width: 768px) {
            h1 { font-size: 2.5rem; }
            .subtitle { font-size: 1.2rem; }
            .btn { min-width: 150px; padding: 12px 20px; }
        }
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
</head>
<body>
    <div class="container">
        <h1>放学力！</h1>
        <div class="subtitle">今日放学音乐：《{{ music }}》<br>点歌人：{{user}}
        </div>
        <div class="button-container">
            <button class="btn btn-xinhua" onclick="window.open('https://www.xinhuanet.com/', '_blank')">
                <i class="fas fa-newspaper"></i> 新华网
            </button>
            
            <button class="btn btn-edu" onclick="window.open('https://basic.smartedu.cn/', '_blank')">
                <i class="fas fa-graduation-cap"></i> 智慧中小学
            </button>
            
            <button class="btn btn-github" onclick="window.open('https://github.com/', '_blank')">
                <i class="fab fa-github"></i> Github
            </button>
            
            <button class="btn btn-bilibili" onclick="window.open('https://www.bilibili.com/', '_blank')">
                <i class="fas fa-tv"></i> 哔哩哔哩
            </button>
        </div>
    </div>

    <script>
        // 创建彩色纸屑效果
        function createConfetti() {
            const colors = ['#ff6b6b', '#48dbfb', '#1dd1a1', '#feca57', '#5f27cd', '#ff9ff3'];
            
            for (let i = 0; i < 50; i++) {
                const confetti = document.createElement('div');
                confetti.className = 'confetti';
                confetti.style.left = Math.random() * 100 + 'vw';
                confetti.style.top = -10 + 'px';
                confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
                confetti.style.width = Math.random() * 10 + 5 + 'px';
                confetti.style.height = confetti.style.width;
                confetti.style.animationDuration = Math.random() * 3 + 2 + 's';
                confetti.style.animationDelay = Math.random() * 2 + 's';
                document.body.appendChild(confetti);
                
                // 移除纸屑元素以避免内存泄漏
                setTimeout(() => {
                    confetti.remove();
                }, 5000);
            }
        }
        
        // 初始纸屑效果
        createConfetti();
        
        // 每3秒创建新的纸屑
        setInterval(createConfetti, 3000);
    </script>
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

'''
@app.route('/music')
def show_music():
    user = requests.args.get('user', '匿名用户')
    music = requests.args.get('music', '未指定歌曲')
    return render_template_string(HTML_TEMPLATE, user=user, music=music)
'''

if __name__ == '__main__':
    app.run()
