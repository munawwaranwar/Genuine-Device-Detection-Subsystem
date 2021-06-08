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

import os
import click
from flask_babel import _
from time import strftime
from ..app import app, conf
from gdds.app.api.common.db_connection import connect


# noinspection SqlDialectInspection,SqlNoDataSourceInspection,PyPep8Naming
@click.command()
def generate():
    """Creating Black-List & Pairing-List from Duplication_list Table."""

    try:
        DOWNLOAD_PATH = conf['GDDS_Lists']
        con = connect()
        cur = con.cursor()

        cur.execute("""SELECT imei FROM duplication_list WHERE imei_status IS FALSE """)
        imei_list = set([l[0] for l in cur.fetchall()])

        if imei_list:
            black_list = "Black-List_" + strftime("%Y-%m-%d_%H-%M-%S") + '.csv'
            bl_path = os.path.join(DOWNLOAD_PATH, black_list)

            with open(bl_path, 'w') as bl:
                bl.write('imei,reason\n')
                for imei in imei_list:
                    bl.write(imei + ',duplicated\n')
                    # bl.write(",duplicated\n".join(imei_list))

            bl.close()

        pair_list = "Pair-List_" + strftime("%Y-%m-%d_%H-%M-%S") + '.csv'
        pl_path = os.path.join(DOWNLOAD_PATH, pair_list)

        if conf['pair_list_triplet']: params = "imei,imsi,msisdn"
        else: params = "imei,imsi"

        cur.execute("""SELECT {p} FROM duplication_list WHERE imei_status IS TRUE """.format(p=params))
        pairs = cur.fetchall()

        with open(pl_path, 'w') as file:
            file.write(params + '\n')
            for row in pairs:
                if conf['pair_list_triplet']:
                    file.write(row[0] + ',' + row[1] + ',' + row[2] + '\n')
                else:
                    file.write(row[0] + ',' + row[1] + '\n')

        file.close()

        print("Files successfully created")

        return

    except Exception as e:
        app.logger.info(_("Error occurred creating Lists."))
        app.logger.exception(e)
