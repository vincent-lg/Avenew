# -*- coding: utf-8 -*-

"""
Module containing the list of available limbs.  The equipment system will
review this list of limbs, to find a list that matches the character
(all characters should have a list of limbs) but if not found, characters
are believeved to have a custom list of limbs.

The 'limbs' persistent attribute set on a character determines the name
(all capital) that should be retrieved from this module.  For instance,
if `character.db.limbs == "HUMAN"`, then the `HUMAN` variable is sought in
this module (`logic.characters.limbs.HUMAN`).  To add new lists of limbs,
simply add a new variable in this module (the name should be all capitals)
containing a list of `Limb` (see the examples below).  On the other hand,
if you want, from the game itself, to customize what a character can wear,
you will be able to create a custom list of limbs without editing code.

"""

class Limb:

    """
    A class to represent a limb.

    This is more like a data class to represent a limb.  The lists given below should contain only Limb object.

    A `Limb` object can have the following data that you can set at init:
        key (str): the English key of the limb without special character or
                space.  Once set, it shouldn't change, for worn objects will
                use this key to mark themselves as worn on a specific limb.
                It should also be unique in a list of limbs (two lims can't
                have the same key).  See 'group' for a way to group lims.
        name (str): the name of the limb, could be English or another
                language.  Contrary to the key, it can change afterward
                without problem.
        group (str, optional): a way to identify groups.  If not set, this
                will be set as the limb key.  You can use it to group
                several limbs together.  That would make some objects
                wearable on one limb or another in this group.  Hands are
                a common example.  While you should create two limbs
                (left_hand and right_hand for instance), you could
                set both of their groups to "hands".  Then you would
                create a sword that can be worn on "hands" and will be
                effectively worn either on the left or right hand.
        cover (list of keys): the optional list of other limb keys this
                limb covers.  Once a character wears something on this
                limb, it will automatically hide the limbs set in this list.
                For instance, you could have a limb of key "undershirt" and
                another one "shirt" with `cover` set to ["undershirt"].
                Characters can wear something as undershirt, but if they
                also wear another object as a shirt, the undershirt will
                disappear (although they'll still wear it and will still
                be able to see it on themselves, contrary to other characters,
                who won't see the undershirt when looking at them).
        can_hold (bool, optional): can this limb hold something?  Usually
                only used for hands.  A limb with this flag set to True can
                get something with this limb.

    """

    def __init__(self, key, name, group=None, cover=None, can_hold=False, msg=None):
        group = group or key
        cover = cover or []
        self.key = key
        self.name = name
        self.group = group
        self.cover = cover
        self.can_hold = can_hold
        self.msg = msg or "on {pronoun} {limb}"

    def __repr__(self):
        return "<Limb {!r}>".format(self.key)

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.key)

    def __eq__(self, other):
        """Just compare hashes."""
        return hash(self) == hash(other)

    def msg_wear(self, doer, obj):
        """
        Display a formatted text to doer and doer's location when doer wears obj.

        Args:
            doer (Object): the object (character) wearing the object.
            obj (Object): the object being worn.

        The `msg` attribute is used and formatted with these information:
            {limb} is replaced with `self.name`
            {pronoun} is replaced with "yours" (for the message sent to the doer)
                    and "their" (for the message sent to the doer's location)

        """
        doer.msg(("You wear {obj} " + self.msg + ".").format(limb=self.name, pronoun="your", obj=obj.get_display_name(doer)))
        doer.location.msg_contents(("{{doer}} wears {{obj}} " + self.msg + ".").format(limb=self.name, pronoun="their"), mapping=dict(doer=doer, obj=obj), exclude=[doer])

    def msg_hold(self, doer, obj):
        """
        Display a formatted text to doer and doer's location when doer holds obj.

        Args:
            doer (Object): the object (character) holding the object.
            obj (Object): the object being held.

        The `msg` attribute is used and formatted with these information:
            {limb} is replaced with `self.name`
            {pronoun} is replaced with "yours" (for the message sent to the doer)
                    and "their" (for the message sent to the doer's location)

        """
        doer.msg("You take {obj} in {pronoun} {limb}.".format(limb=self.name, pronoun="your", obj=obj.get_display_name(doer)))
        doer.location.msg_contents("{doer} takes {obj} in {pronoun} {limb}.", mapping=dict(doer=doer, obj=obj, limb=self.name, pronoun="their"))


# Lists of limbs
# To add a list of limbs, just create a new variable (all capital like a
# constant) and set it to a list, each element should be a `Limb` object.
# You can change the order of limbs in this list afterwards, or add a new
# limb.  You shouldn't remove a limb from this list if at least one
# character uses it.  You should not change the key of any limb in the
# following lists (once set, don't change the key, it's an identifier).

## Human and humanoid
HUMAN = [
        Limb("head", "tête"),
        Limb("left_hand", "main gauche", group="hands", can_hold=True),
        Limb("right_hand", "main droite", group="hands", can_hold=True),
        Limb("legs", "jambes"),
        # notice that we don't define left_leg and right_leg as both limbs
        # are grouped (hard to wear something different on either legs)
        Limb("left_stocking", "pied gauche", group="stockings"),
        Limb("right_stocking", "pied droit", group="stockings"),
        Limb("left_shoe", "pied gauche", group="shoes", cover=["left_stocking"]),
        Limb("right_shoe", "pied droit", group="shoes", cover=["right_stocking"]),
]

