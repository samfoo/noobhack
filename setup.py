from distutils.core import setup

setup(
    name="noobhack",
    version="0.1.0",
    author="Sam Gibson",
    author_email="sam@ifdown.net",
    url="https://github.com/samfoo/noobhack",
    description="noobhack helps you ascend at nethack",
    long_description=open("readme.md", "r").read(),
    requires=["vt102 (>=0.2.0)"],
    packages=["noobhack"],
    scripts=["noobhack/noobhack"],
    license="Lesser General Public License v3.0"
)
