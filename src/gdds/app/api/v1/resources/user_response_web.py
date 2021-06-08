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
from ..models.duplication_list import DupList
from ..models.user_response import UserResponse
from ..schema.input_schema import UserResponseSchema
from gdds.app.api.common.response import STATUS_CODES, MIME_TYPES
from gdds.app.api.common.error_handlers import custom_json_response


# noinspection PyComparisonWithNone,PyUnresolvedReferences
class WebUserResponse(Resource):
    """Flask resource to retrieve user response through Web Portal."""

    @use_kwargs(UserResponseSchema().fields_dict, locations=['json'])
    def post(self, **kwargs):
        """method to update user response through Web Portal."""

        result = self.user_response(kwargs)
        return result

    @staticmethod
    def user_response(kwargs):
        """Static method to extract User response via Web portal """

        try:

            chk_imei = DupList.query.filter(DupList.uid == kwargs['uid']).first()

            if chk_imei and chk_imei.imei in kwargs['user_imeis']:

                chk_uid = UserResponse.query.filter(UserResponse.uid == kwargs['uid'],
                                                    UserResponse.user_serial_no == None).first()
                if chk_uid:
                    chk_uid.user_serial_no = kwargs['user_serial_no'].strip()
                    chk_uid.user_color = kwargs['user_color']
                    chk_uid.user_brand = kwargs['user_brand']
                    chk_uid.user_model = kwargs['user_model']
                    chk_uid.user_imeis = kwargs['user_imeis']
                    chk_uid.user_response_date = strftime("%Y-%m-%d %H:%M:%S")

                    db.session.flush()
                    db.session.commit()

                    return custom_json_response(_("User Response successfully updated"),
                                                STATUS_CODES.get('OK'), MIME_TYPES.get('JSON'))
                else:
                    return custom_json_response(_("UID is not correct or already used"),
                                                STATUS_CODES.get('UNPROCESSABLE_ENTITY'), MIME_TYPES.get('JSON'))
            else:
                return custom_json_response(_("UID is not associated with any of the provided IMEIs"),
                                            STATUS_CODES.get('UNPROCESSABLE_ENTITY'), MIME_TYPES.get('JSON'))

        except Exception as e:
            app.logger.info(_("Error occurred while fetching user response."))
            app.logger.exception(e)
            db.session.rollback()

        finally:
            db.session.close()
