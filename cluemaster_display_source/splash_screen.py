import os
import json
import uuid
import re
import random
import time
import requests
import socket
import threads
from apis import *
from string import Template
from requests.structures import CaseInsensitiveDict
from PyQt5.QtCore import QThread, Qt, pyqtSignal
from PyQt5.QtGui import QFont, QMovie, QIcon
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QDesktopWidget

# Setting up the base directories
ROOT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
MASTER_DIRECTORY = os.path.join(os.environ.get("HOME"), "CluemasterDisplay")

snap_version = os.environ.get("SNAP_VERSION")


class SplashBackend(QThread):
    skip_authentication = pyqtSignal()
    register_device = pyqtSignal(str)

    def __init__(self):
        super(SplashBackend, self).__init__()

        # default variables
        self.is_killed = False
        self.unique_code_file = os.path.join(MASTER_DIRECTORY, "assets/application data/unique_code.json")
        self.platform_specs_file = os.path.join(MASTER_DIRECTORY, "assets/application data/platform_specs.json")

    def run(self):
        """ this is an autorun method that is triggered as soon as the thread is started, this method holds all the
            codes for every work, the thread does"""

        time.sleep(2)
        print(">>> splash_screen - Splash Screen Backend Starting")

        if os.path.isdir(os.path.join(MASTER_DIRECTORY, "assets/application data")) is False:
            # if there is no directory named application data inside the assets directory, then create one
            os.makedirs(os.path.join(MASTER_DIRECTORY, "assets/application data"))
        else:
            # if the directory already exists, then pass
            pass

        if os.path.isfile(self.platform_specs_file):
            pass
        else:
            try:
                with open("/proc/cpuinfo") as master_cpu_info_file:
                    file_data = master_cpu_info_file.read()

                    if "hypervisor" in file_data:
                        dictionary = {"platform": "VirtualMachine", "mpv_configurations": {"vo": "x11"}}
                    elif "Intel" in file_data:
                        dictionary = {"platform": "Intel", "mpv_configurations": {"hwdec": "vaapi", "vo": "gpu"}}
                    elif "AMD" in file_data:
                        dictionary = {"platform": "AMD", "mpv_configurations": {"hwdec": "vaapi", "vo": "gpu"}}
                    else:
                        dictionary = {"platform": "Unspecified"}

                    with open(os.path.join(MASTER_DIRECTORY, "assets/application data/platform_specs.json"), "w") as specs_file:
                        json.dump(dictionary, specs_file)
                        print(f">>> Platform Spec File Created: {specs_file}")
            except Exception as error:
                print(f">>> Error trying to create platform info file: {error}")

        if os.path.isfile(self.unique_code_file):
            # checking if the unique code.json file exists in the application data directory, if yes then get the unique
            # device id and check if there are any device files for it

            with open(self.unique_code_file) as unique_code_json_file:
                json_object_of_unique_code_file = json.load(unique_code_json_file)

            # Load file to in memory variable to be used and not hit the HDD every few seconds.
            threads.UNIQUE_CODE = json_object_of_unique_code_file

            device_unique_code = threads.UNIQUE_CODE["Device Unique Code"]
            api_key = threads.UNIQUE_CODE["apiKey"]
            device_files_url = DEVICES_FILES_API.format(device_unique_code=device_unique_code)

            while self.is_killed is False:
                try:
                    headers = CaseInsensitiveDict()
                    headers["Authorization"] = f"Basic {device_unique_code}:{api_key}"

                    api_check_response = requests.get(device_files_url, headers=headers)
                    new_api_key = None
                    if api_check_response.status_code == 401:
                        # if response is 401 from the GetDeviceFiles api then, register the device
                        # GetDeviceFiles api is being used in this case to also check if the device exists or not
                        # along with the authenticity of the api bearer key

                        print("401 Error. Getting New Token")
                        new_api_key = self.generate_secure_api_key(device_id=device_unique_code)
                        threads.UNIQUE_CODE["apiKey"] = new_api_key

                        self.register_device.emit(new_api_key)

                    else:
                        self.skip_authentication.emit()

                except requests.exceptions.ConnectionError:
                    # if api call is facing connection error, wait for 2 seconds and then retry
                    time.sleep(2)
                    continue

                else:
                    break

        else:
            """ if there is no unique code.json file then generate an unique device id and secure api key and then save
            them to unique code.json file and register device"""

            ## This is not needed at all here. Moved above to look for file and create if missing.
            # with open("/proc/cpuinfo") as master_cpu_info_file:
            #     file_data = master_cpu_info_file.read()
            #
            #     if "hypervisor" in file_data:
            #         dictionary = {"platform": "VirtualMachine", "mpv_configurations": {"vo": "x11"}}
            #     elif "Intel" in file_data:
            #         dictionary = {"platform": "Intel", "mpv_configurations": {"hwdec": "auto", "vo": "gpu", "gpu_context": "auto"}}
            #     elif "AMD" in file_data:
            #         dictionary = {"platform": "AMD", "mpv_configurations": {"hwdec": "auto", "vo": "gpu", "gpu_context": "auto"}}
            #     else:
            #         dictionary = {"platform": "Unspecified"}
            #
            #     with open(os.path.join(MASTER_DIRECTORY, "assets/application data/platform_specs.json"), "w") as specs_file:
            #         json.dump(dictionary, specs_file)
            #
            ## this should not be here at all!
            #     threads.UNIQUE_CODE = dictionary

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
            api_key = self.generate_secure_api_key(device_id=full_unique_code)
            ipv4_address = self.fetch_device_ipv4_address()

            json_object = {"Device Unique Code": full_unique_code, "apiKey": api_key, "IPv4 Address": ipv4_address}
            with open(self.unique_code_file, "w") as file:
                json.dump(json_object, file)

            threads.UNIQUE_CODE = json_object

            self.register_device.emit(api_key)

    # def update_device_details(self):
    #         # Get IP Address to display on Screen and report back to API
    #         ipv4_address = self.fetch_device_ipv4_address()
    #         threads.UNIQUE_CODE["IPv4 Address"] = ipv4_address
    #         api_key = threads.UNIQUE_CODE["apiKey"]
    #         device_unique_code = threads.UNIQUE_CODE["Device Unique Code"]
    #
    #         # Try to post the Device IP and SNAP Version back to the API to store on Device Master Table
    #         try:
    #             headers = CaseInsensitiveDict()
    #             headers["Authorization"] = f"Basic {device_unique_code}:{api_key}"
    #             post_device_details_api_url = POST_DEVICE_DETAILS_UPDATE_API.format(device_id=device_unique_code,
    #                                                                                 device_ip=ipv4_address,
    #                                                                                 snap_version=snap_version)
    #             print(f"POST: {post_device_details_api_url}")
    #             print(f"API KEY: {api_key}")
    #             response = requests.post(url=post_device_details_api_url, headers=headers)
    #             if response.status_code != 200:
    #                 print(f">>>> splash_screen - ERROR SENDING DEVICE DETAILS: {response.status_code} / "
    #                       f"{response.content} / {response.json()}")
    #
    #             else:
    #                 print(f">>> splash_screen - {device_unique_code} - Device Details Updated: {time.ctime()} : "
    #                       f"{post_device_details_api_url}")
    #
    #         except requests.exceptions.HTTPError as request_error:
    #             if "401 Client Error" in str(request_error):
    #                 time.sleep(1)
    #                 pass
    #             else:
    #                 print(f">>> splash_screen - {device_unique_code} - ERROR - HTTP: {request_error}")
    #                 time.sleep(1)
    #                 pass
    #         except Exception as other_errors:
    #             print(f">>> splash_screen - {device_unique_code} - ERROR - API: {other_errors}")
    #             time.sleep(1)
    #             pass

    def generate_secure_api_key(self, device_id):
        """ this method takes the device_id and then generates a secure api key for it"""

        while True:
            try:
                authentication_api_url = GENERATE_API_TOKEN_API
                device_id = device_id

                headers = CaseInsensitiveDict()
                headers["Content-Type"] = "application/json"

                initial_template = Template(
                    """
                    {
                    "DeviceKey": "${device_key}",
                    "Username": "ClueMasterAPI",
                    "Password": "8BGIJh27uBtqBTb2%t*zho!z0nS62tq2pGN%24&5PS3D"
                    }
                    """)
                data = initial_template.substitute(device_key=device_id)

                response = requests.post(url=authentication_api_url, headers=headers, data=data)
                if response.status_code != 200:
                    print(f">>> Error trying to create bearer key with status {response.status_code} - {response.content}")
                    time.sleep(3)
                else:
                    print(">>> Console output - API Auth status - ", response.json()["status"])
                    return response.json()["apiKey"]

                    # print(">>> Console output - Verifying new bearer key ")
                    #
                    # api_key = response.json()["apiKey"]
                    # headers = CaseInsensitiveDict()
                    # headers["Authorization"] = f"Basic {device_id}:{api_key}"
                    #
                    # response = requests.get(GENERAL_REQUEST_API, headers=headers)
                    # if response.status_code == 200:
                    #     pass
                    # else:
                    #     time.sleep(3)

            except KeyError:
                time.sleep(3)
                pass

            except requests.exceptions.ConnectionError:
                time.sleep(3)
                pass

    @staticmethod
    def fetch_device_ipv4_address():
        i_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            i_socket.connect(('10.255.255.255', 1))
            ip_address = i_socket.getsockname()[0]
        except Exception:
            ip_address = "127.0.0.1"
        finally:
            i_socket.close()
            print(">>> Console output - Gateway IP Address: " + ip_address)
        return ip_address

    def stop(self):
        """ this method stops the thread by setting the is_killed attribute to False and then calling the run() methods
            which when validated with a while loop turns False and thus breaks"""

        self.is_killed = True
        self.run()


class SplashWindow(QWidget):
    def __init__(self):
        super().__init__()

        # default variables
        self.screen_width = QApplication.desktop().width()
        self.screen_height = QApplication.desktop().height()
        self.ipv4_address = self.fetch_device_ipv4_address()

        # widgets
        self.font = QFont("IBM Plex Mono", 19)

        # instance methods
        self.window_config()
        self.update_thread_info_file()
        self.frontend()

    @staticmethod
    def fetch_device_ipv4_address():
        i_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            i_socket.connect(('10.255.255.255', 1))
            ip_address = i_socket.getsockname()[0]
        except Exception:
            ip_address = "127.0.0.1"
        finally:
            i_socket.close()
            print(">>> Console output - Gateway IP Address: " + ip_address)
        return ip_address

    def window_config(self):
        """ this method contains code for the configurations of the window"""

        self.font.setWordSpacing(2)
        self.font.setLetterSpacing(QFont.AbsoluteSpacing, 1)

        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        self.setFixedHeight(int(self.screen_height // 2.5))
        self.setFixedWidth(int(self.screen_width // 2.75))
        self.setWindowIcon(QIcon("assets/icons/app_icon.png"))
        self.setWindowFlag(Qt.FramelessWindowHint)

        self.setStyleSheet("""
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&display=swap');
        """)
        self.setStyleSheet("background-color:#191F26; color:white;")

    def update_thread_info_file(self):
        if os.path.isdir(os.path.join(MASTER_DIRECTORY, "assets/application data")):
            print("Configuration Directories Exists")
            thread_info_dictionary = {"IsGameDetailsThreadRunning": False, "IsIdentifyDeviceThreadRunning": False,
                                      "IsGameClueThreadRunning": False, "IsTimerRequestThreadRunning": False,
                                      "IsDownloadConfigsThreadRunning": False, "IsUpdateRoomInfoThreadRunning": False,
                                      "IsShutdownRestartRequestThreadRunning": False, "ResettingGame": False}

            # with open(os.path.join(MASTER_DIRECTORY, "assets/application data/ThreadInfo.json"), "w") as thread_file:
            #     json.dump(thread_info_dictionary, thread_file)

            threads.THREAD_INFO = thread_info_dictionary

        else:
            print("Creating Configuration Directories")
            os.makedirs(os.path.join(MASTER_DIRECTORY, "assets/application data"))
            thread_info_dictionary = {"IsGameDetailsThreadRunning": False, "IsIdentifyDeviceThreadRunning": False,
                                      "IsGameClueThreadRunning": False, "IsTimerRequestThreadRunning": False,
                                      "IsDownloadConfigsThreadRunning": False, "IsUpdateRoomInfoThreadRunning": False,
                                      "IsShutdownRestartRequestThreadRunning": False, "ResettingGame": False}

            # with open(os.path.join(MASTER_DIRECTORY, "assets/application data/ThreadInfo.json"), "w") as thread_file:
            #     json.dump(thread_info_dictionary, thread_file)

            threads.THREAD_INFO = thread_info_dictionary

    def frontend(self):
        """ this methods holds the codes for the different labels and animations"""

        self.main_layout = QVBoxLayout()

        application_name = QLabel(self)
        application_name.setFont(self.font)
        application_name.setText("ClueMaster TV Display Timer")
        application_name.setStyleSheet("color: white; font-weight: 700;")

        version = QLabel(self)
        version.setText(f"Version : {snap_version}")
        version.setFont(self.font)
        version.setStyleSheet("color: white; font-size: 19px; font-weight:bold;")

        local_ipv4_address = QLabel(self)
        local_ipv4_address.setFont(self.font)
        local_ipv4_address.setStyleSheet("color: white; font-size: 19px; font-weight:bold;")
        local_ipv4_address.setText("Local IP : " + self.ipv4_address)

        gif = QMovie(os.path.join(ROOT_DIRECTORY, "assets/icons/security_loading.gif"))
        gif.start()

        loading_gif = QLabel(self)
        loading_gif.setMovie(gif)
        loading_gif.show()

        self.main_layout.addSpacing(self.height() // 9)
        self.main_layout.addWidget(application_name, alignment=Qt.AlignCenter)
        self.main_layout.addSpacing(10)
        self.main_layout.addWidget(version, alignment=Qt.AlignCenter)
        self.main_layout.addSpacing(10)
        self.main_layout.addWidget(local_ipv4_address, alignment=Qt.AlignCenter)
        self.main_layout.addStretch(1)
        self.main_layout.addWidget(loading_gif, alignment=Qt.AlignCenter)

        self.setLayout(self.main_layout)
        self.connect_backend_thread()

    def connect_backend_thread(self):
        """ this method starts the splash screen backend thread """

        self.splash_thread = SplashBackend()
        self.splash_thread.start()
        self.splash_thread.skip_authentication.connect(self.switch_window)
        self.splash_thread.register_device.connect(self.register_device)

    def register_device(self, api_token):
        self.splash_thread.stop()

        import authentication_screen
        self.i_window = authentication_screen.AuthenticationWindow(api_token=api_token)
        self.i_window.show()
        self.deleteLater()

    def switch_window(self):
        """ this method is triggered as soon as the skip_authentication signal is emitted by the backend thread"""
        self.splash_thread.stop()

        import loading_screen
        self.i_window = loading_screen.LoadingScreen()
        self.i_window.show()
        self.deleteLater()

