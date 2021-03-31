"""
This module includes code related to hooking Jaseci's Redis to the
core engine.
"""
from core.utils import utils
from core.utils.utils import logger
import core as core_mod
from core.utils.mem_hook import mem_hook
from jaseci.settings import REDIS_HOST
from redis import Redis
import json


class redis_hook(mem_hook):
    """
    Hooks Django ORM database for Jaseci objects to Jaseci's core engine.

    Sets user on initialization to route calls to correct user. This hook
    lives in :class:`User` class as per :field:`User.orm_hook`.
    """

    def __init__(self, red=Redis(host=REDIS_HOST, decode_responses=True)):
        self.red = red
        super().__init__()

    def get_obj_from_store(self, item_id):
        loaded_obj = self.red.get(item_id.urn)
        if(not loaded_obj):
            logger.error(
                str(f"Object {item_id} does not exist in Redis!")
            )
            return None

        j_type = json.loads(loaded_obj)['j_type']
        class_for_type = \
            utils.find_class_and_import(j_type, core_mod)
        ret_obj = class_for_type(h=self, auto_save=False)
        ret_obj.json_load(loaded_obj)

        return ret_obj

    def save_obj_to_store(self, item):
        # import traceback as tb; tb.print_stack();  # noqa
        self.red.set(item.id.urn, item.json())

    def destroy_obj_from_store(self, item):
        self.red.delete(item.id.urn)