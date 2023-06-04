from setuptools import setup
import os


def find_stubs(package):
    stubs = []
    for root, dirs, files in os.walk(package):
        for file in files:
            path = os.path.join(root, file).replace(package + os.sep, '', 1)
            stubs.append(path)
    return dict(package=stubs)


setup(
    name='card_games-stubs',
    maintainer="card_games Developers",
    maintainer_email="example@python.org",
    description="PEP 561 type stubs for card_games",
    version='1.0',
    packages=['card_games-stubs'],
    # PEP 561 requires these
    install_requires=['card_games'],
    package_data=find_stubs('card_games-stubs'),
)