from setuptools import setup

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

requirements = ["pytelegrambotapi", "pythonnet"]


setup(
    name="reprim",
    version="0.0.6",
    author="GGergy",
    author_email="gergy2k07@gmail.com",
    description="for questions write me in Telegram (@IDieLast)",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/GGergy/RePrIm/",
    packages=['RePrIm', 'RePrIm/util'],
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)
