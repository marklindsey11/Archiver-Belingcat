from __future__ import annotations
from abc import abstractmethod
from dataclasses import dataclass
import hashlib
from typing import IO, Any

from ..core import Media, Metadata, Step
from loguru import logger
import os, uuid
from slugify import slugify


@dataclass
class Storage(Step):
    name = "storage"
    PATH_GENERATOR_OPTIONS = ["flat", "url", "random"]
    FILENAME_GENERATOR_CHOICES = ["random", "static"]

    def __init__(self, config: dict) -> None:
        # without this STEP.__init__ is not called
        super().__init__(config)
        assert self.path_generator in Storage.PATH_GENERATOR_OPTIONS, f"path_generator must be one of {Storage.PATH_GENERATOR_OPTIONS}"
        assert self.filename_generator in Storage.FILENAME_GENERATOR_CHOICES, f"filename_generator must be one of {Storage.FILENAME_GENERATOR_CHOICES}"

    @staticmethod
    def configs() -> dict:
        return {
            "path_generator": {
                "default": "url",
                "help": "how to store the file in terms of directory structure: 'flat' sets to root; 'url' creates a directory based on the provided URL; 'random' creates a random directory.",
                "choices": Storage.PATH_GENERATOR_OPTIONS
            },
            "filename_generator": {
                "default": "random",
                "help": "how to name stored files: 'random' creates a random string; 'static' uses a replicable strategy such as a hash.",
                "choices": Storage.FILENAME_GENERATOR_CHOICES
            }
        }

    def init(name: str, config: dict) -> Storage:
        # only for typing...
        return Step.init(name, config, Storage)

    def store(self, media: Media, item: Metadata) -> None:
        self.set_key(media, item)
        self.upload(media)
        media.add_url(self.get_cdn_url(media))

    @abstractmethod
    def get_cdn_url(self, media: Media) -> str: pass

    @abstractmethod
    def uploadf(self, file: IO[bytes], key: str, **kwargs: dict) -> bool: pass

    def upload(self, media: Media, **kwargs) -> bool:
        logger.debug(f'[{self.__class__.name}] storing file {media.filename} with key {media.key}')
        with open(media.filename, 'rb') as f:
            return self.uploadf(f, media, **kwargs)

    def set_key(self, media: Media, item: Metadata) -> None:
        """takes the media and optionally item info and generates a key"""
        if media.key is not None and len(media.key) > 0: return
        folder = item.get("folder", "")
        filename, ext = os.path.splitext(media.filename)

        # path_generator logic
        if self.path_generator == "flat": 
            path = ""
            filename = slugify(filename) # in case it comes with os.sep
        elif self.path_generator == "url": path = slugify(item.get_url())
        elif self.path_generator == "random":
            path = item.get("random_path", str(uuid.uuid4())[:16], True)

        # filename_generator logic
        if self.filename_generator == "random": filename = str(uuid.uuid4())[:16]
        elif self.filename_generator == "static": 
            with open(media.filename, "rb") as f:
                bytes = f.read()  # read entire file as bytes
            filename = hashlib.sha256(bytes).hexdigest()[:24]

        media.key = os.path.join(folder, path, f"{filename}{ext}")