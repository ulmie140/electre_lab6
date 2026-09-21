from dataclasses import dataclass
from typing import Dict

@dataclass
class Alternative:
    """Модель альтернативы (торговой фирмы)."""
    id: str
    name: str
    scores: Dict[str, float]

@dataclass
class Criterion:
    """Модель критерия."""
    id: str
    name: str
    is_maximize: bool = True