import os
import json
import uuid
import re
import random
import time
import locale
import requests
import urllib3.exceptions
from PyQt5.QtCore import QThread, Qt, pyqtSignal
from PyQt5.QtGui import QFont, QMovie, QIcon
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QDesktopWidget

ROOT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))


class SplashBackend(QThread):
    skip_authentication = pyqtSignal(bool)

    def __init__(self):
        super(SplashBackend, self).__init__()

        self.is_killed = False

    def run(self):

        time.sleep(2)
        if os.path.isdir("assets/application data") is False:
            os.mkdir(os.path.join(ROOT_DIRECTORY, "assets/application data"))

        else:
            pass

        if os.path.isfile(os.path.join("assets/application data", "unique code.json")):
            with open(os.path.join(ROOT_DIRECTORY, "assets/application data", "unique code.json")) as file:
                json_object_of_unique_code_file = json.load(file)

            device_unique_code = json_object_of_unique_code_file["Device Unique Code"]
            device_files_url = f"https://deviceapi.cluemaster.io/api/Device/GetDeviceFiles/{device_unique_code}"

            while self.is_killed is False:
                try:
                    if requests.get(device_files_url).content.decode("utf-8") == "No Device Found":
                        self.skip_authentication.emit(False)

                    else:
                        self.skip_authentication.emit(True)

                except urllib3.exceptions.NewConnectionError:
                    time.sleep(2)
                    continue

                except requests.exceptions.ConnectionError:
                    time.sleep(2)
                    continue

                else:
                    break

        else:
            numbers = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
            alphabets = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S",
                         "T", "U", "V", "W", "X", "Y", "Z"]

            random_pair = [random.choice(alphabets), random.choice(numbers), random.choice(alphabets),
                           random.choice(numbers)]
            get_raw_mac = ':'.join(re.findall('..', '%012x' % uuid.getnode())).replace(":", "").upper()

            splitting_each_character = [character for character in get_raw_mac]

            first_pair = "".join(splitting_each_character[:4])
            second_pair = "".join(splitting_each_character[4:8])
            third_pair = "".join(splitting_each_character[8:12])
            fourth_pair = "".join(random_pair)

            full_unique_code = first_pair + "-" + second_pair + "-" + third_pair + "-" + fourth_pair

            json_object = {"Device Unique Code": full_unique_code}
            with open(os.path.join(ROOT_DIRECTORY, "assets/application data", "unique code.json"), "w") as file:
                json.dump(json_object, file)

            self.skip_authentication.emit(False)

    def stop(self):

        self.is_killed = True
        self.run()


class SplashWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.screen_width = QApplication.desktop().width()
        self.screen_height = QApplication.desktop().height()
        self.font = QFont("Ubuntu", 19)

        self.window_config()
        self.frontend()

    def window_config(self):

        self.font.setWordSpacing(2)
        self.font.setLetterSpacing(QFont.AbsoluteSpacing, 1)

        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        self.setFixedHeight(int(self.screen_height // 2.5))
        self.setFixedWidth(int(self.screen_width // 2.9))
        self.setWindowIcon(QIcon("assets/icons/app_icon.png"))
        self.setStyleSheet("background-color:#191F26; color:white;")

    def frontend(self):

        self.main_layout = QVBoxLayout()

        application_name = QLabel(self)
        application_name.setFont(self.font)
        application_name.setText("ClueMaster TV Display Timer")
        application_name.setStyleSheet("color: white; font-weight:bold;")

        version = QLabel(self)
        version.setText("Version 0.3.1")
        version.setFont(self.font)
        version.setStyleSheet("color: white; font-size: 19px; font-weight:bold;")

        gif = QMovie("assets/icons/security_loading.gif")
        gif.start()

        loading_gif = QLabel(self)
        loading_gif.setMovie(gif)
        loading_gif.show()

        self.main_layout.addSpacing(self.height() // 9)
        self.main_layout.addWidget(application_name, alignment=Qt.AlignCenter)
        self.main_layout.addSpacing(10)
        self.main_layout.addWidget(version, alignment=Qt.AlignCenter)
        self.main_layout.addStretch(1)
        self.main_layout.addWidget(loading_gif, alignment=Qt.AlignCenter)

        self.setLayout(self.main_layout)
        self.connect_backend_thread()

    def connect_backend_thread(self):

        self.splash_thread = SplashBackend()
        self.splash_thread.start()
        self.splash_thread.skip_authentication.connect(self.switch_window)

    def switch_window(self, skip):

        self.splash_thread.stop()

        if skip is True:
            import loading_screen
            self.i_window = loading_screen.LoadingScreen()
            self.i_window.show()
            self.deleteLater()

        else:
            if skip is False:
                import authentication_screen
                self.i_window = authentication_screen.AuthenticationWindow()
                self.i_window.show()
                self.deleteLater()


def main():
    application = QApplication([])
    locale.setlocale(locale.LC_NUMERIC, 'C')
    application.setApplicationVersion("0.3.1")
    window = SplashWindow()
    window.show()
    application.exec_()


main()
