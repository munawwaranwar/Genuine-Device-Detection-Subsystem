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
from gdds.app.api.common.response import *
from ..models.oem_logins import OemLogins
from ..models.brand_mapping import BrandMapping
from ..schema.input_schema import KeyclockSchema
from gdds.app.api.common.error_handlers import custom_json_response


class KeyClockInput(Resource):
    """Flask resource to record/update keyclock users."""

    @staticmethod
    @use_kwargs(KeyclockSchema().fields_dict, locations=['json'])
    def post(**kwargs):
        """method to store/update OEM-keyclock logins."""

        try:
            l_name = kwargs['login_name'].lower()
            user_name = OemLogins.query.filter(OemLogins.oem_name == l_name).first()
            user_id = OemLogins.query.filter(OemLogins.oem_id == kwargs['login_id']).first()

            if not user_name and not user_id:

                if kwargs['login_status'] == 'apply':
                    add_login = OemLogins(oem_name=l_name,
                                          oem_id=kwargs['login_id'],
                                          keyclock_status=kwargs['login_status'],
                                          oem_status='new-request')
                    db.session.add(add_login)
                else:
                    return custom_json_response(_("login does not exist"),
                                                STATUS_CODES.get('UNPROCESSABLE_ENTITY'), MIME_TYPES.get('JSON'))
            else:

                if kwargs['login_status'] == 'delete':
                    user_name.oem_status = 'deleted'
                    user_name.keyclock_status = kwargs['login_status']

                    del_id = OemLogins.query.filter(OemLogins.oem_name == '{}'.format(l_name)).first()

                    if del_id.oem_id == kwargs['login_id']:
                        d_brands = BrandMapping.query.filter(BrandMapping.oem_id == '{}'.format(del_id.oem_id)).all()
                        for d in d_brands:
                            d.oem_id = None
                    else:
                        return custom_json_response(_("login ID does not exist"),
                                                    STATUS_CODES.get('UNPROCESSABLE_ENTITY'), MIME_TYPES.get('JSON'))

                elif kwargs['login_status'] == 'apply':
                    return custom_json_response(_("login name or id already exists"),
                                                STATUS_CODES.get('FORBIDDEN'), MIME_TYPES.get('JSON'))

            db.session.flush()
            db.session.commit()

            return custom_json_response(_("Login request is accepted. Approval from Authority is pending"),
                                        STATUS_CODES.get('OK'), MIME_TYPES.get('JSON'))

        except Exception as e:
            app.logger.info("Error occurred while retrieving keyclock information.")
            app.logger.exception(e)
            db.session.rollback()

        finally:
            db.session.close()
