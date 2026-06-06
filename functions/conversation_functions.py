import sys
import os
import json
from PyQt5.QtWidgets import (QFileDialog,QInputDialog)
import datetime
import pygame
import requests
import wave
import threading
import time
import requests
import pyaudio


def get_API_key(self):
        try: 
            if getattr(sys, 'frozen', False):
                current_dir = os.path.dirname(sys.executable)
            else:
                main_entry_path = os.path.abspath(sys.argv[0])
                current_dir = os.path.dirname(main_entry_path)
            json_file = os.path.join(current_dir,'API_key.json')

            
            with open(json_file, 'r', encoding='utf-8') as file:
                    a = json.load(file)
                    API_key = a["API key"]
                    voicevox_add = a["VoiceVox Address"]
                    

            
        except Exception as e:
            API_key = QInputDialog.getText(
            self,                  # 父窗口（桌宠窗口）
            "API keyを設置してください",          # 对话框标题
            "API keyを設置してください",  # 提示文字
            # 可选参数：默认输入内容、输入框模式（比如密码模式）
            text="",               # 默认空输入
            #echo=QInputDialog.Normal  # 正常输入模式（可设为Password隐藏输入）
        )
            API_key = API_key[0]
            print(API_key)

            voicevox_add, _ = QFileDialog.getOpenFileName(
            self,
            "VOICEVOX.exeのパスを指定してください",
            "",  # 默认打开的路径，可根据需要修改，比如"./"表示当前目录
            "exe (*.exe)"  # 仅显示JSON格式文件
        )
                
        if voicevox_add:
            #print(path)
            if "VOICEVOX.exe" in voicevox_add:
                content = {"API key" : API_key, "VoiceVox Address": voicevox_add}
                try:
                    with open(json_file, 'w', encoding='utf-8') as file:
                        json.dump(content, file, indent=4, ensure_ascii=False)
                except (json.JSONDecodeError, ValueError, Exception) as e:               
                    print(e)

        self.ui.message.setEnabled(True)
        self.ui.send.setEnabled(True)
        return API_key, voicevox_add


class AIChatClient():
    def __init__(self, API_KEY,prompt):
        AI_MODEL = "deepseek-chat"
        AI_API_KEY = API_KEY
        print(AI_API_KEY)
        AI_API_BASE = "https://api.deepseek.com"
        from openai import OpenAI
        # 初始化 AI 客户端（兼容 DeepSeek/OpenAI）
        self.client = OpenAI(
            api_key=AI_API_KEY,
            base_url=AI_API_BASE
        )
        if not prompt:
            # 角色人设（可自定义，比如“可爱的二次元桌宠，语气软萌，回复简短”）
            self.system_prompt = {
                "role": "system",
                "content": '''ユーザーの友達として、可愛い口調で、指定された言語を使って答えてね。
                会話だけを生成して、括弧や動作描写は絶対に使わないで。
                後の質問は最初に<>で囲まれた内容があるから、質問がどんな言語でも、必ずその<>の中の言語で返信して。
                日本語で返す時は敬語（ます、です）を使わないで。
                ユーザーが長い内容を要求した時だけ（詳しい説明、小説、資料やウェブページの検索とか）、それ以外はできるだけ20トークン以内に収めてね。
            '''}
        else:
             self.system_prompt = {
                "role": "system",
                "content": f'''{prompt}。
                指定された言語を使って答えてね。
                会話だけを生成して、括弧や動作描写は絶対に使わないで。
                後の質問は最初に<>で囲まれた内容があるから、質問がどんな言語でも、必ずその<>の中の言語で返信して。
                日本語で返す時は敬語（ます、です）を使わないで。
                ユーザーが長い内容を要求した時だけ（詳しい説明、小説、資料やウェブページの検索とか）、それ以外はできるだけ20トークン以内に収めてね。
            '''}
        # 对话历史（保留上下文）
        self.chat_history = [self.system_prompt]

    def get_reply(self, user_input):
        """获取 AI 回复，带上下文记忆"""
        if not user_input.strip():
            return "你想说什么呀？😯"
        
        # 添加用户输入到历史
        self.chat_history.append({"role": "user", "content": user_input})
        
            # 调用 AI 接口
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=self.chat_history,
            temperature=0.8,  # 回复随机性
            max_tokens=500     # 限制回复长度
        )
        reply = response.choices[0].message.content.strip()
        # 添加 AI 回复到历史
        self.chat_history.append({"role": "assistant", "content": reply})
        # 限制历史长度（避免token超限）
        if len(self.chat_history) > 10:
            self.chat_history = [self.system_prompt] + self.chat_history[-8:]
        return reply


        
global voicevox_character_ids
voicevox_character_ids = {
    "九州そら": 10,
    "ずんだもん": 1,
    "四国めたん": 2,
    "春日部つむぎ": 3,
    "春歌ナナ": 23,
    "猫使アル": 24,
    "猫使ビィ": 25,
    "雨晴はう": 4,
    "波音リツ": 5,
    "玄野武宏": 6,
    "白上虎太郎": 7,
    "青山龍星": 8,
    "冥鳴ひまり": 9,
    "もち子さん": 11,
    "剣崎雌雄": 12,
    "WhiteCUL": 13,
    "後鬼": 14,
    "No7": 15,
    "ちび式じい": 16,
    "櫻歌ミコ": 17,
    "小夜/SAYO": 18,
    "ナースロボ＿タイプＴ": 19,
    "†聖騎士 紅桜†": 20,
    "雀松朱司": 21,
    "麒ヶ島宗麟": 22,
    "中国語読み上げ": 26}


import subprocess
import socket
import os
import sys
from PyQt5.QtWidgets import QMessageBox

def check_voicevox_running(port=50021):
    """检查VoiceVox服务是否已运行（通过端口判断）"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    # 端口能连接上=服务已运行，返回True；否则返回False
    return result == 0


import ctypes
from ctypes import wintypes


def minimize_voicevox():
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    HWND = wintypes.HWND
    LPCSTR = wintypes.LPCSTR
    UINT = wintypes.UINT

    user32.FindWindowA.restype = HWND
    user32.FindWindowA.argtypes = [LPCSTR, LPCSTR]

    user32.ShowWindow.restype = wintypes.BOOL
    user32.ShowWindow.argtypes = [HWND, UINT]
    """最小化VoiceVox窗口"""
    hwnd = b"VOICEVOX"
    if hwnd:
        user32.ShowWindow(hwnd, 6)
        print("VoiceVox已最小化到任务栏")
        return True
    else:
        print("未找到VoiceVox窗口，无法最小化")
        return False
    
def start_voicevox(voicevox_add):
    """自动启动VoiceVox服务（Windows专用）"""
    # ========== 请修改这里的VoiceVox路径 ==========
    voicevox_path = f"{voicevox_add}"
    # =============================================

    # 1. 先检查是否已运行
    if check_voicevox_running():
        print("VoiceVox服务已运行，无需重复启动")
        return True
    
    # 2. 检查VoiceVox路径是否存在
    if not os.path.exists(voicevox_path):
        # 弹出提示框告知用户路径错误
        QMessageBox.warning(
            None, 
            "提示", 
            f"未找到VoiceVox程序，请检查路径：\n{voicevox_path}\n\n请手动启动VoiceVox后再使用语音功能"
        )
        return False
    
    try:
        # 3. 启动VoiceVox（隐藏窗口，不显示控制台）
        # CREATE_NO_WINDOW：隐藏VoiceVox窗口；detach：不随桌宠关闭而关闭
        subprocess.Popen(
            [voicevox_path],
            creationflags=subprocess.CREATE_NO_WINDOW,
            stdout=subprocess.DEVNULL,  # 屏蔽输出
            stderr=subprocess.DEVNULL
        )
        print("VoiceVox启动中，请稍等3-5秒（服务加载需要时间）")
    except Exception as e:
        QMessageBox.critical(
            None, 
            "错误", 
            f"启动VoiceVox失败：{str(e)}\n请手动启动VoiceVox后使用语音功能"
        )
        return False

def init_conversation(self):
        if self.conversation_init == 0:

            self.ui.message.setPlaceholderText("ここでメッセージを入力して~")
            self.ui.message.setEnabled(False)
            self.ui.send.setEnabled(False)
            self.ui.history.setEnabled(True)
            self.ui.voice.addItems(voicevox_character_ids.keys())
            self.ui.voice.setCurrentIndex(self.content["Voice"]) #设置默认角色



            self.ui.send.clicked.connect(lambda: send_chat(self))
            self.ui.message.returnPressed.connect(lambda: send_chat(self))
            API_KEY, voicevox_add = get_API_key(self)
            start_voicevox(voicevox_add)
            self.ai_client = AIChatClient(API_KEY,self.prompt)
            self.VoiceVoxEngine = VoiceVoxEngine(host="127.0.0.1", port=50021)
            self.volume = 1
            self.conversation_init = 1
            return
        else:
            return


def send_chat(self):
    """发送聊天消息，获取 AI 回复并联动动画"""
    text = self.ui.message.text()
    if not text:
        return
    language = self.ui.language.currentText()
    user_input = f"<{language}>{text}"
    time = datetime.datetime.now()
    self.ui.message.setEnabled(False)
    self.ui.message.setText("少し待ってね~")
    self.ui.history.append(f"Userさん   --{time}\n{user_input}")
    
    # 异步调用 AI（避免界面卡顿）
    from PyQt5.QtCore import QThread, pyqtSignal
    class ChatThread(QThread):
        result_signal = pyqtSignal(str)
        def __init__(self, ai_client, user_input):
            super().__init__()
            self.ai_client = ai_client
            self.user_input = user_input
        def run(self):
            global result
            reply = self.ai_client.get_reply(self.user_input)
            s_stripped = reply.lstrip()
            # 定义括号匹配关系
            bracket_map = {'(': ')', '[': ']', '{': '}', "（": "）"}
            print(reply)
            try:
                end_bracket = bracket_map[s_stripped[0]]

                # 找到闭合括号的位置
                end_index = None
                for i, char in enumerate(s_stripped):
                    if char == end_bracket:
                        end_index = i
                        break

                # 如果找到闭合括号，截取之后的内容；否则返回原字符串
                if end_index is not None:
                    # 截取并去除开头空白，再拼接原字符串开头的空白（保持格式）
                    prefix_space = len(reply) - len(reply.lstrip())
                    result = ' ' * prefix_space + s_stripped[end_index+1:].lstrip()
                else:
                    result = reply
            except Exception as e:
                result = reply
                print(e)
            print(result)
            self.result_signal.emit(result)
    
    # 启动线程并处理结果
    self.chat_thread = ChatThread(self.ai_client, user_input)
    self.chat_thread.result_signal.connect(lambda res: show_reply(self, res))
    self.chat_thread.start()

def show_reply(self, reply):
    """显示 AI 回复，并触发说话动画"""
    time = datetime.datetime.now()
    #self.ui.history.append(f"\n返事   --{time}\n{reply}\n")
    character_id = voicevox_character_ids[self.ui.voice.currentText()]
    self.ui.message.clear()
    self.ui.message.setEnabled(True)
    self.ui.send.setEnabled(True)
    def task(self, reply, character_id, volume):
        audio_data = self.VoiceVoxEngine.synthesize_speech(reply, character_id)
        self.ui.history.append(f"\n返事   --{time}\n{reply}\n")
        self.VoiceVoxEngine.play_audio(audio_data, volume, self.live2d_widget)
        # 关键：target=task 而不是 target=task()，args传递参数元组
    if self.ui.language.currentText() != "中文":
        thread = threading.Thread(
            target=task,
            args=(self, result, character_id, self.volume),  # 把参数通过args传递给task
            daemon=True
        )
        thread.start()  # 启动线程（异步执行task）
    else: 
        self.ui.history.append(f"\n返事   --{time}\n{reply}\n")




class VoiceVoxEngine:
    def __init__(self, host="127.0.0.1", port=50021):
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.audio = pyaudio.PyAudio()

    # 获取语音合成音频数据
    def synthesize_speech(self, text, speaker_id):
        if not text.strip():
            return None
        
        # Step1: 获取发音符号
        phoneme_url = f"{self.base_url}/audio_query"
        phoneme_params = {"text": text, "speaker": speaker_id}
        phoneme_res = requests.post(phoneme_url, params=phoneme_params)
        if phoneme_res.status_code != 200:
            print(f"发音符号生成失败: {phoneme_res.status_code}")
            return None
        
        # Step2: 合成语音
        synthesis_url = f"{self.base_url}/synthesis"
        synthesis_params = {"speaker": speaker_id}
        synthesis_res = requests.post(
            synthesis_url,
            params=synthesis_params,
            data=json.dumps(phoneme_res.json()),
            headers={"Content-Type": "application/json"}
        )
        if synthesis_res.status_code != 200:
            print(f"语音合成失败: {synthesis_res.status_code}")
            return None
        
        return synthesis_res.content

    # 播放音频数据
    def play_audio(self, audio_data, volume, live2d_widget):
        if not audio_data:
            return
        
        # 写入临时WAV文件（Pygame播放更稳定）
        temp_wav = "temp_voice.wav"
        with wave.open(temp_wav, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(24000)
            wf.writeframes(audio_data)
        
        # Pygame播放音频
        pygame.mixer.init()
        global sound
        sound = pygame.mixer.Sound(temp_wav)
        pygame.mixer.Sound.set_volume(sound, volume)
        sound.play()

        live2d_widget.wavHandler.Start("temp_voice.wav")
        
        # 等待播放完成后删除临时文件
        while pygame.mixer.get_busy():
            time.sleep(0.1)
        pygame.mixer.quit()
        os.remove(temp_wav)
        
    def set_volume(self):
        pygame.mixer.Sound.set_volume(sound, self.volume)





            