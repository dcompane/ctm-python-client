
from __future__ import annotations
import attrs
import typing
import enum
import random
import string
from aapi import *


@attrs.define
class WaitForEvents(AAPIObject):

    _type: str = attrs.field(init=False, default='WaitForEvents', metadata={
        '_aapi_repr_': 'Type', '_type_aapi_': 'WaitForEvents'})
    object_name: str = attrs.field(init=False, default='waitForEvents', metadata={
        '_aapi_name_': True})
    events: typing.List[EventIn] = attrs.field(
        metadata={'_aapi_repr_': 'Events'})

    def __attrs_post_init__(self):
        if self.object_name == attrs.fields_dict(self.__class__)['object_name'].default:
            self.object_name = f'{self.object_name}_{random.choices(string.ascii_letters + string.digits, k=8)}'
