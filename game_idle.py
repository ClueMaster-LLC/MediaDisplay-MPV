import sys
import requests
import simplejson.errors
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtMultimedia import *
import os
import socket
import json
import threads


class IdentifyDevice(QWidget):
    def __init__(self):
        super(IdentifyDevice, self).__init__()

        self.screen_width = QApplication.desktop().width()
        self.screen_height = QApplication.desktop().height()

        self.API_status = True

        self.font = QFont("Ubuntu")
        self.font.setWordSpacing(2)
        self.font.setLetterSpacing(QFont.AbsoluteSpacing, 1)

        self.master_layout = QVBoxLayout(self)
        self.identify_device_audio_player = QMediaPlayer(self)
        self.app_root = os.path.abspath(os.path.dirname(sys.argv[0]))

        with open("assets/application data/unique code.json") as file:
            json_object = json.load(file)

        self.device_unique_code = json_object["Device Unique Code"]

        self.window_configurations()
        self.frontend()

    def window_configurations(self):

        self.move(0, 0)
        self.setFixedSize(self.screen_width, self.screen_height)
        self.setAttribute(Qt.WA_DontCreateNativeAncestors)
        self.setAttribute(Qt.WA_NativeWindow)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setStyleSheet("background-color: black;")
        self.showFullScreen()

    def keyPressEvent(self, event):
        event.ignore()

    def dragMoveEvent(self, event):
        event.ignore()

    def resizeEvent(self, event):
        event.ignore()
        
    def frontend(self):
        host = socket.gethostname()
        ipAddress = socket.gethostbyname(host)

        with open("assets/application data/IdentifyDeviceDetails.json") as file:
            json_object = json.load(file)

        self.font.setPointSize(40)

        self.device_name = QLabel(self)
        self.device_name.setFont(self.font)
        self.device_name.setText(f"DEVICE NAME : {json_object['DisplayText']}")
        self.device_name.setStyleSheet("color:white; font-weight:bold;")

        self.ip_address = QLabel(self)
        self.ip_address.setFont(self.font)
        self.ip_address.setText(f"IP ADDRESS : {ipAddress}")
        self.ip_address.setStyleSheet("color:white; font-weight:bold;")

        self.device_key = QLabel(self)
        self.device_key.setFont(self.font)
        self.device_key.setText(f"DEVICE KEY : {self.device_unique_code}")
        self.device_key.setStyleSheet("color:white; font-weight:bold;")

        self.api_status = QLabel(self)
        self.api_status.setFont(self.font)
        self.api_status.setText(f"API STATUS : {self.API_status}")
        self.api_status.setStyleSheet("color:white; font-weight:bold;")

        self.last_api_response_time = QLabel(self)
        self.last_api_response_time.setFont(self.font)
        self.last_api_response_time.setText(f"LAST API RESPONSE : {json_object['Requestdate']}")
        self.last_api_response_time.setStyleSheet("color:white; font-weight:bold;")

        self.master_layout.setSpacing(0)
        self.master_layout.setContentsMargins(int(self.screen_width / 10), int(self.screen_height / 15),
                                              int(self.screen_width / 10), int(self.screen_height / 15))

        self.master_layout.addWidget(self.device_name, alignment=Qt.AlignLeft)
        self.master_layout.addWidget(self.ip_address, alignment=Qt.AlignLeft)
        self.master_layout.addWidget(self.device_key, alignment=Qt.AlignLeft)
        self.master_layout.addWidget(self.api_status, alignment=Qt.AlignLeft)
        self.master_layout.addWidget(self.last_api_response_time, alignment=Qt.AlignLeft)

        audio = "assets/IdentifyDevice.mp3"

        media_content = QMediaContent(QUrl.fromLocalFile(os.path.join(self.app_root, audio)))
        self.identify_device_audio_player.setMedia(media_content)
        self.identify_device_audio_player.play()

        self.setLayout(self.master_layout)


class GameIdle(QMainWindow):
    def __init__(self):
        super(GameIdle, self).__init__()

        self.screen_width = QApplication.desktop().width()
        self.screen_height = QApplication.desktop().height()

        self.identify_device_thread = threads.IdentifyDevice()
        if self.identify_device_thread.isRunning() is False:
            self.identify_device_thread.start()
            self.identify_device_thread.identify_device.connect(self.identify_device)

        self.shutdown_restart_request = threads.ShutdownRestartRequest()
        if self.shutdown_restart_request.isRunning() is False:
            self.shutdown_restart_request.start()
            self.shutdown_restart_request.shutdown.connect(self.shutdown_device)
            self.shutdown_restart_request.restart.connect(self.restart_device)

        self.download_files_request = threads.DownloadConfigs()
        if self.download_files_request.isRunning() is False:
            self.download_files_request.start()

        self.font = QFont("Ubuntu")
        self.font.setWordSpacing(2)
        self.font.setLetterSpacing(QFont.AbsoluteSpacing, 1)

        self.shutdownRequestReceived = False
        self.restartRequestReceived = False
        self.isDeviceIdentifying = False
        self.no_media_files = False
        self.app_root = os.path.abspath(os.path.dirname(sys.argv[0]))

        self.master_background = QLabel(self)
        self.setCentralWidget(self.master_background)

        self.font.setWordSpacing(2)
        self.font.setLetterSpacing(QFont.AbsoluteSpacing, 1)
        self.setStyleSheet("background-color:#191F26;")

        with open("assets/application data/unique code.json") as file:
            json_object = json.load(file)

        self.device_unique_code = json_object["Device Unique Code"]

        fullScreen_shortCut = QShortcut(QKeySequence("F11"), self)
        fullScreen_shortCut.activated.connect(self.go_fullScreen)

        self.move(0, 0)
        self.setFixedSize(self.screen_width, self.screen_height)
        self.showFullScreen()
        self.frontend()

    def go_fullScreen(self):
        if self.isFullScreen() is True:
            self.showNormal()
            self.setCursor(Qt.ArrowCursor)
        else:
            self.setCursor(Qt.BlankCursor)
            self.showFullScreen()

    def frontend(self):
        try:
            device_files_url = f"https://deviceapi.cluemaster.io/api/Device/GetDeviceFiles/{self.device_unique_code}"
            self.json_object_of_get_device_files = requests.get(device_files_url).json()

        except json.decoder.JSONDecodeError:
            self.no_media_files = True

        except requests.exceptions.ConnectionError:
            pass

        except simplejson.errors.JSONDecodeError:
            self.no_media_files = True

        else:
            pass

        if self.no_media_files is False:
            if self.json_object_of_get_device_files["IsPhoto"] is True and len(os.listdir("assets/room data/picture")) != 0:

                self.picture_location = "assets/room data/picture/{}".format(os.listdir(os.path.join("assets/room data/picture/"))[0])
                self.master_background.setPixmap(QPixmap(self.picture_location).scaled(self.screen_width, self.screen_height))

            else:
                self.setStyleSheet("background-color:#191F26;")

        else:
            self.setStyleSheet("background-color:#191F26;")

    def identify_device(self, response):
        if response == 1:
            if self.isDeviceIdentifying is False:
                self.identify_device_window = IdentifyDevice()
                self.identify_device_window.show()
                self.isDeviceIdentifying = True

        else:
            if response == 0:
                # if response is other than 1 then hide the device information
                if self.isDeviceIdentifying is True:
                    self.identify_device_window.close()

                else:
                    pass
                self.isDeviceIdentifying = False

    def restart_device(self):
        # restarting device
        if self.restartRequestReceived is False:
            self.restartRequestReceived = True
            self.close()
            os.system("reboot")
        else:
            pass

    def shutdown_device(self):
        # shutting down device
        if self.shutdownRequestReceived is False:
            self.shutdownRequestReceived = True
            self.close()
            os.system("shutdown now")

        else:
            pass

    def deleteLater(self):

        if self.isDeviceIdentifying is True:
            self.identify_device_window.close()

        self.close()

    def stop_threads(self):

        self.identify_device_thread.stop()
        self.shutdown_restart_request.stop()
        self.download_files_request.stop()
