from textwrap import shorten

from py2neo import ogm

from .settings import SCHEMA


class Fragment(ogm.Model):
    __primarylabel__ = SCHEMA["labels"]["fragment"]
    name = ogm.Property()

    def __repr__(self):
        text = f"[{self.__primaryvalue__}] {self.name}"
        return shorten(text, 30)
