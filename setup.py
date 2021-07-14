from setuptools import setup, find_packages

setup(
    name="cluemaster-mediadisplay",
    version="0.4.7",
    description="Cluemaster Display",
    author="Mrittunjoy Sarkar",
    author_email="mrittunjoysarkar21@gmail.com",
    packages=find_packages()
    install_requires=["PyQt5==5.14.1", "requests", "python-mpv"],
    scripts=["splash_screen", "authentication_screen", "loading_screen", "normal_screen", "game_idle", "master_overlay",
             "clue_containers", "platform_facts", "threads"]
)
