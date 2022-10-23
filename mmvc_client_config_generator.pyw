# -*- coding: utf-8 -*
import sys
import os
import json
import subprocess

from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from qt_material import apply_stylesheet

stylesheet_extra = {
    'density_scale': '-1 ',
}

default_profile_path = '.\myprofile.conf'
default_client_path = '.\mmvc_client_GPU_v0.3.0.0\mmvc_client_GPU.exe'

def load_config_file(file_path):
    json_open = open(file_path, 'r', encoding='utf-8')
    json_load = json.load(json_open)
    return json_load


def get_audio_devices_subprocess():
    audio_devices_input = list()
    audio_devices_output = list()
    audio_devices_others = list()
    try:
        result = subprocess.run('.\output_audio_device_list.exe', shell=True, check=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        for line in result.stdout.splitlines():
            print(">>" + line)
    except subprocess.CalledProcessError:
        print('デバイスリストの取得に失敗しました。', file=sys.stderr)
    else:
        print("Success for Getting Sound Device Info")

    with open('./audio_device_list.txt', 'r', encoding='UTF-8') as f:
        device_list = f.read().splitlines()
        for device in device_list:
            #print(device.split(' デバイス名：', 1))
            if device[0:3] == '入力：':
                audio_devices_input.append(device.split(' デバイス名：', 1)[1][1:-1])
            elif device[0:3] == '出力：':
                audio_devices_output.append(device.split(' デバイス名：', 1)[1][1:-1])
            else:
                audio_devices_others.append(device.split(' デバイス名：', 1)[1][1:-1])

    audio_devices_input+=audio_devices_others
    audio_devices_output+=audio_devices_others

    return audio_devices_input, audio_devices_output


def fix_path_for_windows(path):
    return path.replace("/", "\\")


def launch_mmvc_client(_client_path, _profile_path):
    print(_client_path)
    print(_profile_path)
    subprocess.Popen([os.path.abspath(_client_path),os.path.abspath(_profile_path)])



#1段目にLabel，2段目にComboBoxのレイアウトを作成
class CreateComboBoxLayout(QVBoxLayout):
    def __init__(self, label_text, parent=None):
        QVBoxLayout.__init__(self, parent)

        self.layout1 = QHBoxLayout()
        self.addLayout(self.layout1, 0)
        self.layout2 = QHBoxLayout()
        self.addLayout(self.layout2, 1)

        self.label = QLabel(parent)
        self.label.setText(label_text)

        self.combo_box = QComboBox(parent)

        self.layout1.addWidget(self.label, 0)
        self.layout2.addWidget(self.combo_box, 0)

    def updateComboList(self, data_list):
        prev_item = self.combo_box.currentText()
        update_index = 0
        self.combo_box.clear()

        for i, data in enumerate(data_list) :
            self.combo_box.addItem(data)
            if prev_item == data:
                update_index = i

        self.combo_box.setCurrentIndex(update_index)

#Label，SpinBoxがセットのレイアウトを作成
class CreateSpinBoxLayout(QHBoxLayout):
    def __init__(self, label_text,label_width, min_num, max_num, parent=None):
        QHBoxLayout.__init__(self, parent)
        self.label = QLabel(parent)
        self.label.setText(label_text)

        self.spin_box = CustomQSpinBox(parent)
        if label_width != None:
            self.label.setFixedWidth(label_width)
        if min_num != None:
            self.spin_box.setMinimum(min_num)
        if max_num != None:
            self.spin_box.setMaximum(max_num)

        self.addWidget(self.label, 0)
        self.addWidget(self.spin_box, 1)

#マウスホイールでSpinboxの値をうっかり変えそうなので滅する
class CustomQSpinBox(QSpinBox):
    def wheelEvent(self, event):
        event.ignore()

#Label，LineEditでファイル選択のレイアウトを作成
class CreateFileOpenLayout(QHBoxLayout):
    def __init__(self, label_text, label_width, file_filter=None, parent=None):
        self.__cbf_pointer = None
        self.file_filter = file_filter

        QHBoxLayout.__init__(self, parent)
        self.label = QLabel(parent)
        self.label.setText(label_text)
        self.label.setFixedWidth(label_width)

        self.line_edit = QLineEdit(parent)

        self.button1 = QPushButton("...",parent)
        self.button1.clicked.connect(self.get_path)

        self.addWidget(self.label, 0)
        self.addWidget(self.line_edit, 0)
        self.addWidget(self.button1, 0,alignment=(Qt.AlignRight))

    def get_path(self):
        dir_ = MainWindow.OpenFile(self, f'Select a {self.label.text()}:', f'{self.line_edit.text()}', self.file_filter)

        print(dir_[0])
        if len(dir_[0]) != 0:
            self.line_edit.setText(f"{fix_path_for_windows(dir_[0])}")
        #コールバック関数があったら実行
        if self.__cbf_pointer != None:
            self.cbfHandler(dir_[0])

    #コールバック周りが適当
    def setCallbackFunc(self, pointer):
        self.__cbf_pointer = pointer
    def clearCallbackFunc(self):
        self.__cbf_pointer = None
    def cbfHandler(self, *args):
        return self.__cbf_pointer(*args)

# LabelとCheckboxがセットになったレイアウトを作成
class CreateCheckboxLayout(QHBoxLayout):
    def __init__(self, label_text, label_width, parent=None):
        QHBoxLayout.__init__(self, parent)
        self.label = QLabel(parent)
        self.label.setText(label_text)
        self.label.setFixedWidth(label_width)

        self.checkbox = QCheckBox(parent)

        self.addWidget(self.label, 0)
        self.addWidget(self.checkbox, 0)


#メインのウィンドウを作成
class MainWindow(QWidget):
    # コンストラクタ

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        #ベースになるレイアウトを作成
        self.main_grid = QGridLayout()
        self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint)
        self.setLayout(self.main_grid)

        # Window Settings
        self.setWindowTitle('MMVC Client Config Generator')
        self.setGeometry(500, 400, 950, 350)

        #メイングリッドの(0, 0) ConfigとClientのパスとか指定するVBoxを作成
        self.vbox_exfile_path = QVBoxLayout()
        self.main_grid.addLayout(self.vbox_exfile_path, 0, 0)

        self.path_config = CreateFileOpenLayout("Config File", 70, "Client User Profile (*.conf)")
        self.path_config.setCallbackFunc(self.LoadJsonData)
        self.vbox_exfile_path.addLayout(self.path_config, 0)
        self.path_client = CreateFileOpenLayout("MMVC Client", 70, "MMVC Client (*.exe)")
        self.vbox_exfile_path.addLayout(self.path_client, 0)

        #メイングリッドの(0, 1) ConfigとClientのボタンを格納するVBoxを作成
        self.vbox_start_btn = QVBoxLayout()
        self.main_grid.addLayout(self.vbox_start_btn, 0, 1)

        self.btn_save_json = QPushButton("名前を付けて設定ファイルを保存")
        self.btn_save_json.clicked.connect(\
            lambda: MainWindow.SaveConfigFile(self, self.path_config.line_edit.text(), self.path_config.line_edit.setText, "MMVC Client Config File (*.conf)")\
        )
        self.vbox_start_btn.addWidget(self.btn_save_json, 0)

        self.btn_launch_clienet = QPushButton("MMVC Clientを実行")
        self.btn_launch_clienet.clicked.connect(\
            lambda: launch_mmvc_client(self.path_client.line_edit.text(), self.path_config.line_edit.text())\
        )
        self.vbox_start_btn.addWidget(self.btn_launch_clienet, 0)


        #メイングリッドの(1, 0) DeviceのQGroupBox
        self.groupbox_device = QGroupBox("Device")
        self.groupbox_device.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.main_grid.addWidget(self.groupbox_device, 1, 0)
        self.vbox_device = QVBoxLayout()
        self.groupbox_device.setLayout(self.vbox_device)

        self.combo_class1 = CreateComboBoxLayout("INPUT DEVICE 1")
        self.vbox_device.addLayout(self.combo_class1, 0)
        self.combo_class1.layout1.addStretch()

        self.combo_class2 = CreateComboBoxLayout("INPUT DEVICE 2")
        self.vbox_device.addLayout(self.combo_class2, 0)

        self.combo_class3 = CreateComboBoxLayout("OUTPUT DEVICE")
        self.vbox_device.addLayout(self.combo_class3, 0)

        self.vbox_device.addSpacing(8)

        self.hbox_device = QHBoxLayout()
        self.vbox_device.addLayout(self.hbox_device)

        self.spin_gpu_id = CreateSpinBoxLayout("GPUID", 40, -1, 99)
        self.spin_gpu_id.addSpacing(30)
        self.hbox_device.addLayout(self.spin_gpu_id, 1)

        self.btn_getdevice = QPushButton('Get Sound Device Info',self)
        self.btn_getdevice.clicked.connect(self.UpdateDeviceList)
        self.hbox_device.addWidget(self.btn_getdevice, 1)


        #メイングリッドの(1, 1) vc_configのQGroupBox
        self.groupbox_vcconf = QGroupBox("VC Config")
        self.groupbox_vcconf.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.main_grid.addWidget(self.groupbox_vcconf, 1,1)

        self.vbox_vcconf = QVBoxLayout()
        self.groupbox_vcconf.setLayout(self.vbox_vcconf)

        self.vbox_vcconf_params = QVBoxLayout()
        self.vbox_vcconf.addLayout(self.vbox_vcconf_params)
        self.frame_length = CreateSpinBoxLayout("frame_length", 125, 0, 2**20)
        self.vbox_vcconf_params.addLayout(self.frame_length)
        self.delay_flames = CreateSpinBoxLayout("delay_flames", 125, 0, 2**20)
        self.vbox_vcconf_params.addLayout(self.delay_flames)
        self.overlap = CreateSpinBoxLayout("overlap", 125, 0, 2**20)
        self.vbox_vcconf_params.addLayout(self.overlap)
        self.dispose_stft_specs = CreateSpinBoxLayout("dispose_stft_specs", 125, 0, 2**20)
        self.vbox_vcconf_params.addLayout(self.dispose_stft_specs)
        self.dispose_conv1d_specs = CreateSpinBoxLayout("dispose_conv1d_specs", 125, 0, 2**20)
        self.vbox_vcconf_params.addLayout(self.dispose_conv1d_specs)

        self.hbox_vcconf_voiceid = QHBoxLayout()
        self.hbox_vcconf_voiceid.setAlignment(Qt.AlignCenter)
        self.vbox_vcconf.addLayout(self.hbox_vcconf_voiceid)
        self.source_id = CreateSpinBoxLayout("source_id", 60, 0, 2**20)
        self.hbox_vcconf_voiceid.addLayout(self.source_id, 0)
        self.hbox_vcconf_voiceid.addSpacing(30)
        self.target_id = CreateSpinBoxLayout("target_id", 60, 0, 2**20)
        self.hbox_vcconf_voiceid.addLayout(self.target_id, 0)


        #メイングリッドの(2, 0) PathのQGroupBox
        self.groupbox_path = QGroupBox("Path")
        self.groupbox_path.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.main_grid.addWidget(self.groupbox_path, 2,0)
        self.vbox_path = QVBoxLayout()
        self.groupbox_path.setLayout(self.vbox_path)

        self.path_json = CreateFileOpenLayout("JSON", 40, "MMVC Config File (*.json)")
        self.vbox_path.addLayout(self.path_json, 0)

        self.path_model = CreateFileOpenLayout("MODEL", 40, "MMVC Moodel File (*.pth)")
        self.vbox_path.addLayout(self.path_model, 0)

        self.path_noise = CreateFileOpenLayout("NOISE", 40, "Noise Sound File (*.wav)")
        self.vbox_path.addLayout(self.path_noise, 0)


        #メイングリッドの(2, 1) OthersのQGroupBox
        self.groupbox_others = QGroupBox("Others")
        self.groupbox_others.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.main_grid.addWidget(self.groupbox_others, 2,1)
        self.vbox_others = QVBoxLayout()
        self.groupbox_others.setLayout(self.vbox_others)

        self.hbox_others = QHBoxLayout()
        self.hbox_others.setAlignment(Qt.AlignCenter)
        self.vbox_others.addLayout(self.hbox_others)
        self.others_nr = CreateCheckboxLayout("use_nr", 60)
        self.hbox_others.addLayout(self.others_nr, 0)
        self.hbox_others.addSpacing(30)
        self.others_vs = CreateCheckboxLayout("voice_selector", 80)
        self.hbox_others.addLayout(self.others_vs, 0)
        self.hbox_others.addStretch(1)

        self.voice_form_layout = QFormLayout()
        self.vbox_others.addLayout(self.voice_form_layout)
        self.voice_list_label = QLabel("voice_list")
        self.voice_list_line = QLineEdit()
        self.voice_label_label = QLabel("voice_label")
        self.voice_label_line = QLineEdit()
        self.voice_form_layout.addRow(self.voice_list_label, self.voice_list_line)
        self.voice_form_layout.addRow(self.voice_label_label, self.voice_label_line)

        # Set import JSON data
        try:
            json_data = load_config_file(profile_path)
            print(json_data)
            self.path_config.line_edit.setText(f"{os.path.abspath(profile_path)}")
            self.path_client.line_edit.setText(f"{os.path.abspath(client_path)}")

            self.UpdateData(json_data)

        except Exception as e:
            print(e.args)
            print(f"Config File import did not complete!")

        #ウィンドウ初期化完了

    def LoadJsonData(self, path):
        if len(path) != 0:
            try:
                json_data = load_config_file(path)
                self.UpdateData(json_data)
            except Exception as e:
                print(e.args)
                print(f"Config File import did not complete!")
            else:
                print(f"設定ファイルの読み込みに成功しました {path}")


    def UpdateData(self, json_data):
        self.combo_class1.combo_box.clear()
        self.combo_class1.combo_box.addItem(f"{json_data['device']['input_device1']}")
        self.combo_class2.combo_box.clear()
        self.combo_class2.combo_box.addItem(f"{json_data['device']['input_device2']}")
        self.combo_class3.combo_box.clear()
        self.combo_class3.combo_box.addItem(f"{json_data['device']['output_device']}")

        self.spin_gpu_id.spin_box.setValue(json_data['device']['gpu_id'])

        self.frame_length.spin_box.setValue(json_data['vc_conf']['frame_length'])
        self.delay_flames.spin_box.setValue(json_data['vc_conf']['delay_flames'])
        self.overlap.spin_box.setValue(json_data['vc_conf']['overlap'])
        self.dispose_stft_specs.spin_box.setValue(json_data['vc_conf']['dispose_stft_specs'])
        self.dispose_conv1d_specs.spin_box.setValue(json_data['vc_conf']['dispose_conv1d_specs'])
        self.source_id.spin_box.setValue(json_data['vc_conf']['source_id'])
        self.target_id.spin_box.setValue(json_data['vc_conf']['target_id'])

        self.path_json.line_edit.setText(json_data['path']['json'])
        self.path_model.line_edit.setText(json_data['path']['model'])
        self.path_noise.line_edit.setText(json_data['path']['noise'])

        self.others_nr.checkbox.setChecked(json_data['others']['use_nr'])
        self.others_vs.checkbox.setChecked(json_data['others']['voice_selector'])
        self.voice_list_line.setText(', '.join(map(str, json_data['others']['voice_list'])))
        self.voice_label_line.setText(', '.join(json_data['others']['voice_label']))


    def UpdateDeviceList(self):
        print('Getting Sound Device Info...')
        self.btn_getdevice.setText('Getting Sound Device Info...')
        self.btn_getdevice.repaint()

        input_device, output_device = get_audio_devices_subprocess()

        self.combo_class1.updateComboList(input_device)
        self.combo_class2.updateComboList(input_device)
        self.combo_class3.updateComboList(output_device)

        #Input Device2にFalseを追加
        dev2_index = self.combo_class2.combo_box.currentIndex()
        self.combo_class2.combo_box.insertItem(0, "False")
        if dev2_index != 0:
            self.combo_class2.combo_box.setCurrentIndex(dev2_index+1)
        else:
            self.combo_class2.combo_box.setCurrentIndex(0)

        self.btn_getdevice.setText('Get Sound Device Info')
        self.btn_getdevice.repaint()


    def OpenFile(self, caption , path, filter=None):
        update_path = QFileDialog().getOpenFileName(None, f'{caption}', f'{path}', filter)
        return update_path


    def SaveFile(self, caption , path, filter=None):
        update_path = QFileDialog().getSaveFileName(None, f'{caption}', f'{path}', filter)
        return update_path


    def SaveConfigFile(self, path, callbackfunc=None, filter=None):
        self.new_path = MainWindow.SaveFile(self, "Save configuration file", path, filter)
        #キャンセル押したら何もしない
        if len(self.new_path[0]) != 0:
            #コールバック周りが雑
            if callbackfunc!=None:
                callbackfunc(fix_path_for_windows(self.new_path[0]))
            self.save_configuration_file()


    def save_configuration_file(self):
        profile_path = self.new_path[0]
        json_data = self.GenerateJsonData()
        try:
            with open(profile_path, 'w', encoding='UTF-8') as output_f:
                json.dump(json_data, output_f, ensure_ascii=False, indent=2, sort_keys=False, separators=(',', ': '))

        except Exception as e:
            print(e.args)            
        else:
            print(f"設定ファイルの保存に成功しました {profile_path}")


    def GenerateJsonData(self):
        config_dict = {}
        config_dict_device  = {}
        config_dict_vc_conf = {}
        config_dict_path    = {}
        config_dict_others  = {}

        try:
            config_dict_device['input_device1'] = self.combo_class1.combo_box.currentText()
            input_device2_text = self.combo_class2.combo_box.currentText()
            config_dict_device['input_device2'] = input_device2_text if input_device2_text!='False' else False
            config_dict_device['output_device'] = self.combo_class3.combo_box.currentText()
            config_dict_device['gpu_id']        = self.spin_gpu_id.spin_box.value()

            config_dict_vc_conf['frame_length']         = self.frame_length.spin_box.value()
            config_dict_vc_conf['delay_flames']         = self.delay_flames.spin_box.value()
            config_dict_vc_conf['overlap']              = self.overlap.spin_box.value()
            config_dict_vc_conf['dispose_stft_specs']   = self.dispose_stft_specs.spin_box.value()
            config_dict_vc_conf['dispose_conv1d_specs'] = self.dispose_conv1d_specs.spin_box.value()
            config_dict_vc_conf['source_id']            = self.source_id.spin_box.value()
            config_dict_vc_conf['target_id']            = self.target_id.spin_box.value()

            config_dict_path['json']  = self.path_json.line_edit.text()
            config_dict_path['model'] = self.path_model.line_edit.text()
            config_dict_path['noise'] = self.path_noise.line_edit.text()

            config_dict_others['use_nr']         =  self.others_nr.checkbox.isChecked()
            config_dict_others['voice_selector'] =  self.others_vs.checkbox.isChecked()
            config_dict_others['voice_list'] = [int(x.strip()) for x in self.voice_list_line.text().split(',')]
            config_dict_others['voice_label'] = [x.strip() for x in self.voice_label_line.text().split(',')]

            config_dict['device']  = config_dict_device
            config_dict['vc_conf'] = config_dict_vc_conf
            config_dict['path']    = config_dict_path
            config_dict['others']  = config_dict_others

        except Exception as e:
            print(e.args)

        return config_dict



if __name__ == '__main__':

    args = sys.argv
    if len(args) > 1:
        profile_path = args[1]
    else:
        profile_path = default_profile_path

    client_path = default_client_path

    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='dark_cyan.xml', extra=stylesheet_extra)

    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
