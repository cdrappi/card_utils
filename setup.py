import glob
from setuptools import setup  # type: ignore
from pybind11.setup_helpers import Pybind11Extension, build_ext


source_files = sorted(glob.glob("CardGames/src/*.cpp"))
print(source_files)

ext_modules = [
    Pybind11Extension(
        "card_games",
        source_files,
        include_dirs=["CardGames/src"],
    ),
]


def _is_install_requirement(requirement):
    """return True iff setup should install requirement

    :param requirement: (str) line of requirements.txt file
    :return: (bool)
    """
    return not (requirement.startswith("-e") or "git+" in requirement)


with open("requirements/common.txt") as f:
    install_requires = [
        requirement
        for requirement in f.read().splitlines()
        if _is_install_requirement(requirement)
    ]

setup(
    name="card_utils",
    version="2023.6.3",
    install_requires=install_requires,
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
)
