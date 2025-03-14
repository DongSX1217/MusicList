import os,requests,json

import tkinter
from tkinter import messagebox
from moviepy import AudioFileClip
import pygame


def download_file(url, local_filename):
    """下载文件到本地"""
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename


def convert_to_mp3(input_file, output_file):
    """将音频文件转换为MP3格式"""
    audio_clip = AudioFileClip(input_file)
    audio_clip.write_audiofile(output_file, codec="mp3")
    audio_clip.close()


def play_audio(file_path):
    """使用pygame播放音频文件"""
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

def change_data(data):
    """更新数据文件"""
    with open("data/data.json", "r", encoding="utf-8") as file:
        data_list = json.load(file)
    data_list['music'].pop(0)
    data_list['music_already'].append(data)
    with open("data/data.json", "w", encoding="utf-8") as file:
        json.dump(data_list, file, ensure_ascii=False, indent=4)

def main():
    # 示例音频文件路径或URL
    with open("data/data.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    data = data['music'][0]
    music = data['name']
    path = data['url']

    local_file_path = "./music/" + music + ".mp3"
    converted_file_path = "./music/" + music + ".mp3"

    if os.path.isfile(path):
        audio_source = path
        # 如果是本地文件，先转换为MP3格式
        convert_to_mp3(audio_source, converted_file_path)
        play_audio(converted_file_path)
        os.remove(converted_file_path)  # 播放完成后删除临时文件
    else:
        # 如果是URL，先下载文件，然后转换为MP3格式
        audio_source = path
        print(f"Downloading {audio_source} to {local_file_path}")# 打印下载进度
        download_file(audio_source, local_file_path)# 下载文件
        convert_to_mp3(local_file_path, converted_file_path)# 转换为MP3格式
        play_audio(converted_file_path)
        os.remove(local_file_path)  # 删除原始M4A文件

    root = tkinter.Tk()
    root.withdraw()  # 隐藏主窗口
    confirm = messagebox.askyesno("确认修改", "您是否要修改列表吗？")
    if confirm:
        # 更新设置 
        change_data(data)  # 更新数据文件
        print("列表已成功修改")
    else:
        print("取消修改")


if __name__ == "__main__":
    main()
