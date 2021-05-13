import json
import time
import requests
import simplejson
from PyQt5.QtCore import QThread, pyqtSignal


class GameDetails(QThread):
    statusUpdated = pyqtSignal(int)
    cluesUsedChanged = pyqtSignal(int)
    apiStatus = pyqtSignal(int)

    def run(self):
        with open("assets/application data/unique code.json") as file:
            json_object = json.load(file)

        device_unique_code = json_object["Device Unique Code"]
        game_details_url = f"https://deviceapi.cluemaster.io/api/Device/GetGameDetails/{device_unique_code}"

        while True:
            try:

                with open("assets/application data/ThreadInfo.json") as thread_file:
                    thread_file_response = json.load(thread_file)

                if thread_file_response["IsGameDetailsThreadRunning"] is True:
                    pass

                else:
                    print("game details broke")
                    return

                print("Game Details")
                response = requests.get(game_details_url).json()
                gameStatus = response["gameStatus"]

                if response["noOfCluesUsed"] is None:
                    noOfCluesUsed = 0

                else:
                    noOfCluesUsed = response["noOfCluesUsed"]

                with open("assets/application data/GameDetails.json", "w") as file:
                    json.dump(response, file)

                self.statusUpdated.emit(gameStatus)
                self.cluesUsedChanged.emit(noOfCluesUsed)

            except requests.exceptions.ConnectionError:
                self.apiStatus.emit(0)

            except json.decoder.JSONDecodeError:
                pass

            except simplejson.errors.JSONDecodeError:
                pass

            else:
                self.apiStatus.emit(1)

            finally:
                time.sleep(5)

    def stop(self):

        with open("assets/application data/ThreadInfo.json") as initial_thread_file:
            thread_file_response = json.load(initial_thread_file)

        thread_file_response["IsGameDetailsThreadRunning"] = False

        with open("assets/application data/ThreadInfo.json", "w") as thread_file:
            json.dump(thread_file_response, thread_file)


class IdentifyDevice(QThread):
    identify_device = pyqtSignal(int)

    def run(self):

        with open("assets/application data/unique code.json") as file:
            json_object = json.load(file)

        device_unique_code = json_object["Device Unique Code"]
        identify_device_url = f"https://deviceapi.cluemaster.io/api/Device/IdentifyDevice/{device_unique_code}"

        while True:
            try:
                with open("assets/application data/ThreadInfo.json") as thread_file:
                    thread_file_response = json.load(thread_file)

                if thread_file_response["IsIdentifyDeviceThreadRunning"] is True:
                    pass

                else:
                    print("identify device broke")
                    return

                print("identify device")
                json_response = requests.get(identify_device_url).json()

                display_text = json_response["DisplayText"]
                request_date = json_response["Requestdate"]

                dictionary = {"DisplayText": display_text, "Requestdate": request_date}

                with open("assets/application data/IdentifyDeviceDetails.json", "w") as file:
                    json.dump(dictionary, file)

                self.identify_device.emit(1)

            except requests.exceptions.ConnectionError:
                pass

            except json.decoder.JSONDecodeError:
                self.identify_device.emit(0)

            except simplejson.errors.JSONDecodeError:
                self.identify_device.emit(0)

            except FileNotFoundError:
                pass

            finally:
                time.sleep(15)

    def stop(self):

        with open("assets/application data/ThreadInfo.json") as initial_thread_file:
            thread_file_response = json.load(initial_thread_file)

        thread_file_response["IsIdentifyDeviceThreadRunning"] = False

        with open("assets/application data/ThreadInfo.json", "w") as thread_file:
            json.dump(thread_file_response, thread_file)


class ShutdownRestartRequest(QThread):
    shutdown = pyqtSignal()
    restart = pyqtSignal()

    def run(self):

        with open("assets/application data/unique code.json") as file:
            json_object = json.load(file)

        unique_code = json_object["Device Unique Code"]
        shutdown_restart_api = f"https://deviceapi.cluemaster.io/api/Device/GetShutdownRestartRequest/{unique_code}"

        while True:
            try:
                with open("assets/application data/ThreadInfo.json") as thread_file:
                    thread_file_response = json.load(thread_file)

                if thread_file_response["IsShutdownRestartRequestThreadRunning"] is True:
                    pass

                else:
                    print("shutdown restart  broke")
                    return

                print("shutdown restart response")
                json_response = requests.get(shutdown_restart_api).json()

                deviceRequestId = json_response["DeviceRequestid"]
                requestId = json_response["RequestID"]

                if requestId == 8:
                    url = f"https://deviceapi.cluemaster.io/api/Device/{unique_code}/{deviceRequestId}"
                    requests.post(url)
                    self.restart.emit()

                elif requestId == 9:
                    url = f"https://deviceapi.cluemaster.io/api/Device/{unique_code}/{deviceRequestId}"
                    requests.post(url)
                    self.shutdown.emit()

            except requests.exceptions.ConnectionError:
                pass

            except json.decoder.JSONDecodeError:
                pass

            except simplejson.errors.JSONDecodeError:
                pass

            except FileNotFoundError:
                pass

            finally:
                time.sleep(15)

    def stop(self):

        with open("assets/application data/ThreadInfo.json") as initial_thread_file:
            thread_file_response = json.load(initial_thread_file)

        thread_file_response["IsShutdownRestartRequestThreadRunning"] = False

        with open("assets/application data/ThreadInfo.json", "w") as thread_file:
            json.dump(thread_file_response, thread_file)


class GetGameClue(QThread):
    statusChanged = pyqtSignal()
    apiStatus = pyqtSignal(int)

    def run(self):
        with open("assets/application data/GameDetails.json") as file:
            json_object = json.load(file)

        initial_gameId = json_object["gameId"]
        game_clue_url = f"https://deviceapi.cluemaster.io/api/Device/GetGameClue/{initial_gameId}"

        while True:
            try:
                with open("assets/application data/ThreadInfo.json") as thread_file:
                    thread_file_response = json.load(thread_file)

                if thread_file_response["IsGameClueThreadRunning"] is True:
                    pass

                else:
                    print("game clue broke")
                    return

                print("game clue response")
                json_response = requests.get(game_clue_url).json()

                gameClueId = json_response["gameClueId"]
                clueFileName = json_response["clueFilename"]
                clueText = json_response["clueText"]
                clueStatus = json_response["clueStatus"]
                clueType = json_response["clueType"]
                gameId = json_response["gameId"]

                requests.post(f"https://deviceapi.cluemaster.io/api/Device/PostGameClue/{gameId}/{gameClueId}")
                dictionary = {"gameClueId": gameClueId, "clueFileName": clueFileName, "clueStatus": clueStatus,
                              "clueText": clueText, "clueType": clueType, "gameId": gameId}

                with open("assets/application data/GameClue.json", "w") as file:
                    json.dump(dictionary, file)

                self.statusChanged.emit()

            except requests.exceptions.ConnectionError:
                self.apiStatus.emit(0)

            except json.decoder.JSONDecodeError:
                pass

            except simplejson.errors.JSONDecodeError:
                pass

            except KeyError:
                pass

            else:
                self.apiStatus.emit(1)

            finally:
                time.sleep(5)

    def stop(self):

        with open("assets/application data/ThreadInfo.json") as initial_thread_file:
            thread_file_response = json.load(initial_thread_file)

        thread_file_response["IsGameClueThreadRunning"] = False

        with open("assets/application data/ThreadInfo.json", "w") as thread_file:
            json.dump(thread_file_response, thread_file)


class GetTimerRequest(QThread):
    updateTimer = pyqtSignal()
    apiStatus = pyqtSignal(int)

    def run(self):

        with open("assets/application data/unique code.json") as file:
            json_object = json.load(file)

        device_unique_code = json_object["Device Unique Code"]
        get_timer_request_api = f"https://deviceapi.cluemaster.io/api/Device/GetTimerRequest/{device_unique_code}"

        while True:
            try:
                with open("assets/application data/ThreadInfo.json") as thread_file:
                    thread_file_response = json.load(thread_file)

                if thread_file_response["IsTimerRequestThreadRunning"] is True:
                    pass

                else:
                    print("timer request broke")
                    return

                print("timer response")
                response = requests.get(get_timer_request_api).json()

                request_id = response["DeviceRequestid"]
                device_key = response["DeviceKey"]
                requests.post(f"https://deviceapi.cluemaster.io/api/Device/{device_key}/{request_id}")

                self.updateTimer.emit()

            except json.decoder.JSONDecodeError:
                pass

            except simplejson.errors.JSONDecodeError:
                pass

            except requests.exceptions.ConnectionError:
                self.apiStatus.emit(0)

            else:
                self.apiStatus.emit(1)

            finally:
                time.sleep(5)

    def stop(self):

        with open("assets/application data/ThreadInfo.json") as initial_thread_file:
            thread_file_response = json.load(initial_thread_file)

        thread_file_response["IsTimerRequestThreadRunning"] = False

        with open("assets/application data/ThreadInfo.json", "w") as thread_file:
            json.dump(thread_file_response, thread_file)


class DownloadConfigs(QThread):
    downloadFiles = pyqtSignal()

    def run(self):

        with open("assets/application data/unique code.json") as file:
            initial_dictionary = json.load(file)

        unique_code = initial_dictionary["Device Unique Code"]
        download_files_request_api = f"https://deviceapi.cluemaster.io/api/Device/DownloadFilesRequest/{unique_code}"

        while True:
            try:
                with open("assets/application data/ThreadInfo.json") as thread_file:
                    thread_file_response = json.load(thread_file)

                if thread_file_response["IsDownloadConfigsThreadRunning"] is True:
                    pass

                else:
                    print("download configs broke")
                    return

                print("download config response")
                response = requests.get(download_files_request_api).json()
                request_id = response["DeviceRequestid"]
                device_key = response["DeviceKey"]
                print(requests.post(f"https://deviceapi.cluemaster.io/api/Device/{device_key}/{request_id}"))

                self.downloadFiles.emit()
                return

            except requests.exceptions.ConnectionError:
                pass

            except json.decoder.JSONDecodeError:
                pass

            except simplejson.errors.JSONDecodeError:
                pass

            except FileNotFoundError:
                pass

            finally:
                time.sleep(15)

    def stop(self):

        with open("assets/application data/ThreadInfo.json") as initial_thread_file:
            thread_file_response = json.load(initial_thread_file)

        thread_file_response["IsDownloadConfigsThreadRunning"] = False

        with open("assets/application data/ThreadInfo.json", "w") as thread_file:
            json.dump(thread_file_response, thread_file)
