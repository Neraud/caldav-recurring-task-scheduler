import io
import os
import re

from setuptools import find_packages
from setuptools import setup


def read(filename):
    filename = os.path.join(os.path.dirname(__file__), filename)
    text_type = type(u"")
    with io.open(filename, mode="r", encoding='utf-8') as fd:
        return re.sub(text_type(r':[a-z]+:`~?(.*?)`'), text_type(r'``\1``'),
                      fd.read())


setup(
    name="caldav_recurring_task_scheduler",
    version="0.1.0",
    url="https://github.com/Neraud/caldav-recurring-task-scheduler",
    license='MIT',
    author="Neraud",
    description="This project is meant as a workaround to use recurring tasks on a CalDAV instance that doesn't support it natively.",
    long_description=read("README.md"),
    packages=find_packages(exclude=('tests', )),
    install_requires=[
        'caldav==1.3.9',
        'PyYAML==6.0.2',
        'python-dateutil==2.9.0.post0',
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.13',
    ],
)
