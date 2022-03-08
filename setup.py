import os
from setuptools import setup, find_packages
import sys

from mxts import __version__


with open(os.path.join(os.path.dirname(__file__), "README.md"), encoding="utf-8") as f:
    long_description = f.read().replace("\r\n", "\n")

if sys.version_info.major < 3 or sys.version_info.minor < 7:
    raise Exception("Must be python3.7 or above")

requires = [
    'aiohttp>=3.0.0',
    'ujson>=1.35',
    'yarl>=0.12.0',
    'pandas'
]

# requires_dev = [] + requires

setup(
    name="mxts",
    version=__version__,
    description="Multi Exchange Trading System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kevingivens/mxts",
    author="Kevin Givens",
    author_email="givenskevinm@gmail.com",
    license="Apache 2.0",
    install_requires=requires,
    # extras_require={"dev": requires_dev},
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    keywords="algorithmic trading event driven",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
