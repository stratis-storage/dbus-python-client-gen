"""
Python packaging file for setup tools.
"""

# isort: STDLIB
import os

# isort: THIRDPARTY
import setuptools


def local_file(name):
    """
    Function to obtain the relative path of a filename.
    """
    return os.path.relpath(os.path.join(os.path.dirname(__file__), name))


with open(local_file("src/dbus_python_client_gen/_version.py"), encoding="utf-8") as o:
    exec(o.read())  # pylint: disable=exec-used

with open(local_file("README.rst"), encoding="utf-8") as o:
    long_description = o.read()

setuptools.setup(
    name="dbus-python-client-gen",
    version=__version__,  # pylint: disable=undefined-variable
    author="Anne Mulhern",
    author_email="amulhern@redhat.com",
    description="transforms values into properly wrapped dbus-python objects",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    platforms=["Linux"],
    license="MPL-2.0",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)"
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires=["dbus-python", "into-dbus-python>=0.08"],
    package_dir={"": "src"},
    packages=setuptools.find_packages("src"),
    url="https://github.com/mulkieran/dbus-python-client-gen",
)
