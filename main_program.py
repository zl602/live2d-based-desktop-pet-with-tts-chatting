import sys
import os
from PyQt5.QtWidgets import (QApplication,QMainWindow, QWidget)
from GUI.mainwindow import Ui_MainWindow as MainWindowUi
from GUI.loader import Ui_Form as LoaderUI
from functions.controller_functions import (load_file, play, switch_track, reverse_x, reverse_y, reverse_body, 
                                            reset, set_response, open_setting, interval_changed, auto_changed, volume_changed
                                            ,get_param_list)
from functions.loader_functions import get_history, load_another
from functions.conversation_functions import init_conversation
from functions.advanced_functions import init_advanced, load_advanced, save_advanced
import os
import sys
import ctypes

# 适配 OneFile 模式的 OpenGL DLL 路径
def fix_opengl_dll_path():
    if hasattr(sys, '_MEIPASS'):
        # OneFile 模式：临时解压目录
        opengl_dll_path = os.path.join(sys._MEIPASS, "OpenGL", "DLLS")
        # 将 OpenGL DLL 路径加入系统库搜索路径
        os.add_dll_directory(opengl_dll_path)
        # 手动加载核心 OpenGL DLL（以实际存在的 DLL 名为准）
        try:
            ctypes.CDLL(os.path.join(opengl_dll_path, "freeglut64.vc9.dll"))
            ctypes.CDLL(os.path.join(opengl_dll_path, "gle64.vc9.dll"))
        except Exception as e:
            print(f"加载 OpenGL DLL 提示：{e}")  # 仅提示，不影响核心逻辑

# 程序启动时立即执行修复
fix_opengl_dll_path()

# 原有路径适配函数（保留）
def get_real_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

class Loader(QWidget):
    
    def __init__(self):
        super().__init__()
        self.ui = LoaderUI()
        self.ui.setupUi(self)
        self.layout_count = 0
        self.history = None
        self.path = None
        self.content = None
        get_history(self)
        print(self.path, self.content)

        """绑定事件"""
        self.ui.load_new.clicked.connect(lambda:load_another(self))

class MainWindow(QMainWindow):
    
    def __init__(self,content,path,history):
        super().__init__()
        self.ui = MainWindowUi()
        self.ui.setupUi(self)
        self.history = history
        self.path = path
        self.content = content
        self.head_x,self.head_y,self.head_z, self.eye_x,self.eye_y,self.body_x,self.body_z, self.mouth = content["head_x"],content["head_y"],content["head_z"], content["eye_x"],content["eye_y"],content["body_x"],content["body_z"], content["mouth"]
        
        self.ui.response_x.setValue(0.5)
        self.ui.response_y.setValue(0.5)
        self.ui.response_body.setValue(0.3)
        self.ui.response_mouth.setValue(1)
        self.ui.time_interval.setValue(0.5)
        self.ui.volume.setValue(100)
        self.live2d_widget = None
        global volume
        volume = 1
        load_file(self)
        init_advanced(self)
        self.param_dict = get_param_list(self)
        self.volume = 1
        self.conversation_init = 0
        load_advanced(self)

        self.prompt = self.content["Prompt"]

        """绑定事件"""

        self.ui.motions.currentTextChanged.connect(lambda: play(self))
        self.ui.Reverse_X.clicked.connect(lambda: reverse_x(self))
        self.ui.Reverse_Y.clicked.connect(lambda: reverse_y(self))
        self.ui.reverse_body.clicked.connect(lambda: reverse_body(self))
        self.ui.response_x.valueChanged.connect(lambda: set_response(self))
        self.ui.response_y.valueChanged.connect(lambda: set_response(self))
        self.ui.response_body.valueChanged.connect(lambda: set_response(self))
        self.ui.response_mouth.valueChanged.connect(lambda: set_response(self))
        self.ui.set_param.clicked.connect(lambda: open_setting(self, self.content, self.history, self.prompt))
        self.ui.time_interval.valueChanged.connect(lambda: interval_changed(self))
        self.ui.auto_motion.toggled.connect(lambda: auto_changed(self))
        self.ui.volume.valueChanged.connect(lambda: volume_changed(self))
        self.ui.tabWidget.tabBar().tabBarClicked.connect(self.load_tab_bar)



    def load_tab_bar(self, tab_index):
        if tab_index == 1:
            init_conversation(self)

    def closeEvent(self, a0):
        save_advanced(self)
        print(1)
        self.live2d_widget.close()
        return super().closeEvent(a0)
    

        

        
    

    



global app
app = QApplication(sys.argv)
        
def run():
    #app = QApplication(sys.argv)
    loader = Loader()
    loader.show()
    app.exec_()
    if loader.content:
            main_window = MainWindow(loader.content, loader.path, loader.history)
            main_window.show()
            sys.exit(app.exec_())
    else:
            sys.exit(0)
    

    sys.exit(app.exec_())


run()