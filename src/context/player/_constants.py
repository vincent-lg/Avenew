"""Constants for the player contexts."""

from enum import Enum

class Mood(Enum):

    """Different moods."""

    SOBER = "sérieux"
    BUSINESSLIKE = "professionnel"
    TIRED = "fatigué"
    BRUTAL = "brutal"
    POLITE = "poli"

class Pronoun(Enum):

    """Available pronouns."""

    HIM = "il"
    SHE = "elle"
    UNKNOWN = "iel"
