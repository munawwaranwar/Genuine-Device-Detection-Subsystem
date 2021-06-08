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

from flask import request
from flask_restful import Resource
from marshmallow import ValidationError
from gdds.app.api.v2.schema.input_schema import USSDSchema
from gdds.app.api.common.response import STATUS_CODES, MIME_TYPES
from gdds.app.api.v1.schema.input_schema import UserResponseSchema
from gdds.app.api.common.error_handlers import custom_text_response
from gdds.app.api.v1.resources.user_response_web import WebUserResponse


class GddsUssd(Resource):
    """Flask Resource to access and handle USSD parameters"""

    @staticmethod
    def get():

        kwargs = request.args
        try:
            USSDSchema().load(kwargs)
        except ValidationError as e:
            err = []
            for v in e.messages.values():
                err.append(v[0])

            return custom_text_response(err, status=STATUS_CODES.get('UNPROCESSABLE_ENTITY'),
                                        mimetype=MIME_TYPES.get('TEXT'))

        sms_text = kwargs['msg_text'].split(',')

        if len(sms_text) == 7:

            uid, serial_no, color, brand, model = sms_text[1], sms_text[2], sms_text[4], sms_text[5], sms_text[6]
            imeis = sms_text[3].split('|')

            params = {"uid": uid, "user_serial_no": serial_no, "user_imeis": imeis, "user_color": color,
                      "user_brand": brand, "user_model": model}
            try:
                UserResponseSchema().load(params)
            except ValidationError as e:
                err = []
                for k, v in e.messages.items():
                    if k == "user_imeis" and isinstance(v, list):
                        err.append("Maximum 5 IMEIs per device is allowed")
                    elif k == "user_imeis" and isinstance(v, dict):
                        err.append("IMEI(s) format is not correct")
                    else:
                        err.append(v[0])

                return custom_text_response(err, status=STATUS_CODES.get('UNPROCESSABLE_ENTITY'),
                                            mimetype=MIME_TYPES.get('TEXT'))

            ur = WebUserResponse()
            result = ur.user_response(params)
            return result
        else:
            return "USSD did not provide all the required 7 parameters"
