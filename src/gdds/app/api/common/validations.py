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

import re
from gdds.app import conf
from flask_babel import _
from marshmallow import ValidationError


class Validations:
    """Class for input validations."""

    @staticmethod
    def validate_msisdn(msisdn):
        """Validates MSISDN format."""
        match_msisdn = re.match(conf['validation_regex']['msisdn'], msisdn)
        if match_msisdn is None:
            raise ValidationError(_('MSISDN format is not correct'))
        return match_msisdn.string

    @staticmethod
    def validate_login_name(l_name):
        """Validates Login-name"""

        if l_name is None or l_name == "":
            raise ValidationError(_('Login-Name can not be left empty'))

    @staticmethod
    def validate_login_id(l_id):
        """Validates Login-id"""

        if l_id is None or l_id == "":
            raise ValidationError(_('Login-ID can not be left empty'))

    @staticmethod
    def validate_login_status(l_status):
        """Validates Login-status"""

        if l_status not in conf['keyclock_statuses']:
            raise ValidationError(_('Login Status is not correct'))

    @staticmethod
    def validate_brands(brand):
        """Validates Brand Name."""
        match_brand = re.match(conf['regex'][conf['supported_languages']['default_language']]['brand'], brand)
        if match_brand is None:
            raise ValidationError(_('Brand name is not correct'))

    @staticmethod
    def validate_brands_list(b_list):
        """Validates at-least one brand name exists"""

        if len(b_list) == 0:
            raise ValidationError(_('At least one brand name is required'))

    @staticmethod
    def validate_imei(imei):
        """Validates IMEIs"""

        match_imei = re.fullmatch(conf['validation_regex']['imei'], imei)
        if match_imei is None:
            raise ValidationError(_('IMEI is not correct'))

    @staticmethod
    def validate_imei_list(imei_list):
        """Validates at-least one IMEI exists"""

        if len(imei_list) == 0:
            raise ValidationError(_('At least one IMEI is required'))
        elif len(imei_list) > 5:
            raise ValidationError(_('Maximum 5 IMEIs per device is allowed'))

    @staticmethod
    def device_serial_no(serial_no):
        """Validates format of Serial_no and also makes sure that at-least one serial-no exists"""

        if serial_no is None or serial_no == "" or len(serial_no.strip()) == 0:
            raise ValidationError(_('Serial number is missing'))

    @staticmethod
    def device_color(color):
        """Validates at-least one color exists"""

        match_color = re.match(conf['regex'][conf['supported_languages']['default_language']]['model_color'], color)
        if match_color is None:
            raise ValidationError(_('Color name is not correct'))

    @staticmethod
    def device_model(model):
        """Validates at-least one model name exists"""

        match_model = re.match(conf['regex'][conf['supported_languages']['default_language']]['model_name'], model)
        if match_model is None:
            raise ValidationError(_('Model name is not correct'))

    @staticmethod
    def validate_filter(response_filter):
        """Validates DupList-filter must belong to pre-defined List of filters."""

        if response_filter not in ["all_imeis", "processed_imeis", "pending_imeis", "genuine_imeis", "duplicated_imeis",
                                  "threshold_crossed_imeis", "sms_notified_imeis", "sms_pending_imeis", "pending_uids",
                                  "responded_uids", "responded_processed_uids", "responded_unprocessed_uids",
                                  "responded_imeis"]:

            raise ValidationError(_('Filter Value is not correct'))

    @staticmethod
    def validate_rat(rat):
        """Validates RAT Name."""
        match_rat = re.match(conf['validation_regex']['rat'], rat)
        if match_rat is None:
            raise ValidationError(_('RAT is not correct'))

    @staticmethod
    def validate_mac(mac):
        """Validates MAC address."""

        if mac is not "" or not mac or mac is not None:
            match_mac = re.match(conf['validation_regex']['mac'], mac)
            if match_mac is None:
                raise ValidationError(_('MAC format is not correct'))

    @staticmethod
    def validate_operator(operator):
        """Validates Operator Name."""
        if operator not in conf['mnos']:
            raise ValidationError(_('Operator name is not correct'))

    @staticmethod
    def validate_keyword(key):
        """ Validates technology used"""

        if key not in conf['allowed_keywords']:
            raise ValidationError(_('USSD Keyword is not supported'))
