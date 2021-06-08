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

import json
from flask_babel import _
from flask import Response
from flask_restful import Resource
from flask_apispec import use_kwargs
from .....app import db, app
from ..models.oem_response import OemResponse
from ..schema.input_schema import OemHomePageSchema
from gdds.app.api.common.response import STATUS_CODES, MIME_TYPES


# noinspection PyComparisonWithNone
class OemHomePage(Resource):
    """Flask resource to populate all IMEIs on OEM Portal """

    @staticmethod
    @use_kwargs(OemHomePageSchema().fields_dict, locations=['querystring'])
    def get(**kwargs):
        """method to get all IMEIs related to provided OEM whose response is pending."""

        try:

            imei_list = []
            chk_count = OemResponse.query.filter(OemResponse.oem_id == kwargs['login_id'],
                                                 OemResponse.oem_serial_no == None).count()
            chk_imeis = OemResponse.query.filter(OemResponse.oem_id == kwargs['login_id'],
                                                 OemResponse.oem_serial_no == None).offset(kwargs['start'])\
                                                 .limit(kwargs['limit']).all()

            if chk_imeis:

                for c in chk_imeis:
                    imei_list.append(c.oem_imei)

            return Response(json.dumps({"IMEIs": imei_list, "count": chk_count}),
                            status=STATUS_CODES.get('OK'), mimetype=MIME_TYPES.get('JSON'))

        except Exception as e:
            app.logger.info(_("Error occurred while fetching OEM IMEIs."))
            app.logger.exception(e)
            db.session.rollback()

        finally:
            db.session.close()
