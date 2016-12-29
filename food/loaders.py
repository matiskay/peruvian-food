from __future__ import unicode_literals

import re

from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Identity
from scrapy.utils.markup import (remove_tags, replace_escape_chars,
                                 unquote_markup)

from .items import FoodItem

_clean_spaces_re = re.compile('\s+', re.U)


def clean_spaces(value):
    return _clean_spaces_re.sub(' ', value)


_br_re = re.compile('<br\s?\/?>', re.IGNORECASE)
def replace_br(value):
    return _br_re.sub(' ', value)


def replace_escape(value):
    return replace_escape_chars(value, replace_by=' ')


def split(value):
    return [v.strip() for v in value.split(',')]


def strip(value):
    return value.strip()


class FoodItemLoader(ItemLoader):
    default_item_class = FoodItem

    default_input_processor = MapCompose(replace_br, remove_tags, unquote_markup,
            replace_escape, strip, clean_spaces)
    default_output_processor = TakeFirst()

    ingredients_out = Identity()

