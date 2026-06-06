import sys
import os
import json
from PyQt5.QtWidgets import (QFileDialog,QMessageBox)
from PyQt5.QtWidgets import (QWidget,QMessageBox,QFileDialog)
from PyQt5 import QtWidgets

def load_another(self):
    while True:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "选择JSON文件（仅单个）",
            "",  # 默认打开的路径，可根据需要修改，比如"./"表示当前目录
            "JSON文件 (*.json)"  # 仅显示JSON格式文件
        )
                
        if path:
            print(path)
            if "model3.json" in path:
                content = {
                           "head_x": "ParamAngleX", 
                           "head_y": "ParamAngleY", 
                           "head_z": "ParamAngleZ",
                           "eye_x": "ParamEyeBallX", 
                           "eye_y": "ParamEyeBallY",
                           "body_x": "ParamBodyAngleX",
                           "body_z": "ParamBodyAngleZ",
                           "mouth": "ParamMouthOpenY",
                           "Voice": 0,
                           "Prompt": '''ユーザーの友達として、可愛い口調で、指定された言語を使って答えてね。'''}
                self.content = content
                self.path = path

                #再写入history.json
                if getattr(sys, 'frozen', False):
                    current_dir = os.path.dirname(sys.executable)
                else:
                    main_entry_path = os.path.abspath(sys.argv[0])
                    current_dir = os.path.dirname(main_entry_path)
                #print(current_dir)
                json_file = os.path.join(current_dir,'history.json')
                
                try:
                    if os.path.exists(json_file):
                        with open(json_file, 'r', encoding='utf-8') as file:
                            self.history = json.load(file)
                
                    else: 
                        self.history = {path:content}
                except (json.JSONDecodeError, ValueError, Exception) as e:
                    QMessageBox.warning(self, "Error", f"Check db_dir.json: {e}", QMessageBox.Ok)

                self.history[path] = content
                print(self.history)

                # 3. 写入JSON（w模式：存在清空覆盖，不存在创建）

                    # w模式核心特性：清空+写入，encoding=utf-8避免中文乱码
                with open(json_file, 'w', encoding='utf-8') as f:
                        # indent=4格式化写入，ensure_ascii=False支持中文
                        json.dump(self.history, f, indent=4, ensure_ascii=False)
                        self.close()
                        return


                break
            else:
                QMessageBox.warning(self, "文件格式错误", "请选择一个有效的model3.json文件！", QMessageBox.Ok)

        else:
            return

def get_history(self):
    if getattr(sys, 'frozen', False):
        current_dir = os.path.dirname(sys.executable)
    else:
        main_entry_path = os.path.abspath(sys.argv[0])
        current_dir = os.path.dirname(main_entry_path)
    #print(current_dir)
    json_file = os.path.join(current_dir,'history.json')
    
    try:
        if os.path.exists(json_file):
            with open(json_file, 'r', encoding='utf-8') as file:
                self.history = json.load(file)
                #print(self.history.keys())
                for path in list(self.history.keys()):
                    add(self, path, json_file)
                return 
        else: 
            return
    except (json.JSONDecodeError, ValueError, Exception) as e:
        print(e)
        return
    
def load_last_time(self,path):
    self.content = self.history[path]
    self.path = path
    self.close()

def delete(self, layout, json_file):
    key = layout.itemAt(0).widget().text()
    self.history.pop(key)
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(self.history, f, indent=4, ensure_ascii=False)
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget:
            widget.deleteLater()
    # 移除布局本身
    self.ui.verticalLayout_2.removeItem(layout)
    layout.deleteLater()

def add(self, path, json_file):
    self.layout_count += 1
    new_h_layout = QtWidgets.QHBoxLayout()

    # 给水平布局添加示例控件（可根据需求修改）
    # 1. line edit
    line_edit = QtWidgets.QLineEdit()
    new_h_layout.addWidget(line_edit)
    line_edit.setText(path)
    line_edit.setEnabled(False)

    # 2. load button
    load_btn = QtWidgets.QPushButton("Load")
    print(2222222222222)
    load_btn.clicked.connect(lambda: load_last_time(self, path))
    new_h_layout.addWidget(load_btn)

    # 3. delete button
    delete_btn = QtWidgets.QPushButton("Delete")
    print(33333333333333333333)
    delete_btn.clicked.connect(lambda: delete(self, new_h_layout, json_file))
    new_h_layout.addWidget(delete_btn)

    # 设置水平布局内控件的对齐方式（可选）
    #new_h_layout.setAlignment(Qt.AlignLeft)
    # 设置控件之间的间距（可选）
    new_h_layout.setSpacing(6)
    new_h_layout.setStretch(0,7)
    new_h_layout.setStretch(1,1)
    new_h_layout.setStretch(2,1)

    # 将新的水平布局添加到主垂直布局中
    # 插入到按钮上方（如果想加在按钮下方，直接用addLayout即可）
    self.ui.verticalLayout_2.insertLayout(self.ui.verticalLayout_2.count() + 1, new_h_layout)


    #return combo_box, spin, slider, new_h_layout


