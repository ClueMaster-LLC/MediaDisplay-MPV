from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import requests
import time
import json


class MasterOverlay(QWidget):

    def __init__(self):
        super(MasterOverlay, self).__init__()

        self.screen_width = QApplication.desktop().width()
        self.screen_height = QApplication.desktop().height()

        # widgets

        self.master_layout = QVBoxLayout(self)

        self.verify_status_timer = QTimer()
        self.verify_status_timer.setInterval(4000)
        self.verify_status_timer.timeout.connect(self.verify_game_status)
        self.verify_status_timer.start()

        self.countdown_label = QLabel(self)
        self.countdown_timer = QTimer()
        self.countup_label = QLabel(self)
        self.countup_timer = QTimer()

        # apis

        with open("assets/application data/unique code.json") as unique_code_json_file:
            initial_dictionary = json.load(unique_code_json_file)

        self.device_id = initial_dictionary["Device Unique Code"]

        with open("assets/application data/GameDetails.json") as game_details_json_file:
            initial_dictionary = json.load(game_details_json_file)

        self.game_id = initial_dictionary["gameId"]
        self.room_info_api = "https://deviceapi.cluemaster.io/api/Device/GetRoomInfo/{}".format(self.device_id)
        self.get_game_timer_api = "https://deviceapi.cluemaster.io/api/Device/GetGameTimer/{}".format(self.game_id)

        # methods

        self.window_configurations()
        self.load_application_timer()

    def window_configurations(self):

        self.resize(self.screen_width, self.screen_height)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.showFullScreen()

    def resizeEvent(self, event):

        event.ignore()

    def keyPressEvent(self, event):

        event.ignore()

    def dragMoveEvent(self, event):

        event.ignore()

    def load_application_timer(self):

        room_info_response = requests.get(self.room_info_api).json()
        timer_parameter = room_info_response["TimeLimit"]

        if timer_parameter >= 1:
            self.application_countdown_timer()
        else:
            self.application_countup_timer()

    def verify_game_status(self):

        with open("assets/application data/GameDetails.json") as game_details_json_file:
            initial_dictionary = json.load(game_details_json_file)

        game_details_response = initial_dictionary
        if game_details_response["gameStatus"] == 1:

            if self.countup_timer.isActive() is False:
                self.countup_timer.start()

            elif self.countdown_timer.isActive() is False:
                self.countdown_timer.start()

            else:
                pass

        elif game_details_response["gameStatus"] == 2:
            if self.countup_timer.isActive():
                self.countup_timer.stop()

            elif self.countdown_timer.isActive():
                self.countdown_timer.stop()

            else:
                pass

        elif game_details_response["gameStatus"] == 3:

            self.close()

        elif game_details_response["gameStatus"] == 4:

            if self.countup_timer.isActive():
                self.countup_timer.stop()

            elif self.countdown_timer.isActive():
                self.countdown_timer.stop()

            else:
                pass

    def fetch_cloud_timer(self):

        get_game_timer_response = requests.get(self.get_game_timer_api).json()
        timer_value_from_api = int(get_game_timer_response["timer"])
        return timer_value_from_api

    def application_countdown_timer(self):

        self.timer_value_from_api = self.fetch_cloud_timer()

        self.countdown_label.setFont(QFont("Ubuntu", 200))
        self.countdown_label.setStyleSheet("""QLabel{color:white; font-weight:bold;}""")
        self.master_layout.addWidget(self.countdown_label, alignment=Qt.AlignCenter)
        self.countdown_label.show()

        self.countdown_timer.setInterval(1000)
        self.countdown_timer.timeout.connect(self.update_countdown_timer)
        self.countdown_timer.start()

    def update_countdown_timer(self):

        if self.timer_value_from_api < 0:
            self.countdown_label.setText("00:00:00")

        if self.timer_value_from_api >= 1:
            self.timer_value_from_api -= 1
            hours_minutes_seconds_format = time.strftime("%H:%M:%S", time.gmtime(self.timer_value_from_api))
            self.countdown_label.setText(hours_minutes_seconds_format)

    def application_countup_timer(self):

        self.timer_value_from_api = self.fetch_cloud_timer()

        self.countup_label.setFont(QFont("Ubuntu", 200))
        self.countup_label.setStyleSheet("""QLabel{color:white; font-weight:bold;}""")
        self.master_layout.addWidget(self.countup_label, alignment=Qt.AlignCenter)
        self.countup_label.show()

        self.countup_timer.setInterval(1000)
        self.countup_timer.timeout.connect(self.update_countup_timer)
        self.countup_timer.start()

    def update_countup_timer(self):

        self.timer_value_from_api += 1
        hours_minutes_seconds_format = time.strftime("%H:%M:%S", time.gmtime(self.timer_value_from_api))
        self.countup_label.setText(hours_minutes_seconds_format)