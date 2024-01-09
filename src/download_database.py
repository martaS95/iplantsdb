import bz2
import gzip
import base64
import urllib.request
from contextlib import closing
import tarfile
from abc import ABCMeta, abstractmethod
import shutil
import os
import logging

from utils.config import PROJECT_PATH

logging.basicConfig(level=logging.DEBUG)


class DownloadDatabase(metaclass=ABCMeta):

    def __init__(self, db_name, version):
        self.db = db_name
        self.version = str(version)

        self.project_path = PROJECT_PATH

    @abstractmethod
    def download(self):
        """
        Abstract method to download and extract the database files
        """
        pass

    @abstractmethod
    def get_new_version(self):
        """
        Abstract method to get the version of the new database
        """
        pass


class DownloadPMNDatabase(DownloadDatabase):
    """
    Class to download the new version of a PMN database (Plant Metabolic Network resource)
    """

    def __init__(self, db_name, version):

        super().__init__(db_name, version)

    def download(self):
        """
        Download a cyc database from PMN
        Returns
        -------
        """

        db_version = self.db + '_' + self.version

        link = 'ftp://ftp.plantcyc.org/pmn/private/plantcyc/' + self.db + '.tar.bz2'
        download_path = os.path.join(self.project_path, 'downloads')
        download = os.path.join(download_path, self.db + '.tar.bz2')

        with closing(urllib.request.urlopen(link)) as response:
            with open(download, 'wb') as file:
                shutil.copyfileobj(response, file)

        unzipfile = bz2.BZ2File(download).read()
        tar = os.path.join(download_path, self.db + '.tar')
        open(tar, 'wb').write(unzipfile)
        my_tar = tarfile.open(tar)
        my_tar.extractall(os.path.join(download_path, self.db))
        my_tar.close()

        if os.path.isdir(os.path.join(download_path, self.db)):
            message = 'The new version of the ' + self.db + ' database was downloaded'
            logging.info(message)

            outputfile = os.path.join(self.project_path, 'update_outputs', db_version + '_downloaded.txt')

            with open(outputfile, 'w') as output:
                output.write(message)
        else:
            logging.info('Some error has occorred. The ' + self.db + ' database was not downloaded')

    def get_new_version(self):
        version_path = os.path.join(self.project_path, 'downloads', str(self.db), str(self.db), 'default-version')
        with open(version_path, 'r') as version_file:
            version = version_file.readline()

        return version


class DownloadMetaDatabase(DownloadDatabase):
    """
    Class to download the new version of a biocyc database (BIOCYC resource) (only BIOCYC and METACYC are free)
    """

    def __init__(self, db_name, version, username='biocyc-flatfiles', password='data-20541'):

        super().__init__(db_name, version)

        self._username = username
        self._password = password

    @property
    def username(self) -> str:
        return self._username

    @username.setter
    def username(self, value):
        self._username = value

    @property
    def password(self) -> str:
        return self._password

    @password.setter
    def password(self, value):
        self._password = value

    def download(self):
        """
        Download a cyc database from BIOCYC
        Returns
        -------
        """

        db_version = self.db + '_' + self.version

        link = 'https://brg-files.ai.sri.com/public/dist/meta.tar.gz'
        download_path = os.path.join(self.project_path, 'downloads')
        download = os.path.join(download_path, self.db + '.tar.gz')

        req = urllib.request.Request(link)
        base64string = base64.b64encode(bytes('{}:{}'.format(self.username, self.password), 'ascii'))
        req.add_header('Authorization', 'Basic {}'.format(base64string.decode('utf-8')))

        with urllib.request.urlopen(req) as response:
            with open(download, 'wb') as file:
                shutil.copyfileobj(response, file)

        unzipfile = gzip.open(download).read()
        tar = os.path.join(download_path, self.db + '.tar')
        open(tar, 'wb').write(unzipfile)
        my_tar = tarfile.open(tar)
        my_tar.extractall(os.path.join(download_path, self.db))
        my_tar.close()

        if os.path.isdir(os.path.join(download_path, self.db)):
            message = 'The new version of the ' + self.db + ' database was downloaded'
            logging.info(message)

            outputfile = os.path.join(self.project_path, 'update_outputs', db_version + '_downloaded.txt')

            with open(outputfile, 'w') as output:
                output.write(message)
        else:
            logging.info('Some error has occorred. The ' + self.db + ' database was not downloaded')

    def get_new_version(self):
        version_path = os.path.join(self.project_path, 'downloads', self.db)
        version = os.listdir(version_path)[0]
        return version
