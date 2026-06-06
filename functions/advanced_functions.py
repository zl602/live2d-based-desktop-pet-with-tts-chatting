import sys
import os
import json
from PyQt5 import QtCore, QtWidgets




def init_advanced(self,parent = None):
        self.layout_count = 0
        self.ui.add.clicked.connect(lambda: add(self))


def add(self):
    self.layout_count += 1
    new_h_layout = QtWidgets.QHBoxLayout()

    # 给水平布局添加示例控件（可根据需求修改）
    # 1. combobox
    combo_box = QtWidgets.QComboBox()
    new_h_layout.addWidget(combo_box)
    combo_box.addItems(self.param_dict.keys())
    combo_box.setObjectName(f"param_{self.layout_count}")

    # 2. spinbox
    spin = QtWidgets.QDoubleSpinBox()
    spin.setValue(1)
    spin.setObjectName(f"response_{self.layout_count}")
    new_h_layout.addWidget(spin)

    #3. slider
    slider = QtWidgets.QSlider()
    slider.setValue(50)
    slider.setOrientation(QtCore.Qt.Horizontal)
    slider.setObjectName(f"position_{self.layout_count}")
    new_h_layout.addWidget(slider)

    # 3. 示例按钮（可选，演示水平布局可包含多个控件）
    delete_btn = QtWidgets.QPushButton("Delete")
    delete_btn.clicked.connect(lambda: remove_layout(self, new_h_layout))
    delete_btn.setObjectName(f"delete_{self.layout_count}")
    new_h_layout.addWidget(delete_btn)

    # 设置水平布局内控件的对齐方式（可选）
    #new_h_layout.setAlignment(Qt.AlignLeft)
    # 设置控件之间的间距（可选）
    new_h_layout.setSpacing(6)
    new_h_layout.setStretch(0,2)
    new_h_layout.setStretch(1,1)
    new_h_layout.setStretch(2,3)
    new_h_layout.setStretch(3,1)

    # 将新的水平布局添加到主垂直布局中
    # 插入到按钮上方（如果想加在按钮下方，直接用addLayout即可）
    self.ui.main_vlayout.insertLayout(self.ui.main_vlayout.count() - 1, new_h_layout)

    delete_btn.clicked.connect(lambda: remove_layout(self, new_h_layout))
    slider.valueChanged.connect(lambda: on_slider_changed(self, new_h_layout))
    return combo_box, spin, slider, new_h_layout

def remove_layout(self, layout):
    """删除指定的水平布局（可选功能，方便演示）"""
    # 先移除布局内的所有控件
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget:
            widget.deleteLater()
    # 移除布局本身
    self.ui.main_vlayout.removeItem(layout)
    layout.deleteLater()

def on_slider_changed(self, layout):
    combo_item = layout.itemAt(0)
    combo_box = combo_item.widget() if combo_item else None
    # 提取数字输入框（索引1）
    spin_item = layout.itemAt(1)
    spin_box = spin_item.widget() if spin_item else None
    # 提取滑块（索引2）
    slider_item = layout.itemAt(2)
    slider = slider_item.widget() if slider_item else None

    # 步骤2：安全判断控件是否存在，避免报错
    if not (combo_box and spin_box and slider):
        print("无法获取布局内的控件！")
        return
    
    # 步骤3：调用控件的方法获取值
    param = self.param_dict[combo_box.currentText()]  # QComboBox获取选中文本用currentText()，不是text()
    response = spin_box.value()
    position = (slider.value() - 50)/10

    # 步骤4：调用live2d方法
    #try:
        #if self.live2d_widget and self.live2d_widget.model:
    self.live2d_widget.model.SetParameterValue(param, response * position ,1)
        #else:
            #print("live2d_widget或其model未初始化！")
    #except Exception as e:
            #print(f"调用live2d接口出错：{e}")

def load_advanced(self):
    try:
        size = self.content["Window Size"]
        self.live2d_widget.setFixedSize(size[0], size[1])
        self.live2d_widget.model.Resize(size[0], size[1])
    except Exception as e:
        print(e)
    try:
        self.ui.response_x.setValue(self.content["Responses"][0])
        self.ui.response_y.setValue(self.content["Responses"][1])
        self.ui.response_body.setValue(self.content["Responses"][2])
        self.ui.response_mouth.setValue(self.content["Responses"][3])
    except Exception as e:
            print(e)

   
    try:
        advanced = self.content["Advanced"]
        for i in range(len(advanced)):
            combo_box, spin, slider, layout = add(self)
            combo_box.setCurrentIndex(advanced[i]["combo_index"])
            spin.setValue(advanced[i]["spin_value"])
            slider.setValue(advanced[i]["slider_value"])
            on_slider_changed(self, layout)
    except Exception as e:
        print(e)
    




def save_advanced(self):
    responses = [
         self.ui.response_x.value(),
         self.ui.response_y.value(),
         self.ui.response_body.value(),
         self.ui.response_mouth.value()
    ]
    size = [
        self.live2d_widget.size().width(),
        self.live2d_widget.size().height()
    ]
    voice = self.ui.voice.currentIndex()
    # prompt = self.prompt
    # if prompt == "" or prompt == None:
    #     prompt = "ユーザーの友達として、可愛い口調で、指定された言語を使って答えてね。"
    advanced = []
    # 1. 遍历main_vlayout中的所有布局项
    layout_count = self.layout_count
    for i in range(layout_count):
        print(i)
        # 获取第i个布局项（可能是布局/控件/空白项）
        item = self.ui.main_vlayout.itemAt(i)
        
        # 2. 筛选出动态添加的QHBoxLayout（排除其他类型的项）
        if isinstance(item, QtWidgets.QLayoutItem) and isinstance(item.layout(), QtWidgets.QHBoxLayout):
            h_layout = item.layout()  # 获取水平布局
            
            # 3. 提取该水平布局内的控件（按顺序：下拉框、数值框、滑块、删除按钮）
            combo_box = None
            spin_box = None
            slider = None
            
            # 遍历水平布局内的控件
            for j in range(h_layout.count()):
                widget_item = h_layout.itemAt(j)
                if widget_item and widget_item.widget():
                    widget = widget_item.widget()
                    # 按控件类型识别（也可按objectName前缀识别）
                    if isinstance(widget, QtWidgets.QComboBox):
                        combo_box = widget
                    elif isinstance(widget, QtWidgets.QDoubleSpinBox):
                        spin_box = widget
                    elif isinstance(widget, QtWidgets.QSlider):
                        slider = widget
            
            # 4. 安全判断：确保控件都存在（避免动态删除后漏值）
            if combo_box and spin_box and slider and combo_box.currentText() != "":
                # 提取控件当前值
                control_data = {
                    "combo_index" : combo_box.currentIndex(),  # 下拉框选中的参数名
                    "spin_value" : spin_box.value(),  # 数值框的值
                    "slider_value" : slider.value(),  # 滑块原始值
                }
                # 将当前布局的控件值添加到advanced列表
                advanced.append(control_data)
            else:
                print(f"第{i}个水平布局控件不完整，跳过保存")
    
    self.content["Responses"] = responses
    self.content["Voice"] = voice
    self.content["Prompt"] = prompt
    self.content["Advanced"] = advanced
    self.content["Window Size"] = size   
    self.history[self.path] = self.content

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
            return
    except Exception as e:
        print(e)




        
    
