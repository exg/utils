import setuptools

setuptools.setup(
    name="exg-utils",
    version="1.0",
    author="Emanuele Giaquinta",
    author_email="emanuele.giaquinta@gmail.com",
    description="miscellaneous utilities",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/exg/bin",
    packages=setuptools.find_packages(),
    python_requires=">=3.2",
    entry_points={
        "console_scripts": [
            "apt-dump = exg_utils.apt_dump:main",
            "b64decode = exg_utils.b64decode:main",
            "battery = exg_utils.battery:main",
            "browser = exg_utils.browser:main",
            "count-words = exg_utils.count_words:main",
            "cvs-ls = exg_utils.cvs_ls:main",
            "git-sync-fork = exg_utils.git_sync_fork:main",
            "deckdiff = exg_utils.deckdiff:main",
            "ld-grep = exg_utils.ld_grep:main",
            "matrix = exg_utils.matrix:main",
            "md2mbox = exg_utils.md2mbox:main",
            "mirror = exg_utils.mirror:main",
            "mp3sum = exg_utils.mp3sum:main",
            "mutt-open = exg_utils.mutt_open:main",
            "pastebin = exg_utils.pastebin:main",
            "pconfig = exg_utils.pconfig:main",
            "proc-size = exg_utils.proc_size:main",
            "pwd-tool = exg_utils.pwd_tool:main",
            "rename-symbol = exg_utils.rename_symbol:main",
            "setdiff = exg_utils.setdiff:main",
            "tabulate = exg_utils.tabulate:main",
            "tar-dump = exg_utils.tar_dump:main",
            "tar-size = exg_utils.tar_size:main",
            "urldecode = exg_utils.urldecode:main",
            "vcard2mutt = exg_utils.vcard2mutt:main",
            "verify-bom = exg_utils.verify_bom:main",
            "vsort = exg_utils.vsort:main",
        ]
    },
    classifiers=[
        "LICENSE :: OSI APPROVED :: GNU GENERAL PUBLIC LICENSE V2 OR LATER (GPLV2+)"
    ],
)
