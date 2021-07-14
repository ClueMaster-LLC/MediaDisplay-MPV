import os
import subprocess


class AutoStartFunctionality:
    def __init__(self):

        # default variable
        self.current_working_directory = os.getcwd()

        # variables
        self.service_exists = False

        # instance methods
        self.check_service_exists()
        self.create_service()

    def check_service_exists(self):

        service_status = subprocess.getoutput("systemctl is-active --quiet cluemaster.service")
        if service_status == 0:
            self.service_exists = True

        else:
            self.service_exists = False

    def create_service(self):

        if self.service_exists is True:
            pass
        else:
            with open("assets/application data/cluemasterX.service", "w") as service_file:

                service_file.write("[Unit]\n")
                service_file.write("Description=Cluemaster Service\n")
                service_file.write("After=multi-user.target\n\n")

                service_file.write("[Service]\n")
                service_file.write("Type=simple\n")
                service_file.write("ExecStart=cd {}; ./splash_screen\n".format(self.current_working_directory))
                service_file.write("Restart=on-failure\n")
                service_file.write("RestartSec=5\n\n")

                service_file.write("[Install]\n")
                service_file.write("WantedBy=multi-user.target")

                self.starting_service()

    def starting_service(self):

        os.system(f"systemctl enable {self.current_working_directory}/assets/application\ data/cluemasterX.service;")
        os.system("systemctl start cluemasterX.service")
