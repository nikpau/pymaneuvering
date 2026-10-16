from enum import Enum

from .utils.common import MMGVessel, AbkowitzVessel, IntegrationMode
from .mmg.calibrated_vessels import (kvlcc2_full, kvlcc2_l64)
from .mmg.dynamics import MMGModel
from .abkowitz.dynamics import AbkowitzModel
from .abkowitz.calibrated_vessels import gms_like_inland_barge

class VTYPE(Enum):
    GMS_LIKE = gms_like_inland_barge
    KVLCC2_L64 = kvlcc2_l64
    KVLCC2_FULL = kvlcc2_full

class Vessel:
    """Dispatcher class for different vessel types."""
    
    def __new__(cls, *, new_from: VTYPE):
        if new_from in [VTYPE.KVLCC2_FULL, VTYPE.KVLCC2_L64]:
            vessel_params = new_from.value
            return MMGModel(vessel=MMGVessel(**vessel_params))
        elif new_from == VTYPE.GMS_LIKE:
            vessel_params = new_from.value
            return AbkowitzModel(vessel=AbkowitzVessel(**vessel_params))
        else:
            raise ValueError(f"Unknown vessel type: {new_from}")

__version__ = "2.0.1"
__author__ = "Niklas Paulig"
