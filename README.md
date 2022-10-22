# MMVC_Client-Config-Generator
A GUI configuration file generator for MMVC_Client (unofficial)
MMVC_Client向けGUI設定ファイル生成ツール(非公式)

![MMVC_Client_confgen_v0010](https://user-images.githubusercontent.com/24561326/197327727-7f3bad5a-4658-4358-aec7-4f50d7cf5f87.PNG)

## MMVC_Client
https://github.com/isletennos/MMVC_Client

## Requirement
- Windows環境
- MMVC_Client v0.3.0.0  
- Python 3.7 以上の環境(おそらく)

## Usage
1. 必要なライブラリのインストール
```python
pip install PySide6 qt-material
```

2. `mmvc_client_config_generator.pyw`をMMVC_Clientの**output_audio_device_list.exe**と同じディレクトリにコピー  

3. `mmvc_client_config_generator.pyw`をダブルクリックして実行(自動で同じディレクトリにある**myprofile_.conf**が読み込まれます)  
  もしくはロードしたい設定ファイルを**pyw**ファイルにドラッグ&ドロップします

## Features
詳しい設定内容はこちらをご確認ください。  
MMVC_Client  
https://github.com/isletennos/MMVC_Client
