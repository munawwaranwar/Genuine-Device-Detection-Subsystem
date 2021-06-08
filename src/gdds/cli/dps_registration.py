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


import requests
import click
from ..app import app, conf
from gdds.app.api.common.db_connection import connect


# noinspection SqlNoDataSourceInspection,SqlResolve
@click.command()
def register():

    click.echo("DPS PROCESS Initiated")
    try:
        con = connect()
        cur = con.cursor()
        dps_api_params = {"params_list": []}
        params = {}

        cur.execute("""SELECT imei, msisdn FROM duplication_list WHERE imei_status = true 
                    AND export_status IS NOT TRUE """)
        qry_dup = cur.fetchall()

        if qry_dup:
            for q in qry_dup:

                params['contact_no'] = q[1]
                cur.execute("""SELECT oem_serial_no, oem_brand, oem_model, oem_mac, oem_rat, oem_all_imeis 
                                FROM oem_response 
                                WHERE oem_imei = '{imei}'
                                """.format(imei=q[0]))
                qry_oem = cur.fetchall()
                for o in qry_oem:
                    params["serial_no"] = o[0]
                    params["brand"] = o[1]
                    params["model"] = o[2]
                    params["mac"] = o[3]
                    params["rat"] = o[4]
                    params["imei"] = o[5]
                    dps_api_params["params_list"].append(dict(params))

            headers = {'content-type': 'application/json'}
            for p in dps_api_params["params_list"]:
                # print(type(p), p)
                print("Registering device having IMEI(s) '{imei}' for MSISDN '{msisdn}' with DPS....".
                      format(imei=p["imei"], msisdn=p['contact_no']))

                result = requests.post(url=conf['dps_api'], json=p, headers=headers)
                print(result.status_code, result.text, "\n")

            # pprint.pprint(dps_api_params)
        else:
            click.echo("No genuine IMEI exists in DB !!!")

        cur.execute("""UPDATE duplication_list SET export_status = TRUE  WHERE imei_status = TRUE 
                            AND export_status IS NOT TRUE """)

        con.commit()
        cur.close()
        con.close()

    except Exception as e:
        app.logger.info("Error occurred creating Lists.")
        app.logger.exception(e)
