""" module managing the repositories with firmware"""

import os
import glob
from configparser import ConfigParser

from appdirs import user_config_dir
from git import Repo, InvalidGitRepositoryError

def check_local_storage():
    """ Make sure the local repository exists """
    defaultfwremote = "https://github.com/dirkjankrijnders/universal_decoder"

    fwrepodir = os.path.join(user_config_dir("decconf", "pythsoft"),
                             'firmwarerepos')
    if not os.path.isdir(user_config_dir("decconf", "pythsoft")):
        os.mkdir(user_config_dir("decconf", "pythsoft"))
    if not os.path.isdir(fwrepodir):
        os.mkdir(fwrepodir)
    defaultrepodir = os.path.join(fwrepodir, 'default')
    if not os.path.isdir(defaultrepodir):
        os.mkdir(defaultrepodir)
    try:
        repo = Repo(defaultrepodir)
    except InvalidGitRepositoryError:
        repo = Repo.init(fwrepodir)
        origin = repo.create_remote('origin', defaultfwremote)
        with repo.config_writer() as configwriter:
            configwriter.set('core', 'sparsecheckout', True)
        with open(os.path.join(fwrepodir, ".git", "info", "sparse-checkout"), 'w') as fid:
            fid.write("release")
        origin.fetch()
        repo.create_head('develop', origin.refs.develop)
        repo.refs.develop.set_tracking_branch(origin.refs.develop)
        repo.refs.develop.checkout()
    return repo

def update_local_storage(repo):
    """ Pull new firmware from the remote reposistories """
    origin = repo.remote()
    origin.pull()

class FirmwarePackageManager(object):
    """ Manange the firmware packages pulled from the repositories """
    def __init__(self, fwrepodir):
        super(FirmwarePackageManager, self).__init__()
        self.fwrepodir = fwrepodir
        self._packages = []

    @property
    def packages(self):
        """ Return a list of FirmwarePackage's """
        if not self._packages:
            for pkg in glob.glob(os.path.join(self.fwrepodir, '*')):
                self._packages.append(FirmwarePackage(pkg, self.fwrepodir))
        return self._packages

    def rescan(self):
        """ Force a rescan of the package directories """
        self._packages = []

class FirmwarePackage(object):
    """ Represent a firmpackage """
    def __init__(self, fwpkgdir, fwrepodir):
        super(FirmwarePackage, self).__init__()
        self.fwpkgdir = fwpkgdir
        self.fwrepodir = fwrepodir
        self.version = ""
        self.filename = None
        self.boards = []
        self._parsepkg()

    def __str__(self):
        """ Pretty print package information """
        format_string = "Firmware package {}, version {}, available for boards {}"
        return format_string.format(self.filename, self.version, ", ".join(self.boards))

    def _parsepkg(self):
        """ Parse the metadata file supplied in the packages """
        parser = ConfigParser()
        parser.read(os.path.join(self.fwrepodir, self.fwpkgdir, "fwpackage.ini"))
        self.version = parser["release"]["version"]
        self.filename = parser["release"]["filename"]
        self.boards = parser["release"]["boards"]
        if not isinstance(self.boards, list):
            self.boards = [self.boards]

    @property
    def name(self):
        """ Return the name of this package, based on the filename"""
        return self.filename.replace("_", " ")

    def fullpath(self, board, ext="hex"):
        """ Return the complete path to the firmware file """
        if not board in self.boards:
            raise ValueError("board {} not available, available boards are: {}"
                             .format(board, self.boards))

        return os.path.join(self.fwrepodir, self.fwpkgdir, board, self.filename + "." + ext)
