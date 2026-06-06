# live2d-based-desktop-pet-with-tts-chatting
A desktop pet application with mouse tracking, model parameter control, and VOICEVOX-based tts chatting

Here is the English translation of your program documentation:

Program User Manual
1. Launching the Program
Double-click main_program to launch.

2. Loading the Model Interface
On the first launch, select "Load new model." Navigate to your model folder and select the .model3.json file.
Note: The live2d.v3 library used by this program only supports this format; older models are not compatible.

3. Main Interface

3.1 Playback Actions: Use the Motions dropdown to play specific actions. Check "Auto" to trigger random animations at set intervals; adjust the frequency via "Time." Clicking on the model will also trigger random actions.

3.2 Model Control: Use the mouse scroll wheel to zoom the model in/out and drag the model to adjust its position.

3.3 Mouse Tracking: Right-click the model and select "Track" to enable/disable mouse tracking. Use the "X response" slider on the main interface to adjust the responsiveness to mouse movement, and use buttons like "Reverse X" to flip the tracking direction. Use "Set tracking parameters" if the model exhibits tracking issues (e.g., if the model uses HeadParamX instead of the default ParamX, you must manually specify the parameter name here).

3.4 Advanced Parameter Control: The program reads the .cdi3.json file in the model folder to generate a parameter list. Click "Add" in the lower panel to add parameter controls. This works similarly to mouse tracking—select a parameter, set the response range, and use the slider to adjust the value. This feature allows for costume changes (e.g., character outfits) and precise control over arms, eyes, or special effects.
Note: If a file selection dialog appears upon loading a model, the program could not automatically locate the .cdi3.json file; you must select it manually. If a model lacks this file, the advanced control feature will be unavailable.

3.5 Save & Reset: Upon closing, all advanced parameter configurations and mouse tracking settings are automatically saved to histor.json in the same directory as the main_program.exe. You can load these directly from your history next time. Right-click the model and select "Reset" to return all parameters to their default state (as they were when the model was first loaded).

3.6 Expressions: Right-click the model to see a menu containing the model's built-in expressions. Some models may use these slots for different outfits.

4. Conversation Features (Powered by VOICEVOX)

4.0 Installation: This program uses the third-party application VOICEVOX for speech synthesis. Please download and install it from https://voicevox.hiroshiba.jp/ before using the chat feature.

4.1 First-Time Setup: A pop-up will request your API key, as AI conversations are powered by the DeepSeek API. Paste your key and click "OK." Then, select the location of the installed VOICEVOX.exe. If the VOICEVOX application window opens, minimize it—do not close it!

4.2 Language, Voice, and Lip-Sync:

Language: Set the reply language (CN/EN/JP).

Note: To avoid OOC (Out of Character) behavior, voice synthesis is disabled for Chinese replies.

Voice: Select a voice from the "Voice" (ボイス) dropdown. These are built-in VOICEVOX characters; if you are sensitive to voice-matching accuracy, you may prefer not to use the chat function.

Lip-Sync: Use "Lip Open Width" (口の開き幅) to adjust how wide the mouth opens while speaking. The system saves your voice and lip-sync preferences for each model upon exit.

4.3 Chatting: Type your message in the chat box and click the "Send" (送信) button or press Enter.

Disclaimer: This program is a personal, research-driven project for technical exchange. It has no commercial purpose. The developer assumes no responsibility for system instability, data loss, or hardware damage resulting from the use of this program.

1. 启动程序：双击main_program即可
2. 加载模型界面：首次启选择load new model，然后在模型文件夹里选择想加载的模型的.model3.json文件打开（使用的live2d.v3库只支持这个格式的模型，旧的模型都用不了）
3. 应用主界面：
	3.1.播放动作：motions选项框可以选择播放指定动作，勾选auto则会隔一段时间随机播放动作。
时间间隔通过time设定。同时点击模型也可以触发随机播放动作。
	3.2.模型控制：鼠标滚轮可以缩放模型大小，拖动模型可以调整其位置。
	3.3.鼠标追踪相关功能：右键模型，点击track选项可以启用鼠标追踪，再次点击track可关闭该功能。主界面上的x response可以设置模型对鼠标活动的相应幅度，reverse x等按钮可以反转追踪方向。set tracking parameters用于模型追踪出问题的时候，手动设定追踪参数（比如左右转头，默认的参数是ParamX之类的东西，但是有的模型的参数可能叫HeadParamX，这个时候应用就识别不到，就要通过set tracking parameters手动指定。）
	3.4. 高级参数控制：程序通过读取模型文件夹下的.cdi3.json文件来获取参数列表。主界面下面的那个大框，点击add可以添加参数控制，其原理跟鼠标追踪是一样的。选项框选择要控制的参数，response设置响应幅度，滑块调整参数值。这个功能可以实现换装（绫地宁宁可以直接当换装游戏来玩），以及对胳膊，眼睛和特效等参数的单独控制。注意，有些模型加载出来的时候会弹出一个选择文件的对话框。这说明程序没有自动找到.cdi3.json文件，需要手动选择。当然有的模型是没有这个文件的，对于这些模型，高级参数控制功能不可用。
	3.5. 保存与重置：关闭应用的时候高级参数控制区的内容，以及调整之后的鼠标追踪响应等都会自动保存到主程序(main_program.exe）相同目录下的histor.json文件。下次启动的时候可以直接从历史模型中加载。另外，右键模型，菜单中的reset选项会把模型的所有参数重置会默认状态（就是第一次加载模型打开的那个状态）
	3.6.模型表情：右键模型，弹出菜单中除了track和reset，剩下的都是模型自带的表情，点击即可切换。有些模型的表情其实是不同的服装（比如绫地宁宁）
4. 对话功能（第三方依赖VOICEVOX，请提前安装该应用（详见4.0.））：
	4.0.VOICEVOX的安装：程序通过第三方应用VOICEVOX进行语音合成，在启用对话功能前请先前往https://voicevox.hiroshiba.jp/下载安装VOICEVOX应用！
	4.1.首次启动对话：会出现弹窗要你设置API key，这是因为ai对话是通过联网调用deepseek的api实现的。请将你自己的deepseek api key复制粘贴到对话框，点击OK。随后出现文件选择对话框，请选择已安装的VOICEVOX.exe的位置。这样对话功能就能使用了。如果弹出了voicevox的应用窗口，手动最小化就好了，但是不要关闭它！
	4.2.语言，声音，和嘴唇活动：言语选项框可以设定回复语言（中日英），这样不论你用什么语言提问，应用都会使用指定的语言回答。注意：为了避免ooc，中文回答不会启用语音合成。ボイス选项框可以选择语音合成的声音，这些都是voicevox内置的角色，不可能跟模型角色的声音一模一样，所以请选择一个自己喜欢/最接近模型角色的声音。如果介意声音这一点请不要使用聊天功能。最后的口の開き幅可以调整角色说话时嘴唇的张开幅度。关闭应用时系统会保存该模型对应的声音和嘴巴活动幅度。
	4.3.聊天：底下的聊天框输入，然后点击送信按钮或者enter键都可以发送。

本程序为个人兴趣驱动的技术研究与学术交流项目，ai生成代码含量极高，不具有任何商业目的。开发者不对程序运行导致的任何系统不稳定性、数据丢失或硬件损坏承担责任
