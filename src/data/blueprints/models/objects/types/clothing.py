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

"""Blueprint document for the clothing type."""

from data.base import db
from data.blueprints.document import Document
from data.blueprints.exceptions import DelayMe

class ClothingTypeDocument(Document):

    """Blueprint for the clothing object type."""

    doc_type = "clothing"
    doc_dump = False
    fields = {}
    fields_for_prototypes = {
        "protection": {
            "type": "int",
            "presence": "required",
        },
    }
    fields_for_objects = {
        "max_protection": {
            "type": "int",
            "presence": "required",
        },
    }

    @property
    def prototype_dictionary(self):
        """Return the dictionary for prototypes."""
        return {
                "protection": self.cleaned.protection,
        }

    @property
    def object_dictionary(self):
        """Return the dictionary for objects."""
        return {
                "max_protection": self.cleaned.max_protection,
        }

    def fill_for_prototypes(self, document):
        """Fill a document for object prototypes."""
        return super().fill(document, type(self).fields_for_prototypes)

    def fill_for_objects(self, document):
        """Fill a document for objects."""
        return super().fill(document, type(self).fields_for_objects)

    def fill_from_prototype(self, obj_type):
        """Fill the object for a prototype."""
        self.cleaned.protection = obj_type.db.protection

    def fill_from_object(self, obj_type):
        """Fill the object for an object."""
        self.cleaned.max_protection = obj_type.db.max_protection

    def apply_prototype(self, prototype=None):
        """Apply the document."""
        with prototype.db.if_necessary as db:
            db.protection = self.cleaned.protection

    def apply_object(self, obj=None):
        """Apply the document."""
        with obj.db.if_necessary as db:
            db.max_protection = self.cleaned.max_protection
