from setuptools import setup, find_packages
from os import getenv
# noinspection PyPackageRequirements
from dotenv import load_dotenv


load_dotenv()
NAME = getenv('NAME')
VERSION = getenv('VERSION')
DESCRIPTION = getenv('DESCRIPTION')
AUTHOR = getenv('AUTHOR')
AUTHOR_EMAIL = getenv('AUTHOR_EMAIL')
URL = getenv('URL')


def parse_requirements(filename: str) -> list[str]:
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]


setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    packages=find_packages(),
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license='MIT',
    install_requires=parse_requirements('requires.txt'),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.11',
)

