# -*- coding: utf-8 -*-

"""Module containing the representation of the Character class."""

from evennia.utils.evtable import EvTable

from representations.base import BaseRepr

FORM = """
.-------------------------------------------------------------------------.
| Name: xxxxxxxxxxxx1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx |
|                                                                         |
| Statistics:                                                             |
|   Stat  | Name                  | Value | Base  | Mod   | Max           |
|   p_vit | Physical vitality     | xxx2x | xxx3x | xxx4x | xx5x          |
|   p_wea | Physical weariness    | xxx6x | xxx7x | xxx8x | xx9x          |
|   p_str | Physical strength     | xx10x | xx11x | xx12x | x13x          |
|   p_dex | Physical dexterity    | xx14x | xx15x | xx16x | x17x          |
|   p_con | Physical constitution | xx18x | xx19x | xx20x | x21x          |
|   p_sen | Physical sensibility  | xx22x | xx23x | xx24x | x25x          |
|   p_qui | Physical quickness    | xx26x | xx27x | xx28x | x29x          |
|   m_vit | Mental   vitality     | xx30x | xx31x | xx32x | x33x          |
|   m_wea | Mental   weariness    | xx34x | xx35x | xx36x | x37x          |
|   m_pow | Mental   power        | xx38x | xx39x | xx40x | x41x          |
|   m_wil | Mental   willpower    | xx42x | xx43x | xx44x | x45x          |
|   m_int | Mental   intelligence | xx46x | xx47x | xx48x | x49x          |
|   m_cha | Mental   charisma     | xx50x | xx51x | xx52x | x53x          |
|                                                                         |
| Desc: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx |
|       xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx54xxxxxxxxxxxxxxxxxxxxxxxxx |
|       xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx |
|       xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx |
|                                                                         |
.-------------------------------------------------------------------------.
"""

class CharacterRepr(BaseRepr):

    """The character representation."""

    fields = {
            "key": str,
    }
    to_display = ["name",
            "stats.p_vit.current", "stats.p_vit.base", "stats.p_vit.mod", "stats.p_vit.max",
            "stats.p_wea.current", "stats.p_wea.base", "stats.p_wea.mod", "stats.p_wea.max",
            "stats.p_str.current", "stats.p_str.base", "stats.p_str.mod", "stats.p_str.max",
            "stats.p_dex.current", "stats.p_dex.base", "stats.p_dex.mod", "stats.p_dex.max",
            "stats.p_con.current", "stats.p_con.base", "stats.p_con.mod", "stats.p_con.max",
            "stats.p_sen.current", "stats.p_sen.base", "stats.p_sen.mod", "stats.p_sen.max",
            "stats.p_qui.current", "stats.p_qui.base", "stats.p_qui.mod", "stats.p_qui.max",
            "stats.m_vit.current", "stats.m_vit.base", "stats.m_vit.mod", "stats.m_vit.max",
            "stats.m_wea.current", "stats.m_wea.base", "stats.m_wea.mod", "stats.m_wea.max",
            "stats.m_pow.current", "stats.m_pow.base", "stats.m_pow.mod", "stats.m_pow.max",
            "stats.m_wil.current", "stats.m_wil.base", "stats.m_wil.mod", "stats.m_wil.max",
            "stats.m_int.current", "stats.m_int.base", "stats.m_int.mod", "stats.m_int.max",
            "stats.m_cha.current", "stats.m_cha.base", "stats.m_cha.mod", "stats.m_cha.max",
            "desc"]
    form = FORM

    def get_desc(self, caller):
        return self.obj.db.desc
