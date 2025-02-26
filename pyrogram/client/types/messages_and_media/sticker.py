# Pyrogram - Telegram MTProto API Client Library for Python
# Copyright (C) 2017-2019 Dan Tès <https://github.com/delivrance>
#
# This file is part of Pyrogram.
#
# Pyrogram is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pyrogram is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

from functools import lru_cache
from struct import pack
from typing import List

import pyrogram
from pyrogram.api import types, functions
from pyrogram.errors import StickersetInvalid
from .thumbnail import Thumbnail
from ..object import Object
from ...ext.utils import encode


class Sticker(Object):
    """A sticker.

    Parameters:
        file_id (``str``):
            Unique identifier for this file.

        width (``int``):
            Sticker width.

        height (``int``):
            Sticker height.

        is_animated (``bool``):
            True, if the sticker is animated

        file_name (``str``, *optional*):
            Sticker file name.

        mime_type (``str``, *optional*):
            MIME type of the file as defined by sender.

        file_size (``int``, *optional*):
            File size.

        date (``int``, *optional*):
            Date the sticker was sent in Unix time.

        emoji (``str``, *optional*):
            Emoji associated with the sticker.

        set_name (``str``, *optional*):
            Name of the sticker set to which the sticker belongs.

        thumbs (List of :obj:`Thumbnail`, *optional*):
            Sticker thumbnails in the .webp or .jpg format.
    """

    # TODO: Add mask position

    def __init__(
        self,
        *,
        client: "pyrogram.BaseClient" = None,
        file_id: str,
        width: int,
        height: int,
        is_animated: bool,
        file_name: str = None,
        mime_type: str = None,
        file_size: int = None,
        date: int = None,
        emoji: str = None,
        set_name: str = None,
        thumbs: List[Thumbnail] = None
    ):
        super().__init__(client)

        self.file_id = file_id
        self.file_name = file_name
        self.mime_type = mime_type
        self.file_size = file_size
        self.date = date
        self.width = width
        self.height = height
        self.is_animated = is_animated
        self.emoji = emoji
        self.set_name = set_name
        self.thumbs = thumbs
        # self.mask_position = mask_position

    @staticmethod
    @lru_cache(maxsize=256)
    def _get_sticker_set_name(send, input_sticker_set_id):
        try:
            return send(
                functions.messages.GetStickerSet(
                    stickerset=types.InputStickerSetID(
                        id=input_sticker_set_id[0],
                        access_hash=input_sticker_set_id[1]
                    )
                )
            ).set.short_name
        except StickersetInvalid:
            return None

    @staticmethod
    def _parse(client, sticker: types.Document, image_size_attributes: types.DocumentAttributeImageSize,
               sticker_attributes: types.DocumentAttributeSticker, file_name: str) -> "Sticker":
        sticker_set = sticker_attributes.stickerset

        if isinstance(sticker_set, types.InputStickerSetID):
            input_sticker_set_id = (sticker_set.id, sticker_set.access_hash)
            set_name = Sticker._get_sticker_set_name(client.send, input_sticker_set_id)
        else:
            set_name = None

        return Sticker(
            file_id=encode(
                pack(
                    "<iiqq",
                    8,
                    sticker.dc_id,
                    sticker.id,
                    sticker.access_hash
                )
            ),
            width=image_size_attributes.w if image_size_attributes else 512,
            height=image_size_attributes.h if image_size_attributes else 512,
            is_animated=sticker.mime_type == "application/x-tgsticker",
            # TODO: mask_position
            set_name=set_name,
            emoji=sticker_attributes.alt or None,
            file_size=sticker.size,
            mime_type=sticker.mime_type,
            file_name=file_name,
            date=sticker.date,
            thumbs=Thumbnail._parse(client, sticker),
            client=client
        )
