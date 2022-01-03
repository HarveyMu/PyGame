import os
import pygame


class MusicPlayer:
    """音乐播放器"""
    res_path = "./res/sound/"  # 声音资源路径

    def __init__(self, music_file):
        # 加载背景音乐
        pygame.mixer.music.load(self.res_path + music_file)
        pygame.mixer.music.set_volume(0.2)
        # 加载音效字典
        # 定义音效字典属性
        self.sound_dict = {}
        # 获取目录下的文件列表
        files = os.listdir(self.res_path)
        # 遍历文件列表
        for file_name in files:
            # 排除背景音乐
            if file_name == music_file:
                continue
            # 创建声音对象
            sound = pygame.mixer.Sound(self.res_path + file_name)
            # 添加到音效字典, 使用文件名作为字典的键
            self.sound_dict[file_name] = sound

    def play_sound(self, wav_name):
        """
        播放音效
        :param wav_name: 音效文件名
        :return:
        """
        self.sound_dict[wav_name].play()

    @staticmethod
    def play_music():
        pygame.mixer.music.play(-1)

    @staticmethod
    def pause_music(is_pause):
        if is_pause:
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()
