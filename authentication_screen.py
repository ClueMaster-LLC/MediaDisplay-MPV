import time
import os
import shutil
import json
import requests
import simplejson.errors
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QMovie, QKeySequence
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QShortcut

ROOT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))


class AuthenticationBackend(QThread):
    proceed = pyqtSignal(bool)

    def __init__(self):
        super(AuthenticationBackend, self).__init__()

        self.is_killed = False

    def run(self):
        print("authentication")
        try:
            with open(os.path.join(ROOT_DIRECTORY, "assets/application data", "unique code.json"), "r") as file:
                json_object = json.load(file)

            device_unique_code = json_object["Device Unique Code"]

            room_info_api = f"https://deviceapi.cluemaster.io/api/Device/GetRoomInfo/{device_unique_code}"
            device_request_url = f"https://deviceapi.cluemaster.io/api/Device/GetDeviceRequest/{device_unique_code}"

            while self.is_killed is False:
                if requests.get(room_info_api).content.decode("utf-8") == "No Device Found":
                    time.sleep(2)
                    continue

                else:
                    while not requests.get(device_request_url).content.decode("utf") == "No record found":

                        deviceRequestId = requests.get(device_request_url).json()["DeviceRequestid"]
                        requestId = requests.get(device_request_url).json()["RequestID"]
                        deviceConfigurationId = 6

                        if requestId != deviceConfigurationId:
                            identify_device_url = f"https://deviceapi.cluemaster.io/api/Device/{device_unique_code}/{deviceRequestId} "
                            requests.post(identify_device_url)
                            continue

                        else:

                            if requests.get(room_info_api).content.decode("utf-8") != "No Configurations Files Found":
                                main_folder = "assets/room data"
                                main_room_data_directory = os.path.join(ROOT_DIRECTORY, main_folder)
                                room_data_music_subfolder = os.path.join(ROOT_DIRECTORY, main_folder, "music")
                                room_data_picture_subfolder = os.path.join(ROOT_DIRECTORY, main_folder, "picture")
                                room_data_video_subfolder = os.path.join(ROOT_DIRECTORY, main_folder, "video")
                                room_data_intro_media_subfolder = os.path.join(ROOT_DIRECTORY, main_folder, "intro media")
                                room_data_fail_end_media_subfolder = os.path.join(ROOT_DIRECTORY, main_folder, "fail end media")
                                room_data_success_end_media_subfolder = os.path.join(ROOT_DIRECTORY, main_folder, "success end media")
                                main_clue_media_file_directory = os.path.join(ROOT_DIRECTORY, "assets", "clue medias")

                                if os.path.isdir(main_room_data_directory):
                                    shutil.rmtree(main_room_data_directory, ignore_errors=True)

                                if os.path.isdir(main_clue_media_file_directory):
                                    shutil.rmtree(main_clue_media_file_directory, ignore_errors=True)

                                os.mkdir(main_room_data_directory)
                                os.mkdir(main_clue_media_file_directory)
                                os.mkdir(room_data_music_subfolder)
                                os.mkdir(room_data_picture_subfolder)
                                os.mkdir(room_data_video_subfolder)
                                os.mkdir(room_data_intro_media_subfolder)
                                os.mkdir(room_data_fail_end_media_subfolder)
                                os.mkdir(room_data_success_end_media_subfolder)

                                response_of_room_info_api = requests.get(room_info_api).json()

                                music_file_url = response_of_room_info_api["MusicPath"]
                                picture_file_url = response_of_room_info_api["PhotoPath"]
                                video_file_url = response_of_room_info_api["VideoPath"]
                                intro_video_file_url = response_of_room_info_api["IntroVideoPath"]
                                end_success_file_url = response_of_room_info_api["SuccessVideoPath"]
                                end_fail_file_url = response_of_room_info_api["FailVideoPath"]

                                # music directory
                                if music_file_url is not None:
                                    music_file = requests.get(music_file_url).content
                                    file_name = music_file_url.split("/")[5]
                                    with open(os.path.join(room_data_music_subfolder, file_name), "wb") as file:
                                        file.write(music_file)

                                # picture directory
                                if picture_file_url is not None:
                                    picture_file = requests.get(picture_file_url).content
                                    file_name = picture_file_url.split("/")[5]
                                    with open(os.path.join(room_data_picture_subfolder, file_name), "wb") as file:
                                        file.write(picture_file)

                                # video directory
                                if video_file_url is not None:
                                    video_file = requests.get(video_file_url).content
                                    file_name = video_file_url.split("/")[5]
                                    with open(os.path.join(room_data_video_subfolder, file_name), "wb") as file:
                                        file.write(video_file)

                                # intro media directory
                                if intro_video_file_url is not None:
                                    intro_video_file = requests.get(intro_video_file_url).content
                                    file_name = intro_video_file_url.split("/")[5]
                                    with open(os.path.join(room_data_intro_media_subfolder, file_name), "wb") as file:
                                        file.write(intro_video_file)

                                # end media directory
                                if end_success_file_url is not None:
                                    end_success_file = requests.get(end_success_file_url).content
                                    file_name = end_success_file_url.split("/")[5]
                                    with open(os.path.join(room_data_success_end_media_subfolder, file_name), "wb") as file:
                                        file.write(end_success_file)

                                # end media directory
                                if end_fail_file_url is not None:
                                    end_fail_file = requests.get(end_fail_file_url).content
                                    file_name = end_fail_file_url.split("/")[5]
                                    with open(os.path.join(room_data_fail_end_media_subfolder, file_name), "wb") as file:
                                        file.write(end_fail_file)

                                # clue medias
                                index = 0

                                while index <= len(response_of_room_info_api["ClueMediaFiles"]) - 1:
                                    url = response_of_room_info_api["ClueMediaFiles"][index]["FilePath"]

                                    if url is not None:
                                        clue_media_content = requests.get(url).content
                                        file_name = url.split("/")[5]
                                        with open(os.path.join(main_clue_media_file_directory, file_name), "wb") as file:
                                            file.write(clue_media_content)

                                        index += int(1)
                                        continue

                                    else:
                                        index += int(1)

                                identify_device_url = f"https://deviceapi.cluemaster.io/api/Device/{device_unique_code}/{deviceRequestId}"
                                requests.post(identify_device_url)
                                continue

                            else:
                                identify_device_url = f"https://deviceapi.cluemaster.io/api/Device/{device_unique_code}/{deviceRequestId}"
                                requests.post(identify_device_url)
                                continue
                    else:

                        if requests.get(room_info_api).content.decode("utf-8") != "No Configurations Files Found":
                            json_data_of_configuration_files = requests.get(room_info_api).json()

                            data = {"Room Minimum Players": json_data_of_configuration_files["RoomMinPlayers"],
                                    "Room Maximum Players": json_data_of_configuration_files["RoomMaxPlayers"],
                                    "Clues Allowed": json_data_of_configuration_files["CluesAllowed"],
                                    "Clue Size On Screen": json_data_of_configuration_files["ClueSizeOnScreen"],
                                    "Maximum Number Of Clues": json_data_of_configuration_files["MaxNoOfClues"],
                                    "Clue Position Vertical": json_data_of_configuration_files["CluePositionVertical"],
                                    "IsTimeLimit": json_data_of_configuration_files["IsTimeLimit"],
                                    "Time Limit": json_data_of_configuration_files["TimeLimit"],
                                    "Time Override": json_data_of_configuration_files["TimeOverride"]}

                            with open(os.path.join(ROOT_DIRECTORY, "assets/application data", "device configurations.json"), "w") as file:
                                json.dump(data, file)

                        self.proceed.emit(True)
                        self.stop()

        except simplejson.errors.JSONDecodeError:
            pass

        except requests.exceptions.ConnectionError:
            pass

        except json.decoder.JSONDecodeError:
            pass

    def stop(self):

        self.is_killed = True
        self.run()


class AuthenticationWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.screen_width = QApplication.desktop().width()
        self.screen_height = QApplication.desktop().height()
        self.font = QFont("Ubuntu", 20)
        self.custom_font_for_unique_code = QFont("Ubuntu", 40)

        # methods
        self.showFullScreen()
        self.load_unique_id()
        self.window_config()
        self.frontend()

    def load_unique_id(self):

        with open(os.path.join(ROOT_DIRECTORY, "assets/application data", "unique code.json"), "r") as file:
            json_object = json.load(file)

        device_unique_code = json_object["Device Unique Code"]

        self.get_mac = device_unique_code

    def window_config(self):

        self.move(0, 0)
        self.setMinimumSize(self.screen_width, self.screen_height)

        fullScreen_shortCut = QShortcut(QKeySequence("F11"), self)
        fullScreen_shortCut.activated.connect(self.go_fullScreen)

        self.font.setWordSpacing(2)
        self.font.setLetterSpacing(QFont.AbsoluteSpacing, 1)

        self.custom_font_for_unique_code.setWordSpacing(110)
        self.custom_font_for_unique_code.setLetterSpacing(QFont.AbsoluteSpacing, 4)

        self.setStyleSheet("background-color: #191F26;")
        self.setCursor(Qt.BlankCursor)

    def go_fullScreen(self):

        if self.isFullScreen() is True:
            self.showNormal()
            self.setCursor(Qt.ArrowCursor)
        else:
            self.setCursor(Qt.BlankCursor)
            self.showFullScreen()

    def frontend(self):

        self.main_layout = QVBoxLayout()

        alpha_label = QLabel(self)
        alpha_label.setText("ClueMaster TV Display Timer")
        alpha_label.setAlignment(Qt.AlignHCenter)
        alpha_label.setFont(QFont("Ubuntu", 30))
        alpha_label.setStyleSheet("color: #ffffff; font-weight:bold;")

        device_key_label = QLabel(self)
        device_key_label.setFont(QFont("Ubuntu", 50))
        device_key_label.setAlignment(Qt.AlignHCenter)
        device_key_label.setText("DEVICE KEY")
        device_key_label.setStyleSheet("color: #ffffff; font-weight:bold;")

        device_code = QLabel(self)
        device_code.setText(self.get_mac)
        device_code.setAlignment(Qt.AlignHCenter)
        device_code.setFont(QFont("Ubuntu", 60))
        device_code.setStyleSheet("color: #4e71cf; font-weight:bold;")

        loading_gif = QMovie("assets/icons/security_loading.gif")
        loading_gif.start()

        loading_label = QLabel(self)
        loading_label.setAlignment(Qt.AlignHCenter)
        loading_label.setMovie(loading_gif)
        loading_label.setStyleSheet("background-color: #191F26;")
        loading_label.show()

        self.main_layout.addStretch()
        self.main_layout.addWidget(alpha_label)
        self.main_layout.addSpacing(40)
        self.main_layout.addWidget(device_key_label)
        self.main_layout.addSpacing(90)
        self.main_layout.addWidget(device_code)
        self.main_layout.addStretch()
        self.main_layout.addWidget(loading_label)
        self.setLayout(self.main_layout)

        self.connect_backend_thread()

    def connect_backend_thread(self):

        self.authentication_thread = AuthenticationBackend()
        self.authentication_thread.start()
        self.authentication_thread.proceed.connect(self.switch_window)

    def switch_window(self, proceed):

        if proceed is True:
            import loading_screen
            self.window = loading_screen.LoadingScreen()
            self.window.show()
            self.deleteLater()

        else:
            pass
