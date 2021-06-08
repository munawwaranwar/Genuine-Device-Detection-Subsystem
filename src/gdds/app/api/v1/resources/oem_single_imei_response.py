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
from time import strftime
from .....app import db, app
from flask_restful import Resource
from flask_apispec import use_kwargs
from ..models.oem_response import OemResponse
from ..schema.input_schema import OemResponseSchema
from gdds.app.api.common.response import STATUS_CODES, MIME_TYPES
from gdds.app.api.common.error_handlers import custom_json_response


class OemSingleImei(Resource):
    """Flask resource to provide OEM response through Web Portal for single IMEI."""

    @staticmethod
    @use_kwargs(OemResponseSchema().fields_dict, locations=['json'])
    def put(**kwargs):
        """method to get OEM's response for single IMEI."""

        try:
            all_imeis = []

            if kwargs['oem_imei'] in kwargs['oem_other_imeis']:
                return custom_json_response(_("Every IMEI slot must have unique IMEI"),
                                            STATUS_CODES.get('UNPROCESSABLE_ENTITY'), MIME_TYPES.get('JSON'))

            chk_imei = OemResponse.query.filter(OemResponse.oem_imei == kwargs['oem_imei']).first()

            if chk_imei:

                chk_imei.oem_other_imeis = kwargs['oem_other_imeis']
                for imei in kwargs['oem_other_imeis']:
                    all_imeis.append(imei)
                all_imeis.append(kwargs['oem_imei'])

                chk_imei.oem_serial_no = kwargs['oem_serial_no'].strip()
                chk_imei.oem_color = kwargs['oem_color']
                chk_imei.oem_brand = kwargs['oem_brand']
                chk_imei.oem_model = kwargs['oem_model']
                chk_imei.oem_rat = kwargs['oem_rat']
                chk_imei.oem_mac = kwargs['oem_mac']
                chk_imei.oem_all_imeis = all_imeis
                chk_imei.oem_response_date = strftime("%Y-%m-%d %H:%M:%S")

                db.session.flush()
                db.session.commit()

                return custom_json_response(_("Response successfully updated"),
                                            STATUS_CODES.get('OK'), MIME_TYPES.get('JSON'))
            else:
                return custom_json_response(_("IMEI is not correct"),
                                            STATUS_CODES.get('UNPROCESSABLE_ENTITY'), MIME_TYPES.get('JSON'))

        except Exception as e:
            app.logger.info(_("Error occurred while fetching OEM response."))
            app.logger.exception(e)
            db.session.rollback()

        finally:
            db.session.close()
