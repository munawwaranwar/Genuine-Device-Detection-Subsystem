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
from gdds.app.api.common.db_connection import connect


# noinspection SqlDialectInspection,SqlNoDataSourceInspection
@click.command()
def compare():
    """Running comparison-algorithm to compare & evaluate user & oem responses."""

    print("Running Comparison........")
    con = connect()
    cur = con.cursor()

    cur.execute("""select distinct user_response.uid, user_response.user_imeis, 
                                   oem_response.oem_serial_no, oem_response.oem_all_imeis
                        from oem_response
                        INNER JOIN user_response
                        ON user_response.user_serial_no = oem_response.oem_serial_no
                        AND user_response.user_imeis @> oem_response.oem_all_imeis
                        AND user_response.user_imeis <@ oem_response.oem_all_imeis
                        AND oem_response.oem_all_imeis @> user_response.user_imeis
                        AND oem_response.oem_all_imeis <@ user_response.user_imeis
                        AND user_response.uid_status is NULL
                """)

    serial_nos = cur.fetchall()

    for row in serial_nos:
        c = set(row[3]) == set(row[1])

        if c:
            cur.execute("""UPDATE duplication_list SET imei_status = TRUE where uid = '{u}' """.format(u=row[0]))
            cur.execute("""UPDATE user_response SET uid_status = TRUE where uid = '{u}' """.format(u=row[0]))
        else:
            cur.execute("""UPDATE duplication_list SET imei_status = FALSE where uid = '{u}' """.format(u=row[0]))
            cur.execute("""UPDATE user_response SET uid_status = FALSE where uid = '{u}' """.format(u=row[0]))

    cur.execute("""UPDATE duplication_list SET imei_status = FALSE
                    FROM user_response
                    WHERE user_response.uid = duplication_list.uid
                    AND duplication_list.imei_status IS NULL
                    AND user_response.user_serial_no IS NOT NULL;
                """)

    cur.execute("""UPDATE duplication_list SET imei_status = null
                    FROM oem_response
                    WHERE oem_response.oem_imei = duplication_list.imei
                    AND duplication_list.imei_status = FALSE 
                    AND oem_response.oem_serial_no IS NULL;
                """)

    cur.execute("""UPDATE user_response SET uid_status = duplication_list.imei_status
                    FROM duplication_list
                    WHERE user_response.uid = duplication_list.uid
                    AND user_response.uid_status IS NULL
                    AND duplication_list.imei_status IS NOT NULL;
                """)

    con.commit()
    cur.close()
    con.close()

    return
