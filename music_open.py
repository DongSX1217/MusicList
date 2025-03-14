import os
import requests
import json
import sys
import platform
from tkinter import messagebox
import tkinter

def download_file(url, local_filename):
    """下载文件到本地"""
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            os.makedirs(os.path.dirname(local_filename), exist_ok=True)  # 自动创建目录
            with open(local_filename, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:  # 过滤保持活动的空块
                        f.write(chunk)
        return local_filename
    except Exception as e:
        messagebox.showerror("下载错误", f"文件下载失败: {str(e)}")
        return None

def play_music(file_path):
    """使用系统默认播放器打开文件"""
    try:
        if platform.system() == 'Windows':
            os.startfile(file_path)
        elif platform.system() == 'Darwin':
            os.system(f'open "{file_path}"')
        else:
            os.system(f'xdg-open "{file_path}"')
    except Exception as e:
        messagebox.showerror("播放错误", f"无法播放文件: {str(e)}")

def main():
    try:
        # 确保data.json存在
        if not os.path.exists("data/data.json"):
            raise FileNotFoundError("data.json文件不存在")

        with open("data/data.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        
        if not data.get('music') or len(data['music']) == 0:
            raise ValueError("JSON文件中缺少音乐数据")
        
        first_music = data['music'][0]
        music_name = first_music['name']
        music_url = first_music['url']

        local_dir = "./music/"
        local_file_path = os.path.join(local_dir, f"{music_name}.mp3")

        # 如果是本地文件直接播放
        if os.path.isfile(music_url):
            play_music(music_url)
        else:  # 否则尝试下载后播放
            print(f"正在下载: {music_url}")
            downloaded_path = download_file(music_url, local_file_path)
            if downloaded_path and os.path.exists(downloaded_path):
                print(f"文件已保存至: {downloaded_path}")
                play_music(downloaded_path)

    except Exception as e:
        messagebox.showerror("错误", f"程序运行失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    root = tkinter.Tk()  # 创建Tk根窗口
    root.withdraw()      # 隐藏主窗口
    main()
