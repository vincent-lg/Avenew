# Copyright (c) 2020-20201, LE GOFF Vincent
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
# OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.

"""Blueprint document for objects."""

from data.base import db
from data.blueprints.document import Document
from data.blueprints.exceptions import DelayMe
from data.blueprints.models.objects.types.abc import DOC_SUBTYPES

class ObjectDocument(Document):

    """Object document to add objects in blueprints."""

    doc_type = "object"
    doc_dump = True
    fields = {
        "prototype": {
            "type": "str",
            "presence": "required",
        },
        "barcode": {
            "type": "str",
            "presence": "required",
        },
        "location": {
            "type": "external",
            "presence": "required",
        },
        "types": {
            "type": "subset",
            "document_type": ...,
            "presence": "required",
        },
    }

    def fill_from_object(self, obj):
        """Draw the document from an object."""
        self.cleaned.prototype = obj.prototype.barcode
        self.cleaned.barcode = obj.barcode
        self.cleaned.location = self.deduce_external(obj.location)

        # Browse types
        self.cleaned.types = []
        for obj_type in obj.types:
            doc_type = DOC_SUBTYPES.get(obj_type.name)
            assert doc_type, f"The document for {obj_type.name} wasn't found"
            doc = doc_type(None)
            doc.fill_from_object(obj_type)
            attrs = doc.object_dictionary
            attrs["type"] = obj_type.name
            self.cleaned.types.append(attrs)

    def register(self):
        """Register the object for the blueprint."""
        self.object = None
        if (obj := db.Object.get(
                barcode=self.cleaned.barcode)):
            self.object = obj
            self.blueprint.objects[obj] = self
            return (obj, )

        return ()

    def apply(self):
        """Apply the document, spawn objects in the room."""
        barcode = self.cleaned.barcode
        prototype = db.ObjectPrototype.get(barcode=self.cleaned.prototype)
        location = self.get_external(self.cleaned.location)
        if prototype is None or location is None:
            raise DelayMe

        # If the object already exists, do nothing.
        obj = db.Object.get(barcode=barcode)
        if obj is None:
            obj = prototype.create_at(location, barcode=barcode)

        # Apply the object types
        for obj_type in self.cleaned.types:
            name = obj_type.pop("type", None)
            assert name, "The object type hasn't been set in this document"
            doc_type = DOC_SUBTYPES.get(name)
            assert doc_type, f"The document for {name} wasn't found"
            doc = doc_type(self.blueprint)
            doc.fill_for_objects(obj_type)
            try:
                doc.apply_object(obj)
            except DelayMe:
                raise DelayDocument(prototype)

