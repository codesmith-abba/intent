from dataclasses import dataclass
from enum import Enum


class CacheStatus(Enum):

    HIT = "hit"
    MISS = "miss"
    INVALIDATED = "invalidated"


@dataclass(slots=True)
class CacheDecision:

    status: CacheStatus

    source: str

    reason: str