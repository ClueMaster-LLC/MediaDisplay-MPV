import os
import random
import time

import requests
import json
import simplejson
import shutil
import platform_facts
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication, QShortcut
from PyQt5.QtGui import QFont, QMovie, QKeySequence
from PyQt5.QtCore import Qt, QThread, pyqtSignal

ROOT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))


class LoadingBackend(QThread):
    proceed = pyqtSignal(bool)

    def __init__(self):
        super(LoadingBackend, self).__init__()

        self.is_killed = False

    def run(self):
        time.sleep(15)
        try:
            with open(os.path.join(ROOT_DIRECTORY, "assets/application data", "unique code.json"), "r") as file:
                json_object = json.load(file)

            device_unique_code = json_object["Device Unique Code"]

            room_info_api = f"https://deviceapi.cluemaster.io/api/Device/GetRoomInfo/{device_unique_code}"
            download_files_request_api = f"https://deviceapi.cluemaster.io/api/Device/DownloadFilesRequest/{device_unique_code}"

            while self.is_killed is False:
                print("loading screen")
                if requests.get(room_info_api).content.decode("utf-8") != "No Configurations Files Found":

                    main_folder = "assets/room data"
                    main_room_data_directory = os.path.join(ROOT_DIRECTORY, main_folder)
                    room_data_music_subfolder = os.path.join(ROOT_DIRECTORY, main_folder, "music")
                    room_data_picture_subfolder = os.path.join(ROOT_DIRECTORY, main_folder, "picture")
                    room_data_video_subfolder = os.path.join(ROOT_DIRECTORY, main_folder, "video")
                    room_data_intro_media_subfolder = os.path.join(ROOT_DIRECTORY, main_folder, "intro media")
                    room_data_fail_end_media_subfolder = os.path.join(ROOT_DIRECTORY, main_folder, "fail end media")
                    room_data_success_end_media_subfolder = os.path.join(ROOT_DIRECTORY, main_folder,
                                                                         "success end media")
                    main_clue_media_file_directory = os.path.join(ROOT_DIRECTORY, "assets", "clue medias")

                    response_of_room_info_api = requests.get(room_info_api).json()

                    music_file_url = response_of_room_info_api["MusicPath"]
                    picture_file_url = response_of_room_info_api["PhotoPath"]
                    video_file_url = response_of_room_info_api["VideoPath"]
                    intro_video_file_url = response_of_room_info_api["IntroVideoPath"]
                    end_success_file_url = response_of_room_info_api["SuccessVideoPath"]
                    end_fail_file_url = response_of_room_info_api["FailVideoPath"]

                    if os.path.isdir("assets/room data") is False:
                        os.mkdir("assets/room data")

                    if os.path.isdir("assets/clue medias") is False:
                        shutil.rmtree("assets/clue medias", ignore_errors=True)
                        os.mkdir("assets/clue medias")

                    if os.path.isdir("assets/room data/music") is False:
                        os.mkdir("assets/room data/music")

                    if os.path.isdir("assets/room data/picture") is False:
                        os.mkdir("assets/room data/picture")

                    if os.path.isdir("assets/room data/video") is False:
                        os.mkdir("assets/room data/video")

                    if os.path.isdir("assets/room data/intro media") is False:
                        os.mkdir("assets/room data/intro media")

                    if os.path.isdir("assets/room data/success end media") is False:
                        os.mkdir("assets/room data/success end media")

                    if os.path.isdir("assets/room data/fail end media") is False:
                        os.mkdir("assets/room data/fail end media")

                    # music directory
                    if music_file_url is not None:
                        file_name = music_file_url.split("/")[5]
                        file_location = os.path.join(room_data_music_subfolder, file_name)

                        if os.path.isfile(file_location) is False:
                            shutil.rmtree("assets/room data/music", ignore_errors=True)
                            os.mkdir("assets/room data/music")

                            file_bytes = requests.get(music_file_url).content
                            with open(os.path.join(room_data_music_subfolder, file_name), "wb") as file:
                                file.write(file_bytes)

                    # picture directory
                    if picture_file_url is not None:
                        file_name = picture_file_url.split("/")[5]
                        file_location = os.path.join(room_data_picture_subfolder, file_name)

                        if os.path.isfile(file_location) is False:
                            shutil.rmtree("assets/room data/picture", ignore_errors=True)
                            os.mkdir("assets/room data/picture")

                            file_bytes = requests.get(picture_file_url).content
                            with open(os.path.join(room_data_picture_subfolder, file_name), "wb") as file:
                                file.write(file_bytes)

                    # video directory
                    if video_file_url is not None:
                        file_name = video_file_url.split("/")[5]
                        file_location = os.path.join(room_data_video_subfolder, file_name)

                        if os.path.isfile(file_location) is False:
                            shutil.rmtree("assets/room data/video", ignore_errors=True)
                            os.mkdir("assets/room data/video")

                            file_bytes = requests.get(video_file_url).content
                            with open(os.path.join(room_data_video_subfolder, file_name), "wb") as file:
                                file.write(file_bytes)

                    # intro media directory
                    if intro_video_file_url is not None:
                        file_name = intro_video_file_url.split("/")[5]
                        file_location = os.path.join(room_data_intro_media_subfolder, file_name)

                        if os.path.isfile(file_location) is False:
                            shutil.rmtree("assets/room data/intro media", ignore_errors=True)
                            os.mkdir("assets/room data/intro media")

                            file_bytes = requests.get(intro_video_file_url).content
                            with open(os.path.join(room_data_intro_media_subfolder, file_name), "wb") as file:
                                file.write(file_bytes)

                    # end media directory
                    if end_success_file_url is not None:
                        file_name = end_success_file_url.split("/")[5]
                        file_location = os.path.join(room_data_success_end_media_subfolder, file_name)

                        if os.path.isfile(file_location) is False:
                            shutil.rmtree("assets/room data/success end media", ignore_errors=True)
                            os.mkdir("assets/room data/success end media")

                            file_bytes = requests.get(end_success_file_url).content
                            with open(os.path.join(room_data_success_end_media_subfolder, file_name), "wb") as file:
                                file.write(file_bytes)

                    # end media directory
                    if end_fail_file_url is not None:
                        file_name = end_fail_file_url.split("/")[5]
                        file_location = os.path.join(room_data_fail_end_media_subfolder, file_name)

                        if os.path.isfile(file_location) is False:
                            shutil.rmtree("assets/room data/fail end media", ignore_errors=True)
                            os.mkdir("assets/room data/fail end media")

                            file_bytes = requests.get(end_fail_file_url).content
                            with open(os.path.join(room_data_fail_end_media_subfolder, file_name), "wb") as file:
                                file.write(file_bytes)

                    # clue medias
                    index = 0

                    while index <= len(requests.get(room_info_api).json()["ClueMediaFiles"]) - 1:
                        url = requests.get(room_info_api).json()["ClueMediaFiles"][index]["FilePath"]

                        if url is not None:
                            file_name = url.split("/")[5]
                            file_location = os.path.join(main_clue_media_file_directory, file_name)

                            if os.path.isfile(file_location) is False:
                                clue_media_content = requests.get(url).content
                                with open(os.path.join(main_clue_media_file_directory, file_name), "wb") as file:
                                    file.write(clue_media_content)

                            index += int(1)
                            continue

                        else:
                            index += int(1)

                    try:
                        response_of_download_files_request = requests.get(download_files_request_api).json()
                        device_request_id = response_of_download_files_request["DeviceRequestid"]
                        device_key = response_of_download_files_request["DeviceKey"]
                        requests.post(f"https://deviceapi.cluemaster.io/api/Device/{device_key}/{device_request_id}")

                    except json.decoder.JSONDecodeError:
                        pass

                    except simplejson.errors.JSONDecodeError:
                        pass

                    except requests.exceptions.ConnectionError:
                        pass

                    except KeyError:
                        pass

                    else:
                        pass

                    thread_info_dictionary = {"IsGameDetailsThreadRunning": True, "IsIdentifyDeviceThreadRunning": True,
                                              "IsGameClueThreadRunning": True, "IsTimerRequestThreadRunning": True,
                                              "IsDownloadConfigsThreadRunning": True,
                                              "IsShutdownRestartRequestThreadRunning": True}

                    with open("assets/application data/ThreadInfo.json", "w") as thread_file:
                        json.dump(thread_info_dictionary, thread_file)

                    data = {"Room Minimum Players": response_of_room_info_api["RoomMinPlayers"],
                            "Room Maximum Players": response_of_room_info_api["RoomMaxPlayers"],
                            "Clues Allowed": response_of_room_info_api["CluesAllowed"],
                            "Clue Size On Screen": response_of_room_info_api["ClueSizeOnScreen"],
                            "Maximum Number Of Clues": response_of_room_info_api["MaxNoOfClues"],
                            "Clue Position Vertical": response_of_room_info_api["CluePositionVertical"],
                            "IsTimeLimit": response_of_room_info_api["IsTimeLimit"],
                            "Time Limit": response_of_room_info_api["TimeLimit"],
                            "Time Override": response_of_room_info_api["TimeOverride"]}

                    with open(os.path.join(ROOT_DIRECTORY, "assets/application data", "device configurations.json"), "w") as file:
                        json.dump(data, file)

                    self.proceed.emit(True)
                    self.stop()

                else:
                    print("Room Info Blank")

        except simplejson.errors.JSONDecodeError:
            pass

        except requests.exceptions.ConnectionError:
            pass

        except json.decoder.JSONDecodeError:
            pass

    def stop(self):

        self.is_killed = True
        self.run()


class LoadingScreen(QWidget):

    def __init__(self):
        super().__init__()
        self.screen_width = QApplication.desktop().width()
        self.screen_height = QApplication.desktop().height()
        self.font = QFont("Ubuntu", 21)

        self.showFullScreen()
        self.window_config()
        self.frontend()

    def window_config(self):

        self.move(0, 0)
        self.setMinimumSize(self.screen_width, self.screen_height)

        fullScreen_ShortCut = QShortcut(QKeySequence("F11"), self)
        fullScreen_ShortCut.activated.connect(self.go_fullScreen)

        self.font.setWordSpacing(2)
        self.font.setLetterSpacing(QFont.AbsoluteSpacing, 1)
        self.setStyleSheet("background-color: #191F26;")
        self.setCursor(Qt.BlankCursor)

    def go_fullScreen(self):

        if self.isFullScreen() is True:
            self.showMaximized()
            self.setCursor(Qt.ArrowCursor)
        else:
            self.setCursor(Qt.BlankCursor)
            self.showFullScreen()

    def frontend(self):

        self.main_layout = QVBoxLayout()

        gif = QMovie("assets/icons/loading_beaker.gif")
        gif.start()

        loading_gif = QLabel(self)
        loading_gif.setAlignment(Qt.AlignHCenter)
        loading_gif.setMovie(gif)

        did_you_know = QLabel(self)
        did_you_know.setAlignment(Qt.AlignHCenter)
        did_you_know.setStyleSheet("color: #fff; font-weight:bold;")
        did_you_know.setFont(QFont("Ubuntu", 30))

        fact = random.choice(platform_facts.facts)
        did_you_know.setText(str(fact))

        self.main_layout.addStretch()
        self.main_layout.addWidget(loading_gif)
        self.main_layout.addStretch()
        self.main_layout.addWidget(did_you_know)
        self.main_layout.addSpacing(120)

        self.setLayout(self.main_layout)

        self.connect_backend_thread()

    def connect_backend_thread(self):

        self.loading_thread = LoadingBackend()
        self.loading_thread.start()
        self.loading_thread.proceed.connect(self.switch_window)

    def switch_window(self, response):

        if response is True:

            import normal_screen
            self.window = normal_screen.NormalWindow()
            self.window.show()
            self.loading_thread.disconnect()
            self.loading_thread.quit()
            self.close()
            self.deleteLater()

        else:
            pass
