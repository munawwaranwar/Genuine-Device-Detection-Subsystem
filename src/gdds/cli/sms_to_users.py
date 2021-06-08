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

import click
import requests
from ..app import conf
from gdds.app.api.common.db_connection import connect


# noinspection PyUnusedLocal,SqlDialectInspection,SqlNoDataSourceInspection,PyUnboundLocalVariable,PyPep8Naming
@click.command()
@click.argument('sms_to')
def send_sms(sms_to):
    """Sending SMS to all users in duplication_list Table."""

    con = connect()
    cur = con.cursor()

    for mno in conf['mnos']:

        if sms_to == "all":
            cur.execute("""SELECT msisdn, uid, mno, sms_notification FROM duplication_list WHERE imei_status IS NULL AND 
                           mno = '{mno}'; """.format(mno=mno))
        elif sms_to == "unnotified":
            cur.execute("""SELECT msisdn, uid, mno, sms_notification FROM duplication_list WHERE imei_status IS NULL AND
                           sms_notification IS NULL AND mno = '{mno}'; """.format(mno=mno))
        else:
            print("invalid parameter \"{}\" for command \"send-request-sms\" ".format(sms_to))
            return

        msisdns = cur.fetchall()

        print(mno)

        for m in msisdns:
            msisdn = "0" + m[0][2:]

            if m[2] in conf['mnos']:
                MNO_SMSC = m[2]
            else:
                MNO_SMSC = conf['mnos'][0]

            sms = conf['SMS_Text']['initial_sms'] + m[1] + conf['SMS_Text']['link_text']
            sms_intimation(msisdn, sms, MNO_SMSC)

            if m[3] is None:
                cur.execute("""UPDATE duplication_list SET sms_notification = true where uid = '{}' """.format(m[1]))

    con.commit()
    cur.close()
    con.close()

    return


# noinspection PyUnboundLocalVariable,PyPep8Naming
def sms_intimation(num, sms, MNO_SMSC):
    """sending SMS using Kannel gateway"""

    print("Sending SMS to :", num, "\tSMS Text:", sms)

    payload = {'username': conf[MNO_SMSC]['kannel_username'], 'password': conf[MNO_SMSC]['kannel_password'],
               'smsc': conf[MNO_SMSC]['kannel_smsc'], 'from': conf['kannel_shortcode'], 'to': num,
               'text': sms}

    requests.get(conf['kannel_url'], params=payload)

    return
