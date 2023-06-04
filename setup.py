import glob
from setuptools import find_packages, setup  # type: ignore
from pybind11.setup_helpers import Pybind11Extension, build_ext

_SRC = f"CardGames/src"

ext_modules = [
    Pybind11Extension(
        "card_games",
        sorted([f"{_SRC}/main.cpp", *glob.glob(f"{_SRC}/*/*.cpp")]),
        include_dirs=[_SRC],
    ),
]

setup(
    name="card_utils",
    version="2023.6.3",
    packages=[*find_packages(), "card_games"],
    package_data={
        "card_games": ["*.pyi"],
    },
    install_requires=[],
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
)
