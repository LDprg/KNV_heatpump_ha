"""Constants for the KNV heatpump integration."""
from enum import Enum
import logging

LOGGER = logging.getLogger(__package__)

DOMAIN = "knv_heatpump"


ERR_INVALID_IP = "invalid_ip"


class Type(Enum):
    SENSOR = 1
    NUMBER = 2
    SELECT = 3


def getType(data):
    LOGGER.warn("%s\t%s", type(data), data)

    if 'writeable' in data.keys() and data["writeable"] is True:
        if data["type"] == 4 or data["type"] == 6 or data["type"] == 8:
            return Type.NUMBER

    if data["type"] == 29:
        return Type.SELECT
    
    return Type.SENSOR
