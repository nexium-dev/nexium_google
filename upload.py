import logging
import subprocess
from os import getenv

from dotenv import load_dotenv


load_dotenv()
IS_TEST = True if getenv('IS_TEST') == 'True' else False
if IS_TEST:
    USERNAME = getenv('PYPI_TEST_USERNAME')
    PASSWORD = getenv('PYPI_TEST_PASSWORD')
    REPOSITORY = 'testpypi'
else:
    USERNAME = getenv('PYPI_USERNAME')
    PASSWORD = getenv('PYPI_PASSWORD')
    REPOSITORY = 'pypi'


def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stdout)
        logging.error(f'Error occurred: {result.stderr}')
    else:
        logging.info(result.stdout)


def main():
    logging.info('Run setup.py...')
    run_command('python setup.py sdist bdist_wheel')

    logging.info('Upload...')
    upload_command = f'twine upload --repository {REPOSITORY} dist/* -u {USERNAME} -p {PASSWORD}'
    run_command(upload_command)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    main()