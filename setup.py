from distutils.core import setup

setup(
    name="noobhack",
    version="0.4",
    author="Sam Gibson",
    author_email="sam@ifdown.net",
    url="https://samfoo.github.com/noobhack",
    description="noobhack helps you ascend at nethack",
    long_description=open("readme.md", "r").read(),
    install_requires=["vt102 >= 0.3.3"],
    packages=["noobhack", "noobhack.game", "noobhack.ui"],
    scripts=["scripts/noobhack"],
    keywords="nethack noobhack nao hack rogue roguelike",
    license="GPLv3"
)
