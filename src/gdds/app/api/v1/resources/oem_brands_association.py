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

from flask_babel import _
from flask_restful import Resource
from flask_apispec import use_kwargs
from .....app import db, app
from ..models.oem_logins import OemLogins
from ..models.oem_response import OemResponse
from ..models.brand_mapping import BrandMapping
from gdds.app.api.common.response import STATUS_CODES, MIME_TYPES
from ..schema.input_schema import AssociateBrandsSchema
from gdds.app.api.common.error_handlers import custom_json_response


class AssociateBrands(Resource):
    """Flask resource to associate brands with OEM Logins"""

    @staticmethod
    @use_kwargs(AssociateBrandsSchema().fields_dict, locations=['json'])
    def post(**kwargs):
        """method to associate brands with OEM Logins."""

        try:
            q1 = OemLogins.query.filter(OemLogins.oem_name == '{}'.format(kwargs['login_name']),
                                        OemLogins.oem_id == '{}'.format(kwargs['login_id']),
                                        OemLogins.oem_status != 'deleted').first()
            if q1:

                associated_brands = [b.brand_name for b in BrandMapping.query.filter(BrandMapping.oem_id == '{}'.
                                                                          format(kwargs['login_id'])).all()]

                diff_brands = list(set(associated_brands) - set(kwargs['brands_list']))

                for b in diff_brands:
                    del_brand = BrandMapping.query.filter(BrandMapping.brand_name == b).first()
                    if del_brand:
                        del_brand.oem_id = None

                for b in kwargs['brands_list']:
                    q2 = BrandMapping.query.filter(BrandMapping.brand_name == '{}'.format(b)).first()

                    if q2:
                        q2.oem_id = q1.oem_id
                        q3 = OemResponse.query.filter(OemResponse.gsma_brand == '{}'.format(q2.brand_name)).all()

                        if q3:
                            for brand in q3:
                                brand.oem_id = q1.oem_id

                    else:
                        return custom_json_response(_("Brand name (%(b_name)s) is not found in DB", b_name=b),
                                                    STATUS_CODES.get('UNPROCESSABLE_ENTITY'), MIME_TYPES.get('JSON'))

                q1.oem_status = "approved"
                db.session.flush()
                db.session.commit()

            else:
                return custom_json_response(_("Login credentials are not correct"),
                                            STATUS_CODES.get('UNPROCESSABLE_ENTITY'), MIME_TYPES.get('JSON'))

            return custom_json_response(_("Brand(s) got successfully associated with OEM Login"),
                                            status=STATUS_CODES.get('OK'),
                                            mimetype=MIME_TYPES.get('JSON'))

        except Exception as e:
            app.logger.info(_("Error occurred while associating brands with OEM."))
            app.logger.exception(e)
            db.session.rollback()

        finally:
            db.session.close()
