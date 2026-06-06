import sys
import os
import json
from PyQt5.QtWidgets import ( QOpenGLWidget, QMenu, QAction
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QSurfaceFormat, QCursor, QOpenGLVersionProfile
# 导入Live2D模型类
import live2d.v3 as live2d
from live2d.utils.lipsync import WavHandler
import time  
import random
import pygame


# 完整的Live2DWidget类（实现透明背景）
class Live2DWidget(QOpenGLWidget):
    def __init__(self, model_path, parent=None):
        super().__init__(parent)
        self.model_path = model_path
        self.model = None
        self.last_time = time.time()
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setFixedSize(300,400)
        self.mouse_track = False
        #self.mouse_buffer = False
        self.r_x = 1
        self.r_y = -1
        self.r_b = 1
        self.reset = False
        self.response_x = 0.5
        self.response_y = 0.5
        self.response_body = 0.3
        self.response_mouth = 1
        self.head_x = None
        self.head_y = None
        self.head_z = None
        self.eye_x = None
        self.eye_y = None
        self.body_x = None
        self.body_z = None
        self.mouth = None
        #自动播放设定
        self.interval = 0.5
        self.auto = False
        self.combo_dict = None
        self.volume = 1

        self.wavHandler = WavHandler()
        self.exp_files = self.get_expressions()
        self.previous_index = None
        

        
        



        # ========== 1. 关键：设置OpenGLWidget透明属性 ==========
        # 设置窗口属性支持透明
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)  # 开启透明背景
        self.setAutoFillBackground(False)  # 禁用自动填充背景
        
        # 配置OpenGL格式（必须，支持Alpha通道）
        fmt = QSurfaceFormat()
        fmt.setAlphaBufferSize(8)  # 启用Alpha通道（透明必备）
        fmt.setDepthBufferSize(24)
        fmt.setStencilBufferSize(8)
        self.setFormat(fmt)
        
        # 60帧/秒刷新
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(16)  # 约60fps（1000/60≈16）

        #一分钟随机动作
        self.timer_auto = QTimer(self)
        self.timer_auto.timeout.connect(self.auto_motion)
        self.timer_auto.start(int(self.interval * 60*1000))
        print(self.combo_dict)

    def initializeGL(self):
        """初始化OpenGL和Live2D模型"""
        # 初始化GLUT
        version_profile = QOpenGLVersionProfile()
        version_profile.setVersion(2,0)
        self.gl = self.context().versionFunctions(version_profile)
        self.gl.initializeOpenGLFunctions()
        
        
        # ========== 2. 关键：配置OpenGL混合模式（支持透明） ==========
        #self.gl.glEnable(self.gl.GL_BLEND)  # 启用混合（透明必备）
        # 设置混合模式：源Alpha * 源颜色 + (1-源Alpha) * 目标颜色
        self.gl.glBlendFunc(self.gl.GL_SRC_ALPHA, self.gl.GL_ONE_MINUS_SRC_ALPHA)
        self.gl.glClearColor(0,0,0,0)  # 清空颜色设为全透明（0.0）（关键）
        
        # 初始化Live2D
        live2d.init()
        live2d.glInit()
        
        try:
            model = live2d.LAppModel()
            model.LoadModelJson(self.model_path)
            self.model = model
            self.model.SetAutoBlinkEnable(True)
            print(f"✅ 模型加载成功：{self.model_path}")
        except Exception as e:
            print(f"❌ 模型加载失败：{e}")
            print("\n【排查提示】")
            print("1. 确认模型路径是.model3.json文件，不是文件夹")
            print("2. 模型文件夹内必须包含.moc3、纹理图片等文件")
            print("3. 路径中不要有中文/特殊字符")
        
    def paintGL(self):
        """每一帧绘制模型（透明背景版）"""
        # ========== 3. 关键：清空缓冲区但保留透明 ==========
        # GL_COLOR_BUFFER_BIT：清空颜色缓冲区
        # GL_DEPTH_BUFFER_BIT：清空深度缓冲区
        #self.gl.glClear(self.gl.GL_COLOR_BUFFER_BIT | self.gl.GL_DEPTH_BUFFER_BIT)
        try:
            if not self.model:
                return
            # 计算时间差，驱动模型动画
            current_time = time.time()
            delta_time = current_time - self.last_time
            self.last_time = current_time
            self.model.SetAutoBlinkEnable(True)
            
            if self.reset == True:#判断是否重置位置
                live2d.clearBuffer()
                for i in range(self.model.GetParameterCount()):
                    param = self.model.GetParameter(i)
                    self.model.SetParameterValue(param.id, param.default, 1.0)
                self.reset = False
                
                   

            elif self.mouse_track: #判断是否启用鼠标追踪
                window_rect = self.frameGeometry()
                # 2. 计算矩形中心点（直接返回绝对坐标QPoint）
                center_point = window_rect.center()
                height = window_rect.height()
                mouse_global_pos = QCursor.pos()
            
                # 2. 计算鼠标偏离屏幕中心的距离（归一化到-1~1）
                # X轴：屏幕左→右 = -1→1
                offset_x =  self.response_x * (mouse_global_pos.x() - center_point.x()) / (window_rect.width())
                offset_body = self.response_body * (mouse_global_pos.x() - center_point.x()) / (window_rect.width())
                # Y轴：屏幕下→上 = -1→1（反向，让鼠标上移时模型头部上抬），锚定点在窗口高度1/6处以适配主流六头身角色
                offset_y =  self.response_y * (mouse_global_pos.y() - (center_point.y() - window_rect.height()/3)) / (window_rect.height())
                # 3. 限制偏移范围（避免鼠标到屏幕边缘时转头过度）
                offset_x = max(min(offset_x, 1.0), -1.0)
                offset_body = max(min(offset_body, 1.0), -1.0)
                offset_y = max(min(offset_y, 1.0), -1.0)
                #还原模型
                live2d.clearBuffer()
                self.model.Update()
                # 4. 映射到模型角度范围
                self.model.SetParameterValue(self.head_x, self.r_x * offset_x * 30,1)
                self.model.SetParameterValue(self.head_y, self.r_y * offset_y * 30,1)
                self.model.SetParameterValue(self.eye_x, self.r_x * offset_x,1) 
                self.model.SetParameterValue(self.eye_y, self.r_y * offset_y ,1)
                self.model.SetParameterValue(self.body_x, self.r_b * offset_body * 10,1)
                print(self.head_y, self.r_y * offset_y * 30)
                
            else:
                live2d.clearBuffer()
                self.model.Update()
                
            if self.wavHandler.Update():  # 获取 wav 下一帧片段的响度（Rms），并返回当前音频是否已结束
                self.model.SetParameterValue(self.mouth, self.wavHandler.GetRms() * self.response_mouth)
            self.model.Draw()  
        except Exception as e:
            print(e)


    def resizeGL(self, width, height):
        """窗口大小变化时调整视角（保证模型比例）"""
        self.gl.glViewport(0, 0, width, height)
        if self.model:
            self.model.Resize(width, height)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            try:
                self.rand_play()
            except Exception as e:
                print(f"rand_play error: {e}")
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and hasattr(self, 'drag_pos'):
            self.move(event.globalPos() - self.drag_pos)
            event.accept()
    

    def auto_motion(self):
        if self.auto == True:
            self.rand_play()

    def on_motion_start(self):
        self.mouse_buffer = self.mouse_track
        self.mouse_track = False
    def on_motion_end(self):
        self.mouse_track = self.mouse_buffer  

    def motion(self,selected_motion):
        selected_motion 
        if selected_motion != "":
            
            self.model.StartMotion(
                self.combo_dict[selected_motion][0], 
                self.combo_dict[selected_motion][1],
                1,None,None)
            print(self.combo_dict)


    def audio(self, selected_motion):

        
        try:
            path_parts = [part for part in self.model_path.split('/') if part]
            new_path = "/".join(path_parts[:-1])
            audio_path = new_path + "/" + self.combo_dict[selected_motion][2]
            pygame.mixer.init()
            global sound
            sound = pygame.mixer.Sound(audio_path)
            pygame.mixer.Sound.set_volume(sound, self.volume)
            sound.play()
            print("played")
        except Exception as e:
            print("audio error", e)


    def set_volume(self):
        pygame.mixer.Sound.set_volume(sound, self.volume)  


    def play(self,selected_motion):
        self.audio( selected_motion)
        self.motion(selected_motion)



    def rand_play(self): 
        i = random.randint(1, len(self.combo_dict)-1)
        l = list(self.combo_dict.keys())
        selected_motion = l[i]
        self.audio(selected_motion)
        self.motion(selected_motion)

    def wheelEvent(self, event):
        """滚轮事件：同步缩放窗口和Live2D模型"""
        # 1. 获取当前窗口大小
        current_size = self.size()
        
        # 2. 根据滚轮方向计算新尺寸（每次缩放10像素）
        delta = event.angleDelta().y()
        if delta > 0:
            # 向上滚动，放大窗口
            new_width, new_height = int(current_size.width()*1.05), int(current_size.height()*1.05)
        else:
            # 向下滚动，缩小窗口
            new_width, new_height = int(current_size.width()*0.95), int(current_size.height()*0.95)
        
        # 3. 限制最小尺寸（避免缩放到消失）
        min_width, min_height = 50, 100  # 最小尺寸阈值
        width = max(new_width, min_width)
        height = max(new_height, min_height)
        
        
        # 4. 设置新窗口大小
        self.setFixedSize(width, height)
        
        # 5. 关键：同步缩放Live2D模型（核心适配点）
        if self.model:
            self.model.Resize(width, height)
        event.accept()

   

    def initUI(self):
        self.setWindowTitle('PyQt5 右键菜单示例')
        self.resize(400, 300)

    # 重写右键菜单事件
    def contextMenuEvent(self, event):
        # 创建右键菜单
        context_menu = QMenu(self)
        # 添加菜单项
        action1 = QAction('Track', self)
        action2 = QAction('Reset', self)
        # 为菜单项绑定点击事件
        action1.triggered.connect(self.track)
        action2.triggered.connect(self.reset_on)     
        # 添加分隔线
        context_menu.addSeparator()   
        # 将菜单项添加到菜单
        context_menu.addAction(action1)
        context_menu.addAction(action2)
        
        exp_list = list(self.exp_files.keys())
        for i in range(len(self.exp_files)):
            self.add_action(i, exp_list, context_menu)


        # 在鼠标右键点击的位置显示菜单
        context_menu.exec_(event.globalPos())

    def add_action(self, index, exp_list, context_menu): 
        action = QAction(exp_list[index],self)
        action.triggered.connect(lambda checked, idx=index: self.play_expression(idx))
        context_menu.addAction(action)


    # 菜单项1点击事件
    def track(self):
        self.mouse_track = not self.mouse_track
    # 菜单项2点击事件
    def reset_on(self):
        self.reset = True
    
    def get_expressions(self):
        #print(11111111111111111111111111111111111111111111111)
        try:
            cleaned_path = self.model_path.strip('"\'')
            os.path.split(cleaned_path)
            start_dir = os.path.dirname(cleaned_path)
            print(start_dir)
        except Exception as e:
            print(e)
        
        exp_files = {}
        
        # 递归遍历目录树
        for root, dirs, files in os.walk(start_dir):
            for filename in files:
                # 检查是否为.exp文件（忽略大小写，比如.EXP也能匹配）
                if filename.lower().endswith('.exp3.json'):
                    full_path = os.path.join(root, filename)
                    exp_name = filename[:-10]
                    exp_files[exp_name] = full_path
                    print(exp_files)
                    self.exp_files = exp_files
        return exp_files
    
    def play_expression(self, exp_index):
        if self.previous_index: 
            exp = list(self.exp_files.keys())[self.previous_index]
            exp_file = self.exp_files[exp]
            with open(exp_file, 'r', encoding='utf-8') as f:
                try:
                    json_data = json.load(f)
                except json.JSONDecodeError as e:
                    print(e)
            param_ids = self.model.GetParamIds()
            for param in json_data["Parameters"]:
                param_index = param_ids.index(param["Id"])
                default_val = self.model.GetParameter(param_index).default
                self.model.SetParameterValue(param["Id"], default_val, 1.0)
        
        
        exp = list(self.exp_files.keys())[exp_index]

            
        exp_file = self.exp_files[exp]
        with open(exp_file, 'r', encoding='utf-8') as f:
            try:
                json_data = json.load(f)
            except json.JSONDecodeError as e:
                print(e)
        
        for param in json_data["Parameters"]:
            #if param["Blend"] == "Add":
                #self.model.AddParameterValue(param["Id"], param["Value"])
            #else: 
            self.model.SetParameterValue(param["Id"], param["Value"], 1.0)
        print(self.previous_index, exp_index)
        self.previous_index = exp_index
        print(self.model.GetParamIds())

    





    
    

                
            