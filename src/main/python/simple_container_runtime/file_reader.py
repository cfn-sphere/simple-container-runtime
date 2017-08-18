import requests
import codecs
import json
import os

import yaml

from simple_container_runtime.aws.s3 import S3
from simple_container_runtime.exceptions import ScrBaseException


class FileLoader(object):
    @classmethod
    def get_yaml_or_json_file(cls, url, working_dir):
        """
        Load yaml or json from filesystem or s3
        :param url: str
        :param working_dir: str
        :return: dict
        """
        file_content = cls.get_file(url, working_dir)

        try:
            return json.loads(file_content)
        except Exception:
            try:
                return yaml.load(file_content)
            except Exception:
                raise ScrBaseException("Could not read {} as json or yaml.".format(url))

    @classmethod
    def get_file(cls, url, working_dir):
        """
        Load file from filesystem or s3
        :param url: str
        :param working_dir: str
        :return: str(utf-8)
        """
        if url.lower().startswith("s3://"):
            return cls._s3_get_file(url)
        elif url.lower().startswith("http"):
            return cls._http_get_file(url)
        else:
            return cls._fs_get_file(url, working_dir)

    @staticmethod
    def _fs_get_file(url, working_dir):
        """
        Load file from filesystem
        :param url: str template path
        :return: str(utf-8)
        """
        if not os.path.isabs(url) and working_dir:
            url = os.path.join(working_dir, url)

        try:
            with codecs.open(url, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise ScrBaseException("Could not load file from {0}: {1}".format(url, e))

    @staticmethod
    def _s3_get_file(url):
        """
        Load file from s3
        :param url: str
        :return: str(utf-8)
        """
        try:
            return S3().get_contents_from_url(url)
        except Exception as e:
            raise ScrBaseException("Could not load file from {0}: {1}".format(url, e))

    @staticmethod
    def _http_get_file(url):
        return requests.get(url).content
