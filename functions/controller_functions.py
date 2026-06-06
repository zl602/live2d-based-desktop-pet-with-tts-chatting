import sys
import os
import json
from PyQt5.QtWidgets import (QWidget,QMessageBox,QFileDialog)
from .live2d_widget_functions import (Live2DWidget)
from GUI.setting_ui import Ui_Form


def load_file(self):
    try:
        
        # 1. 去除首尾的单/双引号（兼容各种引号情况）
        cleaned_path = self.path.strip('"\'')
        
        # 2. 按反斜杠\分割路径（过滤空字符串，处理连续反斜杠）
        path_parts = [part for part in cleaned_path.split('\\') if part]
        
        # 3. 直接用正斜杠/拼接所有路径片段（核心修改）
        # 最终得到 D:/live2d_test/haru_greeter_pro_jp/haru_greeter_pro_jp
        final_path = "/".join(path_parts)
        
        # 可选：如果需要保证路径开头的盘符（如D:）后也有/，补充处理（针对Windows盘符）
        # 比如把 D:xxx 改成 D:/xxx
        if len(final_path) >= 2 and final_path[1] == ':':
            final_path = final_path[0:2] + '/' + final_path[2:]
        
        global live2d_widget
        live2d_widget = Live2DWidget(model_path = final_path)
        self.live2d_widget = live2d_widget
        self.live2d_widget.head_x = self.head_x
        self.live2d_widget.head_y = self.head_y
        self.live2d_widget.head_z = self.head_z
        self.live2d_widget.eye_x = self.eye_x
        self.live2d_widget.eye_y = self.eye_y
        self.live2d_widget.body_x = self.body_x
        self.live2d_widget.body_z = self.body_z
        self.live2d_widget.mouth = self.mouth
        print(1)
        self.live2d_widget.show()
        print(2)
        self.ui.track.setEnabled(True)
        self.ui.Reverse_X.setEnabled(True)
        self.ui.Reverse_Y.setEnabled(True)

    except Exception as e:
        print(f"发生错误: {str(e)}")

    #加载动作combo选项
    with open(self.path, 'r', encoding='utf-8') as f:
        try:
            json_data = json.load(f)
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "JSON解析错误", 
                                f"模板文件格式错误：{str(e)}")
            return
    try:
        motion_content = json_data["FileReferences"]["Motions"]
        print("----------------------------",motion_content)
        combo_dict = {}
        for key1 in motion_content.keys():
            for i in range(len(motion_content[key1])):
                name = motion_content[key1][i]["File"]
                name_parts = [part for part in name.split('/') if part]
                final_name = name_parts[::-1][0][:-13]
                temp_list = [key1, i]
                if "Sound" in motion_content[key1][i].keys():
                    temp_list.append(motion_content[key1][i]["Sound"])
                combo_dict[final_name] = temp_list
        self.combo_dict = combo_dict
        
        combo_list = list(combo_dict.keys())
        combo_list.insert(0,"")
        live2d_widget.combo_dict = combo_dict
        self.ui.motions.addItems(combo_list)
        self.ui.motions.setEnabled(True)
        self.ui.auto_motion.setEnabled(True)
    except Exception as e:
        print(e)
        self.ui.motions.setEnabled(False)
        return
  



def play(self):
    selected_motion = self.ui.motions.currentText()
    live2d_widget.play(selected_motion)

    

def switch_track(self):
    self.live2d_widget.mouse_track = not self.live2d_widget.mouse_track
    if self.ui.track.text() == "Track":
        self.ui.track.setText("Tracking...")
    elif self.ui.track.text() == "Tracking...":
        self.ui.track.setText("Track")
        self.ui.Reset.setEnabled(True)

def reverse_x(self):
    if self.live2d_widget.r_x == 1:
        self.live2d_widget.r_x = -1
    else: self.live2d_widget.r_x = 1
def reverse_y(self):
    if self.live2d_widget.r_y == 1:
        self.live2d_widget.r_y = -1
    else: self.live2d_widget.r_y = 1
def reverse_body(self):
    if self.live2d_widget.r_b == 1:
        self.live2d_widget.r_b = -1
    else: self.live2d_widget.r_b = 1
def reset(self):
    self.live2d_widget.reset = not self.live2d_widget.reset

def set_response(self):
    self.live2d_widget.response_x = self.ui.response_x.value()
    self.live2d_widget.response_y = self.ui.response_y.value()
    self.live2d_widget.response_body = self.ui.response_body.value()
    self.live2d_widget.response_mouth = self.ui.response_mouth.value()

def get_param_list(self):
    param_dict = {"":""}
    try:
        new_path = self.path[:-11] + "cdi3.json"
        print("get path")

     
    except Exception as e:
        new_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择JSON文件（仅单个）",
            "",  # 默认打开的路径，可根据需要修改，比如"./"表示当前目录
            "JSON文件 (*.json)"  # 仅显示JSON格式文件
        )

    try:
        with open(new_path, 'r', encoding='utf-8') as file:
            a = json.load(file)
            for i in a["Parameters"]:
                param_dict[i["Name"]] = i["Id"]
    except (json.JSONDecodeError, ValueError, Exception) as e:
        try:
                new_path, _ = QFileDialog.getOpenFileName(
                    self,
                    "选择JSON文件（仅单个）",
                    "",  # 默认打开的路径，可根据需要修改，比如"./"表示当前目录
                    "JSON文件 (*.json)"  # 仅显示JSON格式文件
                )
                with open(new_path, 'r', encoding='utf-8') as file:
                    a = json.load(file)
                for i in a["Parameters"]:
                    param_dict[i["Name"]] = i["Id"]
        except (json.JSONDecodeError, ValueError, Exception) as e:
            print(e)
    
    return param_dict


def open_setting(self, content, history, prompt):
    class Setting(QWidget):
        def __init__(self, path, parent = None):
            super().__init__(parent)
            self.ui = Ui_Form()  # 实例化自动生成的UI类
            self.ui.setupUi(self)
            self.path = path
            self.param_dict = get_param_list(self)
            self.content = content
            self.history = history
            
                

            self.ui.head_x.addItems(self.param_dict.keys())
            self.ui.head_y.addItems(self.param_dict.keys())
            self.ui.head_z.addItems(self.param_dict.keys())
            self.ui.eye_x.addItems(self.param_dict.keys())
            self.ui.eye_y.addItems(self.param_dict.keys())
            self.ui.body_x.addItems(self.param_dict.keys())
            self.ui.body_z.addItems(self.param_dict.keys())
            self.ui.mouth.addItems(self.param_dict.keys())
            self.ui.prompt.setText(prompt)
            self.ui.ok.clicked.connect(self.ok)
            self.ui.cancel.clicked.connect(self.cancel) 

        def ok(self):
            if self.ui.head_x.currentText() != "":
                self.content["head_x"] = self.param_dict[self.ui.head_x.currentText()]
                live2d_widget.head_x = self.param_dict[self.ui.head_x.currentText()]
            if self.ui.head_y.currentText() != "":
                self.content["head_y"] = self.param_dict[self.ui.head_y.currentText()]
                live2d_widget.head_y = self.param_dict[self.ui.head_y.currentText()]
            if self.ui.head_z.currentText() != "":
                self.content["head_z"] = self.param_dict[self.ui.head_z.currentText()]
                live2d_widget.head_y = self.param_dict[self.ui.head_y.currentText()]
            if self.ui.eye_x.currentText() != "":
                self.content["eye_x"] = self.param_dict[self.ui.eye_x.currentText()]
                live2d_widget.eye_x = self.param_dict[self.ui.eye_x.currentText()]
            if self.ui.eye_y.currentText() != "":
                self.content["eye_y"] = self.param_dict[self.ui.eye_y.currentText()]
                live2d_widget.eye_y= self.param_dict[self.ui.eye_y.currentText()]
            if self.ui.body_x.currentText() != "":
                self.content["body_x"] = self.param_dict[self.ui.body_x.currentText()]
                live2d_widget.body_x = self.param_dict[self.ui.body_x.currentText()]
            if self.ui.body_z.currentText() != "":
                self.content["body_z"] = self.param_dict[self.ui.body_z.currentText()]
                live2d_widget.body_z = self.param_dict[self.ui.body_z.currentText()]
            if self.ui.mouth.currentText() != "":
                self.content["mouth"] = self.param_dict[self.ui.mouth.currentText()]
                live2d_widget.mouth = self.param_dict[self.ui.mouth.currentText()]
            self.content["Prompt"] = self.ui.prompt.toPlainText()
            self.history[self.path] = self.content
            #self.content["Prompt"] = self.ui.prompt.toPlainText()
            if getattr(sys, 'frozen', False):
                current_dir = os.path.dirname(sys.executable)
            else:
                main_entry_path = os.path.abspath(sys.argv[0])
                current_dir = os.path.dirname(main_entry_path)
            #print(current_dir)
            json_file_path = os.path.join(current_dir,'history.json')

            # 3. 写入JSON（w模式：存在清空覆盖，不存在创建）
            try:
                # w模式核心特性：清空+写入，encoding=utf-8避免中文乱码
                with open(json_file_path, 'w', encoding='utf-8') as f:
                    # indent=4格式化写入，ensure_ascii=False支持中文
                    json.dump(self.history, f, indent=4, ensure_ascii=False)
                    self.close()
                    return
            except Exception as e:
                print(e)   
                self.close()

        def cancel(self):
            self.close()
    global setting_widget
    setting_widget = Setting(self.path)
    setting_widget.show()

def interval_changed(self):
    if self.ui.time_interval.value() == 0:
        return
    self.live2d_widget.interval = self.ui.time_interval.value()
    #立即播放一次
    self.live2d_widget.rand_play()
    #重新设置播放计时器
    self.live2d_widget.timer_auto.start(int(self.live2d_widget.interval * 60*1000))  

def auto_changed(self):
    self.live2d_widget.auto = self.ui.auto_motion.isChecked()

def volume_changed(self):
    try:
        volume = self.ui.volume.value()/100
        self.live2d_widget.volume = volume
        self.volume = volume
        self.live2d_widget.set_volume()
    except Exception as e:
        return e






    
    








