# -*- coding: utf-8 -*-

"""
Module containing shared classes, usually handlers to be used for objects
with prototypes.

Classes:
    SharedAttributeHandler - share attributes between the objedct and its prototype.

"""

import time

from evennia.typeclasses.attributes import AttributeHandler

class AvenewObject(object):

    """Mix-in containing shared behavior that all typeclasses in the Avenew game should use."""

    @property
    def location(self):
        return super(AvenewObject, self)._ObjectDB__location_get()
    @location.setter
    def location(self, location):
        old_location = self.location
        super(AvenewObject, self)._ObjectDB__location_set(location)
        self.db._moved_at = time.time()

        # Update the former location's content
        if old_location and hasattr(old_location, "ndb"):
            old_location.ndb._cached_contents = old_location.contents_cache.get(exclude=None)
            old_location.ndb._cached_contents.sort(key=lambda obj: obj.attributes.get("_moved_at", 0))

        # Update the location's contents (sort it and cache it)
        if location and hasattr(location, "ndb"):
            location.ndb._cached_contents = location.contents_cache.get(exclude=None)
            location.ndb._cached_contents.sort(key=lambda obj: obj.attributes.get("_moved_at", 0))
    @location.deleter
    def location(self):
        super(AvenewObject, self)._ObjectDB__location_del()

    def contents_get(self, exclude=None):
        """
        Returns the contents of this object, i.e. all
        objects that has this object set as its location.
        This should be publically available.

        Args:
            exclude (Object): Object to exclude from returned
                contents list

        Returns:
            contents (list): List of contents of this Object.

        Notes:
            Also available as the `contents` property.
            We had ordering of objects.

        """
        if self.ndb._cached_contents is not None:
            return self.ndb._cached_contents
        else:
            con = self.contents_cache.get(exclude=exclude)
            con.sort(key=lambda obj: obj.attributes.get("_moved_at", 0))
            self.ndb._cached_contents = con
            return con
    contents = property(contents_get)

    @property
    def mass(self):
        """Return the mass and these of contents."""
        mass = self.db.mass
        if mass is None:
            mass = 1

        return reduce(lambda x, y: x + y.mass, [mass] + self.contents)

    @property
    def locations(self):
        """
        Return the list of location of this object.

        Return the list of location, then locatio.location, and so on util
        None is reached.

        """
        locations = []
        obj = self
        while obj is not None:
            obj = obj.location
            if obj is not None:
                locations.append(obj)

        return locations

    def get_display_name(self, looker, **kwargs):
        """
        Displays the name of the object in a viewer-aware manner.

        Args:
            looker (TypedObject): The object or account that is looking
                at/getting inforamtion for this object.

        Returns:
            name (str): A string containing the name of the object,
                including the DBREF if this user is privileged to control
                said object.

        """
        if self.locks.check_lockstring(looker, "perm(Builder)"):
            return "{}(#{})".format(self.name, self.id)
        return self.name

    def get_numbered_name(self, count, looker):
        """
        Return the numbered (singular or plural) name of this object. This is by default called
        by return_appearance and is used for grouping multiple same-named of this object.

        Args:
            count (int): Number of objects of this singular name to group.
            looker (Object): Onlooker.

        Returns:
            name (str): the appropriate name (singular or plural).

        """
        singular = self.get_display_name(looker)
        plural = self.attributes.get("plural", "things")
        return singular if count < 2 else "{} {}".format(count, plural)

    def search(self, searchdata, candidates=None, **kwargs):
        """
        Returns an Object matching a search string/condition

        Perform a standard object search in the database, handling
        multiple results and lack thereof gracefully. By default, only
        objects in the current `location` of `self` or its inventory are searched for.

        Args:
            searchdata (str or obj): Primary search criterion. Will be matched
                against `object.key` (with `object.aliases` second) unless
                the keyword attribute_name specifies otherwise.
                **Special strings:**
                - `#<num>`: search by unique dbref. This is always
                   a global search.
                - `me,self`: self-reference to this object
                - `<num>-<string>` - can be used to differentiate
                   between multiple same-named matches
            global_search (bool): Search all objects globally. This is overruled
                by `location` keyword.
            use_nicks (bool): Use nickname-replace (nicktype "object") on `searchdata`.
            typeclass (str or Typeclass, or list of either): Limit search only
                to `Objects` with this typeclass. May be a list of typeclasses
                for a broader search.
            location (Object or list): Specify a location or multiple locations
                to search. Note that this is used to query the *contents* of a
                location and will not match for the location itself -
                if you want that, don't set this or use `candidates` to specify
                exactly which objects should be searched.
            attribute_name (str): Define which property to search. If set, no
                key+alias search will be performed. This can be used
                to search database fields (db_ will be automatically
                prepended), and if that fails, it will try to return
                objects having Attributes with this name and value
                equal to searchdata. A special use is to search for
                "key" here if you want to do a key-search without
                including aliases.
            quiet (bool): don't display default error messages - this tells the
                search method that the user wants to handle all errors
                themselves. It also changes the return value type, see
                below.
            exact (bool): if unset (default) - prefers to match to beginning of
                string rather than not matching at all. If set, requires
                exact matching of entire string.
            candidates (list of objects): this is an optional custom list of objects
                to search (filter) between. It is ignored if `global_search`
                is given. If not set, this list will automatically be defined
                to include the location, the contents of location and the
                caller's contents (inventory).
            nofound_string (str):  optional custom string for not-found error message.
            multimatch_string (str): optional custom string for multimatch error header.
            use_dbref (bool or None, optional): if True/False, active/deactivate the use of
                #dbref as valid global search arguments. If None, check against a permission
                ('Builder' by default).

        Returns:
            match (Object, None or list): will return an Object/None if `quiet=False`,
                otherwise it will return a list of 0, 1 or more matches.

        """
        if candidates is None:
            candidates = self.location.contents
            if hasattr(self, "equipment"):
                candidates += self.equipment.all(only_visible=True)

        return super(AvenewObject, self).search(searchdata, candidates=candidates, **kwargs)


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
                key=key, default=None, category=category,
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
