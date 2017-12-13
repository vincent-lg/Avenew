# -*- coding: utf-8 -*-

"""
Module containing shared classes, usually handlers to be used for objects
with prototypes.

Classes:
    SharedAttributeHandler - share attributes between the objedct and its prototype.

"""

from evennia.typeclasses.attributes import AttributeHandler

class SharedAttributeHandler(AttributeHandler):

    """
    A shared attribute handler, to share attributes between object and prototype.

    The object should have a shared attribute handler in a lazy property,
    overriding `obj.attributes`.  This handler will behave like the
    standard AttributeHandler, except its `has` and `get` methods will
    also query the prototype if the attribute cannot be found.  However,
    one can still write attributes for the specific objects.  Here is
    a small sample: we assume `apple` to be a prototype, and `red_apple`
    to be an object from this prototype:

    >>> red_apple in apple.objs
    True
    >>> red_apple.db.all
    []
    >>> apple.db.all
    [<Attribute 'quality']
    >>> red_apple.db.quality
    3
    >>> # Here, we have gotten the attribute even thoug it's defined in the prototype
    >>> red_apple.db.quality = 5
    >>> red_apple.db.quality
    5
    >>> apple.db.quality
    3
    >>> # The prototype still has its attribute quality set to 3, while the object has a different value
    >>> del red_apple.db.quality
    >>> red_apple.db.quality
    3
    >>> # Back to the prototype value

    """

    def has(self, key=None, category=None):
        """
        Checks if the given Attribute (or list of Attributes) exists on
        the object.

        Args:
            key (str or iterable): The Attribute key or keys to check for.
                If `None`, search by category.
            category (str or None): Limit the check to Attributes with this
                category (note, that `None` is the default category).

        Returns:
            has_attribute (bool or list): If the Attribute exists on
                this object or not. If `key` was given as an iterable then
                the return is a list of booleans.

        """
        ret = super(SharedAttributeHandler, self).has(
                key=key, category=category)
        if isinstance(ret, list):
            # In this case, we just return the list, as it would be
            # too complicated to handle individual checks.
            return ret

        if not ret:
            prototype = AttributeHandler.get(self, "prototype")
            if prototype:
                return prototype.attributes.has(key=key, category=category)

        return ret

    def get(self, key=None, default=None, category=None, return_obj=False,
            strattr=False, raise_exception=False, accessing_obj=None,
            default_access=True, return_list=False):
        """
        Get the Attribute.

        Args:
            key (str or list, optional): the attribute identifier or
                multiple attributes to get. if a list of keys, the
                method will return a list.
            category (str, optional): the category within which to
                retrieve attribute(s).
            default (any, optional): The value to return if an
                Attribute was not defined. If set, it will be returned in
                a one-item list.
            return_obj (bool, optional): If set, the return is not the value of the
                Attribute but the Attribute object itself.
            strattr (bool, optional): Return the `strvalue` field of
                the Attribute rather than the usual `value`, this is a
                string-only value for quick database searches.
            raise_exception (bool, optional): When an Attribute is not
                found, the return from this is usually `default`. If this
                is set, an exception is raised instead.
            accessing_obj (object, optional): If set, an `attrread`
                permission lock will be checked before returning each
                looked-after Attribute.
            default_access (bool, optional): If no `attrread` lock is set on
                object, this determines if the lock should then be passed or not.
            return_list (bool, optional):

        Returns:
            result (any or list): One or more matches for keys and/or categories. Each match will be
                the value of the found Attribute(s) unless `return_obj` is True, at which point it
                will be the attribute object itself or None. If `return_list` is True, this will
                always be a list, regardless of the number of elements.

        Raises:
            AttributeError: If `raise_exception` is set and no matching Attribute
                was found matching `key`.

        """
        ret = super(SharedAttributeHandler, self).get(
                key=key, default=default, category=category,
                return_obj=return_obj, strattr=strattr,
                raise_exception=raise_exception, accessing_obj=accessing_obj,
                default_access=default_access, return_list=return_list)
        if isinstance(ret, list):
            # In this case, we just return the list, as it would be
            # too complicated to handle individual checks.
            return ret

        if ret is None:
            prototype = AttributeHandler.get(self, "prototype")
            if prototype:
                return prototype.attributes.get(key=key, default=default, category=category,
                        return_obj=return_obj, strattr=strattr, raise_exception=raise_exception, accessing_obj=accessing_obj,
                        default_access=default_access, return_list=return_list)

        return ret
