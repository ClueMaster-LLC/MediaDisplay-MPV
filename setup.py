from setuptools import setup

with open("README") as master_readme_file:
    long_description_x = master_readme_file.read()

setup(
    name="cluemaster-mediadisplay",
    version="0.4.6",
    description="Cluemaster Display",
    long_description=long_description_x,
    author="Mrittunjoy Sarkar",
    author_email="mrittunjoysarkar21@gmail.com",
    packages=["cluemaster-mediadisplay"],
    install_requires=["PyQt5==5.14.1", "requests", "python-mpv"],
    scripts=["splash_screen", "authentication_screen", "loading_screen", "normal_screen", "game_idle", "master_overlay",
             "clue_containers", "platform_facts", "threads"]
)
