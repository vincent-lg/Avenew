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

"""Blueprint document for object prototypes."""

from typing import Optional

from data.base import db
from data.blueprints.document import Document
from data.blueprints.exceptions import BlueprintAlert, DelayMe, DelayDocument
from data.blueprints.models.objects.types.abc import DOC_SUBTYPES
import settings

class ObjectPrototypeDocument(Document):

    """Object prototype document to add object prototypes in blueprints."""

    doc_type = "object_proto"
    doc_dump = True
    fields = {
        "barcode": {
            "type": "str",
            "presence": "required",
        },
        "singular": {
            "type": "str",
            "presence": "required",
        },
        "plural": {
            "type": "str",
            "presence": "required",
        },
        "description": {
            "type": "str",
            "presence": "required",
        },
        "types": {
            "type": "subset",
            "document_type": ...,
        },
    }

    def fill_from_object(self, prototype):
        """Draw the document from an object."""
        self.cleaned.barcode = prototype.barcode
        self.cleaned.singular = prototype.names.singular
        self.cleaned.plural = prototype.names.plural
        self.cleaned.description = prototype.description.text

        # Browse types
        self.cleaned.types = []
        for obj_type in prototype.types:
            doc_type = DOC_SUBTYPES.get(obj_type.name)
            assert doc_type, f"The document for {obj_type.name} wasn't found"
            doc = doc_type(None)
            doc.fill_from_prototype(obj_type)
            attrs = doc.prototype_dictionary
            attrs["type"] = obj_type.name
            self.cleaned.types.append(attrs)

    def register(self):
        """Register the object for the blueprint."""
        self.object = None
        if (prototype := db.ObjectPrototype.get(
                barcode=self.cleaned.barcode)):
            self.object = prototype
            self.blueprint.objects[prototype] = self
            return (prototype, )

        return ()

    def apply(self):
        """Apply the document, create a prototype."""
        prototype = self.object
        if prototype is None:
            prototype = db.ObjectPrototype(barcode=self.cleaned.barcode)
            prototype.blueprints.add(self.blueprint.name)

        self.object = prototype
        self.blueprint.objects[prototype] = self
        prototype.names.singular = self.cleaned.singular
        prototype.names.plural = self.cleaned.plural
        description = self.cleaned.description
        if description:
            prototype.description.set(description)

        # Add the types
        for obj_type in self.cleaned.types:
            name = obj_type.pop("type", None)
            assert name, "The object type hasn't been set in this document"
            doc_type = DOC_SUBTYPES.get(name)
            assert doc_type, f"The document for {name} wasn't found"
            doc = doc_type(self.blueprint)
            doc.fill_for_prototypes(obj_type)
            try:
                doc.apply_prototype(prototype)
            except DelayMe:
                raise DelayDocument(prototype)
