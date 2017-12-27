# -*- coding: utf-8 -*-

"""
Module containing the StatsHandler for characters, and the individual Stats.

You will access the `StatsHandler` through `character.stats`.  From there you will be able to access the stats as objects (not value):
    character.stats.p_vit: the character's physical health/vitality (0-100).
    character.stats.p_tired: physical tiredness (0-200).
    character.stats.p_str: physical strength.
    character.stats.p_dex: physical dexterity.
    character.stats.p_con: physical constitution, can influence health and tiredness.
    character.stats.p_sen: physical sensitivity.
    character.stats.p_qui: physical quickness, agility.
    character.stats.m_vit: mental vitality/health, integrity (0-100).
    character.stats.m_tired: mental stress (0-200).
    character.stats.m_pow: mental power.
    character.stats.m_wil: mental willpower.
    character.stats.m_int: mental intelligence, memory.
    character.stats.m_cha: charisma.

Stats can be manipulated as is.  They can be compared to numbers.
    if character.stats.p_str > 5:
        character.stats.str += 2

But they're really objects with other properties.
    stat.base: get/set the base (a number).
    stat.mod: get/set the modifier, a number. base+mod is the stat current value.
    stat.min: get/set the stat minimum value. A stat cannot go beyond it.
    stat.max: get/set the stat maximum value. A stat cannot go beyond it.

A few examples:
    character.stats.p_str.base # Get the current base of the physical strength
    character.stats.p_str.base = 10 # Modify it
    character.stats.m_cha.mod # Get the modifier for the charisma
    character.stats.m_cha.mod = 2 # Add 2 as a modifier to this stat
    character.stats.p_vit.min # Get the minimum value of p_health (0)
    character.stats.p_vit.max # Get the maximum value of p_health (100 except modifiers)

"""

from evennia.utils.utils import lazy_property

class StatsHandler(object):

    """
    Stats handler, accessible through `character.stats`.

    Most stats are accessible through getters/setters from here, as they
    are properties.  Some additional methods can be used from the handler
    itself.

    """

    defaults = {
        "p_vit": (100, 0, 100),
        "p_tired": (0, 0, 100),
        "p_str": (5, 0, 100),
        "p_dex": (5, 0, 100),
        "p_con": (5, 0, 100),
        "p_sen": (5, 0, 100),
        "p_qui": (5, 0, 100),

        # Mental stats
        "m_vit": (100, 0, 100),
        "m_tired": (0, 0, 100),
        "m_pow": (5, 0, 100),
        "m_wil": (5, 0, 100),
        "m_int": (5, 0, 100),
        "m_cha": (5, 0, 100),
    }

    def __init__(self, character):
        self.character = character
        self._in_cache = {}

    @property
    def p_vit(self):
        """Return the physical vitality of this character."""
        return self._retrieve("p_vit", PVit)
    @p_vit.setter
    def p_vit(self, value):
        """Change the physical vitality."""
        self._error_set("p_vit", value)

    @property
    def p_tired(self):
        """Return the physical tiredness of this character."""
        return self._retrieve("p_tired", StatVarMax)
    @p_tired.setter
    def p_tired(self, value):
        """Change the physical tiredness."""
        self._error_set("p_tired", value)

    @property
    def p_str(self):
        """Return the physical strength of this character."""
        return self._retrieve("p_str")
    @p_str.setter
    def p_str(self, value):
        """Change the physical strength."""
        self._error_set("p_str", value)

    @property
    def p_dex(self):
        """Return the physical dexterity of this character."""
        return self._retrieve("p_dex")
    @p_dex.setter
    def p_dex(self, value):
        """Change the physical dexterity."""
        self._error_set("p_dex", value)

    @property
    def p_con(self):
        """Return the physical constitution of this character."""
        return self._retrieve("p_con")
    @p_con.setter
    def p_con(self, value):
        """Change the physical constitution."""
        self._error_set("p_con", value)

    @property
    def p_sen(self):
        """Return the physical sensitivity of this character."""
        return self._retrieve("p_sen")
    @p_sen.setter
    def p_sen(self, value):
        """Change the physical sensitivity."""
        self._error_set("p_sen", value)

    @property
    def p_qui(self):
        """Return the physical quickness of this character."""
        return self._retrieve("p_qui")
    @p_qui.setter
    def p_qui(self, value):
        """Change the physical quickness."""
        self._error_set("p_qui", value)

    @property
    def m_vit(self):
        """Return the mental vitality of this character."""
        return self._retrieve("m_vit", StatVarMax)
    @m_vit.setter
    def m_vit(self, value):
        """Change the mental vitality."""
        self._error_set("m_vit", value)

    @property
    def m_tired(self):
        """Return the mental tiredness of this character."""
        return self._retrieve("m_tired", StatVarMax)
    @m_tired.setter
    def m_tired(self, value):
        """Change the mental tiredness."""
        self._error_set("m_tired", value)

    @property
    def m_pow(self):
        """Return the mental power of this character."""
        return self._retrieve("m_pow")
    @m_pow.setter
    def m_pow(self, value):
        """Change the mental power."""
        self._error_set("m_pow", value)

    @property
    def m_wil(self):
        """Return the mental willpower of this character."""
        return self._retrieve("m_wil")
    @m_wil.setter
    def m_wil(self, value):
        """Change the mental willpower."""
        self._error_set("m_wil", value)

    @property
    def m_int(self):
        """Return the mental intelligence of this character."""
        return self._retrieve("m_int")
    @m_int.setter
    def m_int(self, value):
        """Change the mental intelligence."""
        self._error_set("m_int", value)

    @property
    def m_cha(self):
        """Return the mental charisma of this character."""
        return self._retrieve("m_cha")
    @m_cha.setter
    def m_cha(self, value):
        """Change the mental charisma."""
        self._error_set("m_cha", value)

    @lazy_property
    def db_read(self):
        """Return the database in which to read only, not write.

        The difference between the `db_read` and `db_write` properties is that
        the latter returns a dictionary in which you can write.  This
        dictionary will be saved as attribute of the character.  The
        former method, on the other hand, will return an empty, not
        editable dictionary, except if the attributes exist.  You should
        call `db_read` only when you need to read from the handler but
        not write in it, for the result will vary depending on whether
        the attribute already exist or not.

        """
        if "db" in self._in_cache:
            return self._in_cache["db"]
        else:
            if not self.character.attributes.has("stats"):
                return {}

            db = self.character.db.stats
            self._in_cache["db"] = db
            return db

    @property
    def db_write(self):
        """Return the dictionary in which you can write.

        See the docstring on `db_read` for details.

        """
        if not self.character.attributes.has("stats"):
            self.character.db.stats = {}

        db = self.character.db.stats
        self._in_cache["db"] = db
        return db

    def _retrieve(self, name, from_class=None, default=None):
        """Retrieve the stat from the cache, or create it."""
        from_class = from_class or Stat
        min = max = None
        if default is None:
            default, min, max = type(self).defaults[name]

        if name in self._in_cache:
            return self._in_cache[name]
        else:
            # Get the stat value, if found
            kwargs = {"base": default, "min": min, "max": max}
            db = self.db_read
            kwargs.update(db.get(name, {}))

            # Create the stat
            stat = from_class(self, name, **kwargs)
            self._in_cache[name] = stat
            return stat

    def _error_set(self, name, value):
        """Raise an exception, cannot set stat like this."""
        raise TypeError("you cannot set the {name} value like this, you " \
                "should use character.stats.{name}.base or " \
                "character.stats.{name}.mod to update either the base or " \
                "mod of this stat.".format(name=name))


class Stat(object):

    """Base class for a Stat representation.

    Stats can be compared and modified directly.  They also provide
    additional properties to access more low-level information, as
    their base value, modifiers, or limits.

    """

    def __init__(self, handler, name, base=10, mod=0, min=None, max=None):
        self.handler = handler
        self.name = name
        self._base = base
        self._mod = mod
        self._min = min
        self._max = max

    @property
    def character(self):
        return self.handler and self.handler.character or None

    def __repr__(self):
        return "<Stat {}={} (base={}, mod={}, min={}, max={}, character={})>".format(
                self.name, self.current, self._base, self._mod, self._min,
                self._max, self.character)

    @property
    def current(self):
        """Return the current stat value, its base + mod."""
        value = self._base + self._mod
        if self._min is not None and value < self._min:
            return self._min
        if self._max is not None and value > self._max:
            return self._max

        return value

    @property
    def base(self):
        """Return the stat base."""
        return self._base
    @base.setter
    def base(self, new_base):
        """Set the stat base."""
        old = self.current
        self._base = new_base
        self._normalize()
        self._save()

        # If the base has changed, call the 'hit' method that can be subclassed
        new = self.current
        if old != new:
            self.hit(old, new)

    @property
    def mod(self):
        """Return the stat mod."""
        return self._mod
    @mod.setter
    def mod(self, new_mod):
        """Set the stat mod."""
        old = self.current
        self._mod = new_mod
        self._save()
        new = self.current
        if old != new:
            self.hit(old, new)

    @property
    def min(self):
        return self._min

    @property
    def max(self):
        return self._max

    def _normalize(self):
        """Normalize the stat so it's neither too small or too high."""
        if self._min is not None and self._base < self._min:
            self._base = self._min
        if self._max is not None and self._base > self._max:
            self._base = self._max

    def _save(self):
        """Save the stat in the handler.

        This should be done automatically and shouldn't have to be called directly.

        """
        handler = self.handler
        db = handler.db_write
        db[self.name] = {
                "base": self._base,
                "mod": self._mod,
        }

        if self._max is not None:
            db[self.name].update({"max": self._max})

    def hit(self, old_value, new_value):
        """The base of this stat has changed.

        Subclass and override this method to implement customized behavior.

        Args:
            old_value (int or float): the stat old value.
            new_value (int or float): the stat's new value.

        """
        pass

    # Mathematic methods
    def __eq__(self, o):
        return self.current == self.number(o)
    def __ne__(self, o):
        return self.current != self.number(o)
    def __lt__(self, o):
        return self.current < self.number(o)
    def __le__(self, o):
        return self.current <= self.number(o)
    def __gt__(self, o):
        return self.current > self.number(o)
    def __ge__(self, o):
        return self.current >= self.number(o)

    @classmethod
    def number(cls, stat):
        """Return, if possible, the object's number to be compared."""
        if isinstance(stat, (int, float)):
            return stat

        return stat.current


class StatVarMax(Stat):

    """A stat with variable max that can be changed through stat.max."""

    @Stat.max.setter
    def max(self, value):
        self._max = value
        if value is not None and self._base > value:
            self._base = value
        self._save()

class PVit(StatVarMax):

    """Physical vitality/health."""

    def hit(self, old_value, new_value):
        """The physical health has changed."""
        character = self.character
        if character:
            if new_value == 0:
                character.die()
            elif old_value == 0:
                character.live()
