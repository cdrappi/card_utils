from setuptools import setup


def _is_install_requirement(requirement):
    """ return True iff setup should install requirement

    :param requirement: (str) line of requirements.txt file
    :return: (bool)
    """
    return not (requirement.startswith('-e') or 'git+' in requirement)


with open('requirements/common.txt') as f:
    install_requires = [
        requirement
        for requirement in f.read().splitlines()
        if _is_install_requirement(requirement)
    ]

setup(
    name='gin_utils',
    version='2019.5.5.4',
    packages=['gin_utils'],
    install_requires=install_requires,
)
