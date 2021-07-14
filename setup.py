from setuptools import setup, find_packages

setup(
    name="cluemaster_mediadisplay",
    version="0.4.7",
    description="Cluemaster Display",
    author="Mrittunjoy Sarkar",
    author_email="mrittunjoysarkar21@gmail.com",
    packages=find_packages(),
    install_requires=["PyQt5==5.14.1", "requests", "python-mpv"],
    scripts=["splash_screen.py", "authentication_screen.py", "loading_screen.py", "normal_screen.py", "game_idle.py", "master_overlay.py",
             "clue_containers.py", "platform_facts.py", "threads.py"]
)
