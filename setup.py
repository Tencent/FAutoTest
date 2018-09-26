from setuptools import setup, find_packages

NAME = "fastAutoTest"
VERSION = "2.2.2"
AUTHOR = "jaggergan,fitchzheng"
PACKAGES = find_packages()
CLASSIFIERS = [
    "Operating System :: Microsoft :: Windows",
    "Operating System :: MacOS",
    "Operating System :: Unix",
    "Programming Language :: Python :: 2.7",
]

INSTALL_REQUIRES = [
    "websocket-client>=0.44.0",
    "uiautomator>=0.3.2",
    "lxml>=4.0.0",
    "bidict>=0.14.0"

]
setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    packages=PACKAGES,
    classifiers=CLASSIFIERS,
    include_package_data=True,
    install_requires=INSTALL_REQUIRES
)
