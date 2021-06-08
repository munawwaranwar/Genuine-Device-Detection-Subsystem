"""
Copyright (c) 2018-2021 Qualcomm Technologies, Inc.

All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted (subject to the
limitations in the disclaimer below) provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this list of conditions and the following
disclaimer.
* Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
disclaimer in the documentation and/or other materials provided with the distribution.
* Neither the name of Qualcomm Technologies, Inc. nor the names of its contributors may be used to endorse or promote
products derived from this software without specific prior written permission.
* The origin of this software must not be misrepresented; you must not claim that you wrote the original software.
If you use this software in a product, an acknowledgment is required by displaying the trademark/log as per the details
provided here: https://www.qualcomm.com/documents/dirbs-logo-and-brand-guidelines
* Altered source versions must be plainly marked as such, and must not be misrepresented as being the original software.
* This notice may not be removed or altered from any source distribution.

NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED BY
THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
 BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 POSSIBILITY OF SUCH DAMAGE.
"""

from marshmallow import Schema, fields
from gdds.app.api.common.validations import Validations


class BulkUploadSchema(Schema):
    """Marshmallow schema for duplication list input."""

    file = fields.String(required=False)

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields


class ErrorFileSchema(Schema):
    """Marshmallow schema for downloading error files."""

    url = fields.String(required=True)

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields


class KeyclockSchema(Schema):
    """Marshmallow schema for Keyclock API's parameters."""

    login_name = fields.String(required=True, validate=Validations.validate_login_name)
    login_id = fields.String(required=True, validate=Validations.validate_login_id)
    login_status = fields.String(required=True, validate=Validations.validate_login_status)

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields


class BrandSearchSchema(Schema):
    """Marshmallow schema for searching brand names."""

    search = fields.String(required=False, missing=None)
    start = fields.Integer(required=True)
    limit = fields.Integer(required=True)

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields


class AssociateBrandsSchema(Schema):
    """Marshmallow schema for Keyclock API's parameters."""

    login_name = fields.String(required=True, validate=Validations.validate_login_name)
    login_id = fields.String(required=True, validate=Validations.validate_login_id)
    brands_list = fields.List(fields.String(required=True, validate=Validations.validate_brands), required=True,
                              validate=Validations.validate_brands_list)

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields


class AssociatedBrandsSchema(Schema):
    """Marshmallow schema for searching brand names."""

    login_id = fields.String(required=True, validate=Validations.validate_login_id)

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields


class UserResponseSchema(Schema):
    """Marshmallow schema for User response."""

    class Meta:
        strict = True
    uid = fields.String(required=True)
    user_serial_no = fields.String(required=True, validate=Validations.device_serial_no)
    user_imeis = fields.List(fields.String(required=True, validate=Validations.validate_imei), required=True,
                              validate=Validations.validate_imei_list)
    user_color = fields.String(required=True, validate=Validations.device_color)
    user_brand = fields.String(required=True, validate=Validations.validate_brands)
    user_model = fields.String(required=True, validate=Validations.device_model)

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields


class OemResponseSchema(Schema):
    """Marshmallow schema for User response."""
    oem_imei = fields.String(required=True, validate=Validations.validate_imei)
    oem_other_imeis = fields.List(fields.String(required=False, validate=Validations.validate_imei), required=False,
                                  missing=[])
    oem_serial_no = fields.String(required=True, validate=Validations.device_serial_no)
    oem_color = fields.String(required=True, validate=Validations.device_color)
    oem_brand = fields.String(required=True, validate=Validations.validate_brands)
    oem_model = fields.String(required=True, validate=Validations.device_model)
    oem_rat = fields.String(required=True, validate=Validations.validate_rat)
    oem_mac = fields.String(required=False, missing="00:00:00:00", validate=Validations.validate_mac)

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields


class OemHomePageSchema(Schema):
    """Marshmallow schema for parameters of OEM home page."""

    login_id = fields.String(required=True, validate=Validations.validate_login_id)
    start = fields.Integer(required=True)
    limit = fields.Integer(required=True)

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields


class BulkImeisSchema(Schema):
    """Marshmallow schema for Bulk imeis download"""

    login_name = fields.String(required=True, validate=Validations.validate_login_name)
    login_id = fields.String(required=True, validate=Validations.validate_login_id)

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields


class DetailedResponseSchema(Schema):
    """Marshmallow schema for parameters of Duplication-List Table API """

    filter = fields.String(required=True, validate=Validations.validate_filter)
    start = fields.Integer(required=True)
    limit = fields.Integer(required=True)

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields
