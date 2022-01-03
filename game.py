import pygame
from game_hud import *
from game_items import *
from game_hud import *
from game_music import *
import random


class Game(object):
    """游戏类"""

    def __init__(self):
        # 游戏主窗口
        self.main_window = pygame.display.set_mode(SCREEN_RECT.size)
        pygame.display.set_caption("飞机大战")
        # 游戏状态属性
        self.is_game_over = False  # 结束标记
        self.is_pause = False  # 暂停标记

        # 精灵组属性
        self.all_group = pygame.sprite.Group()
        self.enemies_group = pygame.sprite.Group()
        self.supplies_group = pygame.sprite.Group()
        # #创建精灵
        # 背景精灵, 交替滚动
        self.all_group.add(Background(False), Background(True))
        # 指示器面板
        self.hud_panel = HudPanel(self.all_group)
        # 创建敌机
        self.create_enemies()
        # 英雄精灵
        self.hero = Hero(self.all_group)
        # 设置面板中的炸弹数量
        self.hud_panel.show_bomb(self.hero.bomb_count)
        # 创建道具
        self.create_supplies()
        # 创建音乐播放器
        self.player = MusicPlayer("game_music.mp3")
        self.player.play_music()

    def check_collide(self):
        """检测碰撞"""
        # 检测英雄飞机和敌机的碰撞, 若飞机处于无敌状态, 彼此不能碰撞
        if not self.hero.is_power:
            # noinspection PyTypeChecker
            enemies = pygame.sprite.spritecollide(self.hero, self.enemies_group, False, pygame.sprite.collide_mask)
            # 过滤掉已经被撞毁的敌机
            enemies = list(filter(lambda x: x.hp > 0, enemies))
            # 是否碰撞敌机
            if enemies:
                self.hero.hp = 0  # 英雄被撞毁
            for enemy in enemies:
                enemy.hp = 0  # 敌机被撞毁
        # 检测敌机是否被子弹击中
        hit_enemies = pygame.sprite.groupcollide(self.enemies_group, self.hero.bullets_group, False, False,
                                                 pygame.sprite.collide_mask)
        # 遍历字典
        for enemy in hit_enemies:
            # 已经被催毁的敌机, 不需要浪费子弹
            if enemy.hp <= 0:
                continue
            # 遍历击中敌机的子弹列表
            for bullet in hit_enemies[enemy]:
                # 将子弹从所有精灵组中清除
                bullet.kill()
                # 修改敌机的生命值
                enemy.hp -= bullet.damage
                # 如果敌机没有被催毁, 继续判定下一颗子弹
                if enemy.hp > 0:
                    continue
                # 修改游戏得分并判断是否升级
                if self.hud_panel.increase_score(enemy.value):
                    self.create_enemies()
                # 退出遍历子弹列表循环
                break
        # 英雄拾取道具
        supplies = pygame.sprite.spritecollide(self.hero, self.supplies_group, False, pygame.sprite.collide_mask)
        if supplies:
            supply = supplies[0]
            # 将道具设置到游戏窗口正下方
            supply.rect.y = SCREEN_RECT.h
            # 判断道具类型
            if supply.kind == 0:
                self.hero.bomb_count += 1
                self.hud_panel.show_bomb(self.hero.bomb_count)
            else:
                self.hero.bullets_kind = 1
                # 设置结束子弹增强效果定时器的事件
                pygame.time.set_timer(BULLET_ENHANCED_OFF_EVENT, 8000)

    def reset_game(self):
        """重置游戏"""
        self.is_game_over = False
        self.is_pause = False
        self.hud_panel.reset_panel()  # 重置指示器面板
        # 设置英雄飞机的初始位置
        self.hero.rect.midbottom = HERO_DEFAULT_MID_BOTTOM
        # 清空所有敌机
        for enemy in self.enemies_group:
            enemy.kill()
        # 清空残留子弹
        for bullet in self.hero.bullets_group:
            bullet.kill()
        # 重新创建敌机
        self.create_enemies()

    # 监听游戏中的事件
    def event_handler(self):
        """事件监听
        :return 如果监听到退出事件， 返回True , 否则返回False
        """
        for event in pygame.event.get():
            # 判断是否在玩游戏
            if not self.is_game_over and not self.is_pause:
                # 监听结束子弹增强效果定时器事件
                if event.type == BULLET_ENHANCED_OFF_EVENT:
                    self.hero.bullets_kind = 0
                    pygame.time.set_timer(BULLET_ENHANCED_OFF_EVENT, 0)
                # 监听投放道具事件
                if event.type == THROW_SUPPLY_EVENT:
                    supply = random.choice(self.supplies_group.sprites())
                    supply.throw_supply()
                # 监听发射子弹事件
                if event.type == HERO_FIRE_EVENT:
                    self.player.play_sound("bullet.wav")
                    self.hero.fire(self.all_group)
                # 监听取消英雄飞机无敌的事件
                if event.type == HERO_POWER_OFF_EVENT:
                    print("取消无敌状态...")
                    # 设置英雄飞机状态
                    self.hero.is_power = False
                    # 取消定时器
                    pygame.time.set_timer(HERO_POWER_OFF_EVENT, 0)
                # 监听英雄飞机牺牲事件
                if event.type == HERO_DEAD_EVENT:
                    print("英雄牺牲了...")
                    # 生命计数-1
                    self.hud_panel.lives_count -= 1
                    # 更新生命计数显示
                    self.hud_panel.show_lives()
                    # 更新炸弹显示
                    self.hud_panel.show_bomb(self.hero.bomb_count)
                # 监听玩家按下"b"键, 引爆1颗炸弹
                if event.type == pygame.KEYDOWN and event.key == pygame.K_1:
                    # 如果英雄飞机没有牺牲同时有炸弹
                    if self.hero.hp > 0 and self.hero.bomb_count > 0:
                        self.player.play_sound("me_down.wav")
                    # 引爆炸弹
                    score = self.hero.blowup(self.enemies_group)
                    # 更新炸弹数量显示
                    self.hud_panel.show_bomb(self.hero.bomb_count)
                    # 更新游戏得分, 若关卡等级提升， 则可创建新类型的敌机
                    if self.hud_panel.increase_score(score):
                        self.create_enemies()
            if event.type == pygame.QUIT:
                return True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if self.is_game_over:  # 游戏已经结束
                    self.reset_game()  # 重新开始游戏
                else:
                    self.is_pause = not self.is_pause  # 切换暂停状态
                    # 暂停或恢复背景音乐
                    self.player.pause_music(self.is_pause)
            return False

    # 开始游戏
    def start(self):
        clock = pygame.time.Clock()
        frame_counter = 0  # 计数器
        while True:
            # 生命计数等于0, 表示游戏结束
            self.is_game_over = self.hud_panel.lives_count == 0
            if self.event_handler():  # 事件监听
                self.hud_panel.save_best_score()
                return
            # 判断游戏状态
            if self.is_game_over:
                self.hud_panel.panel_pause(True, self.all_group)
            elif self.is_pause:
                self.hud_panel.panel_pause(False, self.all_group)
            else:
                self.hud_panel.panel_resume(self.all_group)
                # 碰撞检测
                self.check_collide()
                # 获取当前时刻的按键元组
                keys = pygame.key.get_pressed()
                # 水平移动基数
                move_hor = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
                # 垂直移动基数
                move_ver = keys[pygame.K_DOWN] - keys[pygame.K_UP]
                # 修改逐帧动画计数器
                frame_counter = (frame_counter + 1) % FRAME_INTERVAL
                # 更新all_group所有精灵
                self.all_group.update(frame_counter == 0, move_hor, move_ver)
            # 绘制all_group中的所有精灵
            self.all_group.draw(self.main_window)
            pygame.display.update()
            clock.tick(60)

    def create_enemies(self):
        """根据关卡级别创建不同数量的敌机"""
        # 敌机精灵组中的精灵数量
        count = len(self.enemies_group.sprites())
        # 要添加到的精灵族
        groups = (self.all_group, self.enemies_group)
        # 判断关卡级别及已有的敌机数量
        if self.hud_panel.level == 1 and count == 0:  # 关卡级别1
            for i in range(8):
                Enemy(0, 1, *groups)
        elif self.hud_panel.level == 2 and count == 8:  # 关卡级别2
            # 提高敌机的最大速度
            for enemy in self.enemies_group.sprites():
                enemy.max_speed = 2
            # 创建敌机
            for i in range(4):
                Enemy(0, 2, *groups)
            for i in range(2):
                Enemy(1, 1, *groups)
        elif self.hud_panel.level == 3 and count == 14:  # 关卡级别3
            for enemy in self.enemies_group.sprites():
                # noinspection PyUnresolvedReferences
                enemy.max_speed = 3 if enemy.kind == 0 else 3
            for i in range(4):
                Enemy(0, 3, *groups)
            for i in range(1):
                Enemy(1, 2, *groups)
            for i in range(1):
                Enemy(2, 1, *groups)

    def create_supplies(self):
        """创建道具"""
        Supply(0, self.supplies_group, self.all_group)
        Supply(1, self.supplies_group, self.all_group)
        # 设置30s投放道具定时器事件(测试时用10s)
        pygame.time.set_timer(THROW_SUPPLY_EVENT, 10000)


if __name__ == '__main__':
    pygame.init()
    Game().start()
    pygame.quit()
