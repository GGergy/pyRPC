from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

requirements = ["telegrambotapi", "pythonnet"]


setup(
    name="reprim",
    version="0.0.1",
    author="GGergy",
    author_email="gergy2k07@gmail.com",
    description="for quests write me in Telegram (@IDieLast)",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/GGergy/RePrIm/",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)
