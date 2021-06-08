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
import uuid
import magic
import click
import tempfile
import pandas as pd
from shutil import rmtree
from time import strftime
from ..app import conf, app
from gdds.app.api.common.brandname_formatter import BrandsModifier
from gdds.app.api.common.db_connection import connect


DOWNLOAD_FOLDER = conf['Download_Path']


# noinspection PyUnusedLocal
@click.command()
# @click.argument('file', nargs=1, type=click.File())
@click.argument('duplication_list', type=str)
@click.argument('path', type=click.Path(exists=True))
def process(duplication_list, path):
    """Accepts the Duplication-List from DIRBS-CORE & Process it."""

    print("Processing File ...........")
    t_path, filename = path.rsplit('/', 1)
    result = DuplicationListProcessor.list_processor(t_path, filename)
    click.echo(result)


# noinspection DuplicatedCode,PyUnusedLocal,SqlDialectInspection,SqlNoDataSourceInspection,PyUnboundLocalVariable
class DuplicationListProcessor:
    """Class for processing duplication List from Core."""

    @staticmethod
    def list_processor(f_path, filename):
        """method to accept & process duplication List."""

        try:
            if file_allowed(filename):
                filepath = os.path.join(f_path, filename)
                tmp_dir = tempfile.mkdtemp()
                temp_path = os.path.join(tmp_dir, filename)
                try:
                    filetype = magic.from_file(filepath, mime=True)

                    if filename != '' and filetype == 'text/plain':
                        try:
                            with open(filepath, 'r') as newfile:
                                df = pd.read_csv(newfile, usecols=range(4), dtype=dict(imei=str, imsi=str,
                                                                                       msisdn=str, operator=str))
                            newfile.close()
                        except Exception as e:
                            if e:
                                newfile.close()
                                return "File content is not Correct", 403

                        total_rows, total_columns = df.shape

                        if df.columns[0] == 'imei' and df.columns[1] == 'imsi' and df.columns[2] == 'msisdn' and \
                                df.columns[3] == 'operator':

                            if not df.empty:
                                df['imei'] = df['imei'].str.strip()
                                df['imsi'] = df['imsi'].str.strip()
                                df['msisdn'] = df['msisdn'].str.strip()
                                df['operator'] = df['operator'].str.strip()

                                df1 = df[df.isnull().any(axis=1)]   # to detect null values in any column
                                df2 = df.dropna()                   # to drop rows with one or more null values
                                df3 = df2[~(df2.msisdn.astype(str).str.match(conf['validation_regex']['msisdn']))]
                                df2 = df2[(df2.msisdn.astype(str).str.match(conf['validation_regex']['msisdn']))]
                                df4 = df2[~(df2.imei.astype(str).str.match(conf['validation_regex']['imei']))]
                                df2 = df2[(df2.imei.astype(str).str.match(conf['validation_regex']['imei']))]
                                df5 = df2[~(df2.imsi.astype(str).str.match(conf['validation_regex']['imsi']))]
                                df2 = df2[(df2.imsi.astype(str).str.match(conf['validation_regex']['imsi']))]

                                final_rows, final_columns = df2.shape
                                del_rec = (total_rows - final_rows)

                                df2['uid'] = [str(uuid.uuid4())[24:] for x in range(len(df2))] + \
                                             df2['msisdn'].str[-6:]

                                df2.to_csv(temp_path, index=False, header=False)

                                lst_df = [df1, df3, df4, df5]
                                dfs = pd.concat(lst_df, ignore_index=False)

                                con = connect()
                                cur = con.cursor()

                                cur.execute(""" CREATE TABLE if not exists test_list (imei VARCHAR(50), 
                                                                                      imsi VARCHAR(50), 
                                                                                      msisdn VARCHAR(50), 
                                                                                      operator VARCHAR(200), 
                                                                                      uid VARCHAR(50), 
                                                                                      t_time TIMESTAMP) """)
                                con.commit()
                                f = open(temp_path)

                                cur.copy_from(f, 'test_list', sep=",", columns=('imei', 'imsi', 'msisdn',
                                                                                       'operator', 'uid'))
                                con.commit()
                                f.close()

                                OemImeis.imeis_loader()

                                cur.execute(""" drop table if exists test_list;""")
                                con.commit()
                                cur.close()
                                con.close()

                                if del_rec != 0:
                                    error_file = "Error-File_" + strftime("%Y-%m-%d_%H-%M-%S") + '.csv'
                                    download_path = os.path.join(DOWNLOAD_FOLDER, error_file)
                                    with open(download_path, 'w') as ff:
                                        dfs.to_csv(download_path, index=False)

                                    return "Duplication-List loaded successfully\nTotal_Records : {}\n" \
                                           "Successful_Records : {}\nDeleted_Record : {}\n" \
                                           "link to Error-File : {}".format(total_rows, final_rows, del_rec,
                                                                            download_path)
                                else:
                                    return "Duplication-List loaded successfully without errors", 200
                            else:
                                return "File is empty", 403
                        else:
                            return "File headers are incorrect", 403
                    else:
                        return "System only accepts csv/txt files", 403
                finally:
                    rmtree(tmp_dir)
            else:
                return "Please select csv/txt file", 422

        except Exception as e:
            app.logger.info("Error occurred while processing duplication-list.")
            app.logger.exception(e)
            cur.close()
            con.close()
            return "Failed to process Duplication-List.", 422


# noinspection SqlDialectInspection,SqlNoDataSourceInspection
class OemImeis:
    """Class for loading unique IMEIs for OEMs."""

    @staticmethod
    def imeis_loader():
        """method to load unique IMEIs for OEMs."""

        con = connect()
        cur = con.cursor()

        cur.execute("""INSERT INTO oem_response(oem_imei, oem_tac)
                       SELECT DISTINCT imei, LEFT(imei, 8)
                       FROM test_list
                       ON CONFLICT (oem_imei)
                       DO NOTHING;
                    """)

        cur.execute("""INSERT INTO duplication_list(imei, imsi, msisdn, mno, uid)
                        SELECT imei, imsi, msisdn, operator, uid
                        FROM test_list;
                    """)

        cur.execute("""UPDATE duplication_list SET list_upload_date = '{lud}'
                        WHERE imei IS NOT NULL; """.format(lud=strftime("%Y-%m-%d %H:%M:%S")))

        cur.execute("""INSERT INTO user_response(uid)
                        SELECT uid
                        FROM test_list
                        ON CONFLICT (uid)
                        DO NOTHING;
                    """)

        cur.execute("""UPDATE oem_response SET gsma_brand = gsma_tac_data.manufacturer
                        FROM gsma_tac_data
                        WHERE oem_response.oem_tac = gsma_tac_data.tac 
                        AND oem_response.oem_id IS NULL;
                    """)

        cur.execute("""select gsma_brand from oem_response where oem_id is null; """)
        t_brands = cur.fetchall()

        if t_brands:
            for t in t_brands:
                brand = BrandsModifier.manufacturer_modifications(t)
                cur.execute("""update oem_response set gsma_brand = '{b}' where gsma_brand = '{g}';""".format(b=brand,
                                                                                                              g=t[0]))

            cur.execute("""UPDATE oem_response SET oem_id = brand_mapping.oem_id
                            FROM brand_mapping
                            WHERE oem_response.gsma_brand = brand_mapping.brand_name
                            AND oem_response.oem_id IS NULL;
            """)
        con.commit()
        cur.close()
        con.close()

        return


def file_allowed(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in conf['allowed_extensions']
