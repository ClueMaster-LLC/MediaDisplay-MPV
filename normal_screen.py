from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import requests

import master_overlay
import threads
import locale
import json
import time
import mpv
import os
import sys


class EndMediaWidget(QMainWindow):
    def __init__(self, status):
        super(EndMediaWidget, self).__init__()

        self.screen_width = QApplication.desktop().width()
        self.screen_height = QApplication.desktop().height()

        # widgets

        self.end_media_player = mpv.MPV(wid=str(int(self.winId())), vo="x11")

        # variables

        self.status = status

        # methods

        self.window_configurations()
        self.frontend()

    def window_configurations(self):

        self.resize(self.screen_width, self.screen_height)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.showFullScreen()

    def resizeEvent(self, event):

        event.ignore()

    def dragMoveEvent(self, event):

        event.ignore()

    def keyPressEvent(self, event):

        event.ignore()

    def frontend(self):

        if self.status == "won":

            default = "assets/room data/success end media/{}".format(
                            os.listdir(os.path.join("assets/room data/success end media/"))[0])

            self.end_media_player.play(default)
            self.end_media_player.register_event_callback(self.verify_status_of_end_media_player)

        elif self.status == "lost":

            default = "assets/room data/fail end media/{}".format(
                os.listdir(os.path.join("assets/room data/fail end media"))[0])

            self.end_media_player.play(default)
            self.end_media_player.register_event_callback(self.verify_status_of_end_media_player)

    def verify_status_of_end_media_player(self, event):

        event_id = event["event_id"]
        end_of_file_id = 7

        if event_id == end_of_file_id:
            self.end_media_player.quit()
            self.close()

        else:
            pass


class NormalWindow(QMainWindow):

    def __init__(self):
        super(NormalWindow, self).__init__()

        self.screen_width = QApplication.desktop().width()
        self.screen_height = QApplication.desktop().height()

        self.restore_thread_status()

        # threads

        self.game_details_thread = threads.GameDetails()

        # widgets

        self.master_background = QLabel(self)
        self.start_threads_timer = QTimer(self)

        self.master_intro_video_player = mpv.MPV(wid=str(int(self.winId())), vo="x11")
        self.master_video_player = mpv.MPV(wid=str(int(self.winId())), vo="x11")
        self.master_image_viewer = QLabel(self)
        self.master_audio_player = mpv.MPV()

        # variables

        self.general_font = QFont("Ubuntu")

        self.is_game_in_progress = False
        self.is_master_video_playing = False
        self.is_master_audio_playing = False
        self.is_game_status_for_idle_screen_received = False

        # apis

        with open("assets/application data/unique code.json") as unique_code_json_file:
            initial_dictionary_of_unique_code = json.load(unique_code_json_file)

        self.device_id = initial_dictionary_of_unique_code["Device Unique Code"]

        self.game_details_api = "https://deviceapi.cluemaster.io/api/Device/GetGameDetails/{}".format(self.device_id)
        self.game_id = requests.get(self.game_details_api).json()["gameId"]

        self.get_intro_request_api = f"https://deviceapi.cluemaster.io/api/Device/GetGameIntroRequest/{self.game_id}"
        self.room_info_api = "https://deviceapi.cluemaster.io/api/Device/GetRoomInfo/{}".format(self.device_id)

        # methods

        self.showFullScreen()
        self.window_configurations()
        self.frontend()

    def closeEvent(self, event):

        try:
            self.master_overlay_window.close()

        except AttributeError:
            pass

        else:
            pass

    def restore_thread_status(self):

        thread_info_dictionary = {"IsGameDetailsThreadRunning": True, "IsIdentifyDeviceThreadRunning": True,
                                  "IsGameClueThreadRunning": True, "IsTimerRequestThreadRunning": True,
                                  "IsDownloadConfigsThreadRunning": True,
                                  "IsShutdownRestartRequestThreadRunning": True}

        with open("assets/application data/ThreadInfo.json", "w") as thread_file:
            json.dump(thread_info_dictionary, thread_file)

    def window_configurations(self):

        self.resize(self.screen_width, self.screen_height)
        self.full_screen_shortcut = QShortcut(QKeySequence("Ctrl + F11"), self)
        self.full_screen_shortcut.activated.connect(self.go_full_screen)

        self.general_font.setWordSpacing(2)
        self.general_font.setLetterSpacing(QFont.AbsoluteSpacing, 1)

    def go_full_screen(self):

        if self.isFullScreen() is True:
            self.showNormal()
        else:
            self.showFullScreen()

    def frontend(self):

        default = "assets/room data/picture/{}".format(os.listdir(os.path.join("assets/room data/picture/"))[0])

        self.master_background.resize(self.screen_width, self.screen_height)
        self.master_background.setPixmap(QPixmap(default).scaled(self.screen_width, self.screen_height))
        self.setCentralWidget(self.master_background)
        self.master_background.show()

        self.start_threads_timer.setInterval(2000)
        self.start_threads_timer.timeout.connect(self.start_master_thread)
        self.start_threads_timer.start()

    def start_master_thread(self):

        self.game_details_thread.start()
        self.game_details_thread.statusUpdated.connect(self.verify_game_status)
        self.game_details_thread.cluesUsedChanged.connect(self.verify_clues_used)

    def verify_game_status(self, game_status):

        if game_status == 1:
            # start or resume game

            if self.is_game_in_progress is False:
                self.is_game_in_progress = True
                self.load_intro_video()

            else:
                pass

        elif game_status == 2:
            # stop game

            if self.is_game_in_progress is True:
                self.is_game_in_progress = False
                self.stop_game()

            else:
                pass

        elif game_status == 3:

            if self.is_game_status_for_idle_screen_received is False:
                if self.master_background.isVisible() is False:

                    self.is_game_status_for_idle_screen_received = True

                    self.game_details_thread.stop()
                    time.sleep(10)
                    self.deleteLater()

                    self.normal_window = NormalWindow()
                    self.normal_window.show()

                else:
                    pass

            else:
                pass

        elif game_status == 4:
            # pause game
            pass

    def verify_clues_used(self, clues_used):

        pass

    def load_intro_video(self):

        self.master_background.close()

        with open("assets/application data/GameDetails.json") as game_details_json_file:
            initial_dictionary = json.load(game_details_json_file)

        game_details_response = initial_dictionary

        if game_details_response["isIntro"] is True:
            self.master_intro_video_container()
        else:

            self.master_overlay_window = master_overlay.MasterOverlay()
            self.master_overlay_window.show()

            self.master_media_files()

    def master_media_files(self):

        with open("assets/application data/GameDetails.json") as game_details_json_file:
            initial_dictionary = json.load(game_details_json_file)

        game_details_response = initial_dictionary
        room_info_response = requests.get(self.room_info_api).json()

        if game_details_response["isVideo"] is True:
            self.master_background_video_container()

            if game_details_response["isMusic"] is True:
                self.master_background_audio_container()

        elif game_details_response["isMusic"] is True:
            self.master_background_audio_container()

            if room_info_response["isPhoto"] is True:
                self.master_background_image_container()

        elif room_info_response["isPhoto"] is True:
            self.master_background_image_container()

        else:
            # no media files are allowed
            # show only game timer ( countdown or count up )

            self.setStyleSheet("background-color: #191F26;")

    def master_intro_video_container(self):

        default = "assets/room data/intro media/{}".format(os.listdir(os.path.join("assets/room data/intro media/"))[0])

        self.master_intro_video_player.fullscreen = True
        self.master_intro_video_player.play(default)
        self.master_intro_video_player.register_event_callback(self.verify_status_of_intro_video_player)

    def verify_status_of_intro_video_player(self, event):

        event_id = event["event_id"]
        end_of_file_event_id = 7

        if event_id == end_of_file_event_id:

            self.master_intro_video_player.quit()

            # send post response to start timer in web app

            response_of_intro_request_api = requests.get(self.get_intro_request_api).json()
            device_request_id = response_of_intro_request_api["DeviceRequestid"]
            requests.post(f"https://deviceapi.cluemaster.io/api/Device/{self.device_id}/{device_request_id}")

            # startup media files

            self.master_media_files()

        else:
            pass

    def master_background_video_container(self):

        default = "assets/room data/video/{}".format(os.listdir(os.path.join("assets/room data/video/"))[0])

        self.master_video_player.loop = True
        self.master_video_player.fullscreen = True
        self.master_video_player.play(default)

        self.is_master_video_playing = True

    def master_background_image_container(self):

        default = "assets/room data/picture/{}".format(os.listdir(os.path.join("assets/room data/picture/"))[0])

        self.master_image_viewer.resize(self.screen_width, self.screen_height)
        self.master_image_viewer.setPixmap(QPixmap(default).scaled(self.screen_width, self.screen_height))
        self.setCentralWidget(self.master_image_viewer)
        self.master_image_viewer.show()

    def master_background_audio_container(self):

        default = "assets/room data/music/{}".format(os.listdir(os.path.join("assets/room data/music/"))[0])

        self.master_audio_player.play(default)
        self.master_audio_player.loop = True

        self.is_master_audio_playing = True

    def stop_game(self):

        if self.is_master_video_playing is True:
            self.master_video_player._set_property("pause", True)

        if self.is_master_audio_playing is True:
            self.master_audio_player._set_property("pause", True)

        # stop/pause application countdown timers

        game_details_response = requests.get(self.game_details_api).json()
        win_loss_text = game_details_response["winLossText"]

        if win_loss_text == "won":
            self.master_end_media_container(status="won")

        elif win_loss_text == "lost":
            self.master_end_media_container(status="lost")

    def master_end_media_container(self, status):

        if status == "won":

            self.custom_end_media_widget = EndMediaWidget("won")
            self.custom_end_media_widget.show()

        elif status == "lost":

            self.custom_end_media_widget = EndMediaWidget("lost")
            self.custom_end_media_widget.show()
