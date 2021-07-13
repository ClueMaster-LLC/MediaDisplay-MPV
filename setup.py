from setuptools import setup

setup(
    name="cluemaster_mediadisplay",
    version="0.4.6",
    description="Cluemaster Display",
    author="ClueMaster LLC",
    author_email="support@cluemaster.io",
    packages=["cluemaster_mediadisplay"],
    install_requires=["PyQt5==5.14.1", "requests", "python-mpv"],
    scripts=["splash_screen", "authentication_screen", "loading_screen", "normal_screen", "game_idle", "master_overlay",
             "clue_containers", "platform_facts", "threads"]
)
