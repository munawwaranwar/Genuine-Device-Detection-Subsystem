"""
Copyright (c) 2018-2019 Qualcomm Technologies, Inc.

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
from ..app.api.v1.common.db_connection import connect


# noinspection PyUnusedLocal,SqlDialectInspection,SqlNoDataSourceInspection
@click.command()
@click.argument('user_type')
def intimation(user_type):
    """Sending SMS to all users in duplication_list Table on the basis of their IMEI Status."""

    con = connect()
    cur = con.cursor()

    if user_type == "duplicated":
        cur.execute("""SELECT imei, msisdn, imei_status, mno FROM duplication_list WHERE imei_status IS FALSE; """)
        qry = cur.fetchall()

        for q in qry:

            sms = "Your IMEI '{imei}' is marked duplicated and will be blocked in next 24 hours".format(imei=q[0])

            kannel_sms(q[1], sms, q[3])

    elif user_type == "genuine":
        cur.execute("""SELECT imei, msisdn, imei_status, mno FROM duplication_list WHERE imei_status IS TRUE; """)
        qry = cur.fetchall()

        for q in qry:

            sms = "Your IMEI '{imei}' is declared Genuine and will be paired in next 24 hours".format(imei=q[0])

            kannel_sms(q[1], sms, q[3])

    else:
        print("invalid parameter \"{}\" for command \"send-intimation-sms\" ".format(user_type))

    con.commit()
    cur.close()
    con.close()

    return


# noinspection PyPep8Naming
def kannel_sms(num, sms, mno):
    """sending SMS using Kannel gateway"""

    MNO_SMSC = ""
    msisdn = "0" + num[2:]
    print("Sending SMS to :", msisdn, "\tSMS Text:", sms)

    if mno == 'jazz':
        MNO_SMSC = "MNO_1_SMSC"
    elif mno == 'telenor':
        MNO_SMSC = "MNO_2_SMSC"
    elif mno == 'ufone':
        MNO_SMSC = "MNO_3_SMSC"
    elif mno == 'zong':
        MNO_SMSC = "MNO_4_SMSC"

    payload = {'username': conf[MNO_SMSC]['kannel_username'], 'password': conf[MNO_SMSC]['kannel_password'],
               'smsc': conf[MNO_SMSC]['kannel_smsc'], 'from': conf['kannel_shortcode'], 'to': num,
               'text': sms}

    requests.get(conf['kannel_url'], params=payload)

    return
