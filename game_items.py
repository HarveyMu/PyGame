import pygame
# noinspection PyUnresolvedReferences
import random

# 游戏窗口区域
SCREEN_RECT = pygame.Rect(0, 0, 480, 700)
# 记录逐帧动画更新的间隔帧数
FRAME_INTERVAL = 10
HERO_BOMB_COUNT = 3
# 英雄飞机默认初始位置
HERO_DEFAULT_MID_BOTTOM = (SCREEN_RECT.centerx, SCREEN_RECT.bottom - 90)
# 英雄飞机牺牲事件
HERO_DEAD_EVENT = pygame.USEREVENT
# 取消英雄飞机无敌的事件
HERO_POWER_OFF_EVENT = pygame.USEREVENT + 1
# 飞机发射子弹事件
HERO_FIRE_EVENT = pygame.USEREVENT + 2
# 投放道具事件
THROW_SUPPLY_EVENT = pygame.USEREVENT + 3
# 结束子弹增强定时器的事件
BULLET_ENHANCED_OFF_EVENT = pygame.USEREVENT + 4


# 基类
class GameSprite(pygame.sprite.Sprite):
    """游戏精灵类"""
    res_path = "./res/images/"  # 图片资源路径

    def __init__(self, image_name, speed, *groups):
        """构造方法
        :param image_name: 图片文件名
        :param speed: 移动速度, 0 表示静止不动
        :param groups: 要添加的精灵族, 不传值则不添加
        """
        super().__init__(*groups)
        # 图像
        self.image = pygame.image.load(self.res_path + image_name)
        self.rect = self.image.get_rect()  # 矩形区域, 默认在左上角
        self.speed = speed  # 移动速度
        # 图像遮罩, 可以提高碰撞检测的执行性能
        self.mask = pygame.mask.from_surface(self.image)

    """更新精灵位置, 默认在垂直"""

    def update(self, *args):
        self.rect.y += self.speed


# 背景类
class Background(GameSprite):
    """背景精灵类"""

    def __init__(self, is_alt, *groups):
        # 调用父类实现精灵的创建
        super().__init__("background.png", 1, *groups)
        # 判断是否是另一个精灵, 如果是, 需要设置初始位置
        if is_alt:
            self.rect.y = -self.rect.h  # 设置到游戏窗口正上方

    def update(self, *args):
        # 调用父类的方法实现向下运动
        super().update(*args)
        # 判断是否移出屏幕, 如果移除屏幕,, 将图像设置到屏幕的上方
        if self.rect.y >= self.rect.h:
            self.rect.y = -self.rect.h


# 三个状态按钮
class StatusButton(GameSprite):
    """状态按钮类"""

    def __init__(self, image_names, *groups):
        """
        构造方法
        :param image_names: 要加载的图像名称列表
        :param groups: 要添加的精灵组
        """
        super().__init__(image_names[0], 0, *groups)
        # 加载图像
        self.images = [pygame.image.load(self.res_path + name) for name in image_names]

    def switch_status(self, is_pause):
        """
        切换状态
        :param is_pause: 是否暂停
        :return:
        """
        self.image = self.images[1 if is_pause else 0]


# 3个状态按钮旁边的文本
class Label(pygame.sprite.Sprite):
    """文本标签精灵"""
    font_path = "./res/font/Wovebrik.ttf"  # 字体文本路径

    def __init__(self, text, size, color, *groups):
        """
        构造方法
        :param text: 文本内容
        :param size: 字体大小
        :param color: 字体颜色
        :param groups: 要添加到的精灵组
        """
        super().__init__(*groups)
        self.font = pygame.font.Font(self.font_path, size)
        self.color = color
        self.image = self.font.render(text, True, self.color)
        self.rect = self.image.get_rect()

    def set_text(self, text):
        """
        设置文本, 使用指定的文本重新渲染image, 并且更新rect
        :param text: 文本内容
        :return:
        """
        self.image = self.font.render(text, True, self.color)
        self.rect = self.image.get_rect()


class Plane(GameSprite):
    """飞机类"""

    def __init__(self, hp, speed, value, wav_name, normal_names, hurt_name, destroy_names, *groups):
        """
        构造方法
        :param normal_names: 记录正常飞行状态下的图像名称列表
        :param groups: 要添加到的精灵组
        """
        super().__init__(normal_names[0], speed, *groups)
        # 飞机属性
        self.hp = hp
        self.max_hp = hp
        self.value = value
        self.wav_name = wav_name
        # 图像属性
        # 加载正常图像列表
        self.normal_images = [pygame.image.load(self.res_path + name) for name in normal_names]
        self.normal_index = 0
        # 受伤图像
        self.hurt_image = pygame.image.load(self.res_path + hurt_name)
        # 被催婚图像列表及索引
        self.destroy_images = [pygame.image.load(self.res_path + name) for name in destroy_names]
        self.destroy_index = 0

    def reset_plane(self):
        """重置飞机"""
        self.hp = self.max_hp  # 生命值
        self.normal_index = 0  # 正常状态图像索引
        self.destroy_index = 0  # 被摧毁状态图像索引
        self.image = self.normal_images[0]  # 恢复正常图像

    def update(self, *args):
        # 如果第0个参数为False, 不需要更新图像, 直接返回
        if not args[0]:
            return
        # 判断飞机状态
        if self.hp == self.max_hp:  # 未受伤
            # 设置图像
            self.image = self.normal_images[self.normal_index]
            # 更新索引
            count = len(self.normal_images)
            self.normal_index = (self.normal_index + 1) % count
        elif self.hp > 0:  # 受伤
            self.image = self.hurt_image
        else:  # 被摧毁
            # 判断是否显示到最后一张图像, 若是说明飞机完全被摧毁
            if self.destroy_index < len(self.destroy_images):
                self.image = self.destroy_images[self.destroy_index]
                self.destroy_index += 1
            else:
                self.reset_plane()  # 重置飞机


class Enemy(Plane):
    """敌机类"""

    def __init__(self, kind, max_speed, *groups):
        # 记录敌机类型和最大速度
        self.kind = kind
        self.max_speed = max_speed
        # 根据类型调用父类方法传递不同参数
        if kind == 0:
            super().__init__(1, 1, 1000, "enemy1_down.wav", ["enemy1.png"], "enemy1.png",
                             ["enemy1_down%d.png" % i for i in range(1, 3)], *groups)
        elif kind == 1:
            super().__init__(6, 1, 6000, "enemy2_down.wav", ["enemy2.png"], "enemy2_hit.png",
                             ["enemy2_down%d.png" % i for i in range(1, 2)], *groups)
        else:
            super().__init__(15, 1, 15000, "enemy3_down.wav", ["enemy3_n1.png"], "enemy3_hit.png",
                             ["enemy3_down%d.png" % i for i in range(1, 2)], *groups)
        # 调佣重置飞机的方法, 设置敌机初始位置和速度
        self.reset_plane()

    def reset_plane(self):
        """重置飞机"""
        super().reset_plane()
        # 设置初识随机位置和速度
        # 设置随机x值
        x = random.randint(0, SCREEN_RECT.w - self.rect.w)
        # 设置随机y值
        y = random.randint(0, SCREEN_RECT.h-500)
        self.rect.topleft = (x, y)  # 作为初始位置
        self.speed = random.randint(1, self.max_speed)

    def update(self, *args):
        """更新图像及位置"""
        # 调用父类方法更新敌机图像 - 注意args 需要拆包
        super().update(*args)
        # 判断敌机是否被催毁, 若没有, 则根据速度更新敌机的位置
        if self.hp > 0:
            self.rect.y += self.speed
        # 飞机若飞出屏幕, 如果是, 重置飞机
        if self.rect.y >= SCREEN_RECT.h:
            self.reset_plane()


class Hero(Plane):
    """英雄飞机类"""

    def __init__(self, *groups):
        """
        构造方法
        :param groups: 要添加到的精灵组
        """
        super().__init__(1000, 5, 0, "me_down.wav", ["img%d.png" % i for i in range(1, 4)], "img1.png",
                         ["destroy_img%d.png" % i for i in range(1, 3)], *groups)
        self.is_power = False
        self.bomb_count = HERO_BOMB_COUNT
        self.bullets_kind = 0  # 子弹类型
        self.bullets_group = pygame.sprite.Group()  # 子弹精灵组
        # 初始位置
        self.rect.midbottom = HERO_DEFAULT_MID_BOTTOM
        # 设置0.2s发射子弹定时器事件
        pygame.time.set_timer(HERO_FIRE_EVENT, 200)

    def update(self, *args):
        """
        更新英雄飞机的图像及矩形区域
        :param args: 0 更新图像标记, 1 水平移动基数, 2 垂直移动基数
        :return:
        """
        # 调用父类方法更新飞机图像 - 注意 args 需要拆包
        super().update(*args)
        # 如果没有传递方向基数或者英雄飞机被催毁, 直接返回
        if len(args) != 3 or self.hp <= 0:
            return
        # 调整水平移动距离
        self.rect.x += args[1] * self.speed
        self.rect.y += args[2] * self.speed
        # 限定在游戏窗口内部移动
        self.rect.x = 0 if self.rect.x < 0 else self.rect.x
        if self.rect.right > SCREEN_RECT.right:
            self.rect.right = SCREEN_RECT.right
            self.rect.y = 0 if self.rect.y < 0 else self.rect.y
        if self.rect.bottom > SCREEN_RECT.bottom:
            self.rect.bottom = SCREEN_RECT.bottom

    def blowup(self, enemies_group):
        # 如果没有足够数量的炸弹或者英雄飞机被催毁, 直接返回
        if self.bomb_count <= 0 or self.hp <= 0:
            return 0
        self.bomb_count -= 1  # 炸弹数-1
        score = 0  # 本次得分
        count = 0  # 炸毁数量
        # 遍历敌机精灵组, 将游戏窗口内的敌机引爆
        for enemy in enemies_group.sprites():
            # 判断敌机是否进入游戏窗口
            if enemy.rect.bottom > 0:
                score += enemy.value  # 计算得分
                count += 1  # 累计数量
                enemy.hp = 0  # 摧毁敌机
        print("炸毁了%d架敌机， 得分 %d" % (count, score))
        return score

    def reset_plane(self):
        """重置英雄飞机"""
        # 调用父类方法重置图像相关属性
        super().reset_plane()
        self.is_power = True  # 无敌判断标记
        self.bomb_count = HERO_BOMB_COUNT  # 炸弹数量
        self.bullets_kind = 0  # 子弹类型
        # 发布英雄牺牲事件
        pygame.event.post(pygame.event.Event(HERO_DEAD_EVENT))
        # 设置3s之后取消无敌定时器事件
        pygame.time.set_timer(HERO_POWER_OFF_EVENT, 3000)

    def fire(self, display_group):
        """
        发射子弹
        :param display_group: 要添加的显示精灵组
        :return:
        """
        # 需要将子弹添加到2个精灵组
        groups = (self.bullets_group, display_group)
        # 测试子弹增强效果
        # self.bullets_kind = 1
        for i in range(3):
            # 创建子弹精灵
            bullet1 = Bullet(self.bullets_kind, *groups)
            # 计算子弹的垂直位置
            y = self.rect.y - i * 15
            # 判断子弹类型
            if self.bullets_kind == 0:
                bullet1.rect.midbottom = (self.rect.centerx, y)
            else:
                bullet1.rect.midbottom = (self.rect.centerx - 20, y)
                # 在创建一颗子弹
                bullet2 = Bullet(self.bullets_kind, *groups)
                bullet2.rect.midbottom = (self.rect.centerx + 20, y)


class Bullet(GameSprite):
    """子弹类"""

    def __init__(self, kind, *groups):
        """
        构造方法
        :param kind: 子弹类型
        :param groups: 要添加到的精灵组
        """
        image_name = "bullet1.png" if kind == 0 else "bullet2.png"
        super().__init__(image_name, -12, *groups)
        self.damage = 1

    def update(self, *args):
        super().update(*args)  # 向上移动
        # 判断是否从上方飞出窗口
        if self.rect.bottom < 0:
            self.kill()


class Supply(GameSprite):
    """道具类"""

    def __init__(self, kind, *groups):
        # 调用父类方法
        image_name = "%s_supply.png" % ("bomb" if kind == 0 else "bullet")
        super().__init__(image_name, 5, *groups)
        # 道具类型
        self.kind = kind
        # 音频文件名
        self.wav_name = "get_%s.wav" % ("bomb" if kind == 0 else "bullet")
        # 初始位置
        self.rect.y = SCREEN_RECT.h

    def throw_supply(self):
        """投放道具"""
        self.rect.bottom = 0
        self.rect.x = random.randint(0, SCREEN_RECT.w - self.rect.w)

    def update(self, *args):
        """更新位置, 在屏幕下方不移动"""
        if self.rect.h > SCREEN_RECT.h:
            return
        # 调用父类方法, 沿垂直方移动
        super().update(*args)
