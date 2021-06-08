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
import magic
import tempfile
import pandas as pd
from time import strftime
from shutil import rmtree
from flask_babel import _
from flask import request
from .....app import conf, app
from gdds.app.api.common.response import *
from flask_restful import Resource
from flask_apispec import use_kwargs
from werkzeug.utils import secure_filename
from gdds.app.api.common.db_connection import connect
from ..schema.input_schema import BulkUploadSchema
from gdds.app.api.common.error_handlers import custom_json_response, custom_text_response


DOWNLOAD_FOLDER = conf['Download_Path']


# noinspection PyUnusedLocal,SqlDialectInspection
class OemBulkUpload(Resource):
    """Flask resource to upload OEM Response as a file."""

    # noinspection SqlNoDataSourceInspection
    @staticmethod
    @use_kwargs(BulkUploadSchema().fields_dict, locations=['form'])
    def put():
        """method to check and upload a file."""

        try:

            file = request.files.get('file')
            if file and file_allowed(file.filename):
                tmp_dir = tempfile.mkdtemp()
                filename = secure_filename(file.filename)
                filepath = os.path.join(tmp_dir, filename)
                file.save(filepath)
                try:
                    filetype = magic.from_file(filepath, mime=True)

                    if filename != '' or filetype == 'text/plain':
                        try:
                            with open(filepath, 'r') as newfile:
                                df = pd.read_csv(newfile, usecols=range(8), dtype={"IMEI": str, "Serial_no": str,
                                                                                   "Color": str, "Brand": str,
                                                                                   "Model": str, "RAT": str,
                                                                                   "MAC": str, "Other_IMEIs": str})
                            newfile.close()
                        except Exception as e:
                            if e:
                                newfile.close()
                                return custom_json_response(_("File content is not Correct"),
                                                            STATUS_CODES.get('FORBIDDEN'), MIME_TYPES.get('JSON'))

                        total_rows, total_columns = df.shape

                        if df.columns[0] == 'IMEI' and df.columns[1] == 'Serial_no' and df.columns[2] == 'Color' and \
                           df.columns[3] == 'Brand' and df.columns[4] == 'Model' and df.columns[5] == 'RAT' and \
                           df.columns[6] == 'MAC' and df.columns[7] == 'Other_IMEIs':

                            if not df.empty:
                                df['Serial_no'] = df['Serial_no'].str.strip()
                                df1 = df[df.isnull().any(axis=1)]   # to detect null values in any column
                                # df2 = df.dropna()                   # to drop rows with one or more null values
                                df2 = df
                                df3 = df2[~(df2.IMEI.astype(str).str.match(conf['validation_regex']['imei']))]
                                df2 = df2[(df2.IMEI.astype(str).str.match(conf['validation_regex']['imei']))]
                                df4 = df2[~(df2.Serial_no.astype(str).str.match(conf['validation_regex']['serial_no']))]
                                df2 = df2[(df2.Serial_no.astype(str).str.match(conf['validation_regex']['serial_no']))]

                                final_rows, final_columns = df2.shape
                                del_rec = (total_rows - final_rows)
                                df2.to_csv(filepath, index=False, header=False)

                                lst_df = [df1, df3, df4]
                                dfs = pd.concat(lst_df, ignore_index=False)

                                con = connect()
                                filename1 = os.path.join(tmp_dir, filename)
                                cur = con.cursor()

                                cur.execute(""" CREATE TABLE if not exists test_response (t_imei text, t_serial text,
                                            t_color text, t_brand text, t_model text, t_rat text, t_mac text, 
                                            t_other_imeis text)""")

                                f = open(filename1)
                                cur.copy_from(f, 'test_response', sep=",")

                                cur.execute("""UPDATE oem_response SET oem_serial_no = test_response.t_serial,
                                             oem_color = test_response.t_color, oem_brand = test_response.t_brand, 
                                             oem_model = test_response.t_model, oem_rat = test_response.t_rat,
                                             oem_mac = test_response.t_mac, 
                                             oem_other_imeis = string_to_array(test_response.t_other_imeis, '|'), 
                                             oem_response_date = '{}' 
                                             FROM test_response
                                             WHERE oem_imei = test_response.t_imei""".
                                            format(strftime("%Y-%m-%d %H:%M:%S")))

                                cur.execute("""UPDATE oem_response SET oem_all_imeis = array_append(oem_other_imeis, 
                                                                                                    oem_imei)
                                               FROM test_response
                                               WHERE oem_imei = test_response.t_imei """)

                                cur.execute(""" drop table if exists test_response;  """)
                                con.commit()

                                cur.close()
                                con.close()
                                f.close()

                                if del_rec != 0:
                                    error_file = "Error-File" + strftime("%Y-%m-%d_%H-%M-%S") + '.csv'
                                    download_path = os.path.join(DOWNLOAD_FOLDER, error_file)
                                    file.save(download_path)
                                    dfs.to_csv(download_path, index=False)
                                    rtn_msg = {
                                        "msg": _("Duplication-List loaded successfully"),
                                        "Total_Records": total_rows,
                                        "Successful_Records": final_rows,
                                        "Deleted_Record": del_rec,
                                        "link": download_path
                                    }

                                    return custom_text_response(rtn_msg, STATUS_CODES.get('OK'), MIME_TYPES.get('JSON'))
                                else:
                                    return custom_json_response(_("File loaded successfully without errors"),
                                                                STATUS_CODES.get('OK'), MIME_TYPES.get('JSON'))
                            else:
                                return custom_json_response(_("File is empty"),
                                                            STATUS_CODES.get('FORBIDDEN'), MIME_TYPES.get('JSON'))
                        else:
                            return custom_json_response(_("File headers are incorrect"),
                                                        STATUS_CODES.get('FORBIDDEN'), MIME_TYPES.get('JSON'))
                    else:
                        return custom_json_response(_("System only accepts csv/txt files"),
                                                    STATUS_CODES.get('FORBIDDEN'), MIME_TYPES.get('JSON'))

                finally:
                    rmtree(tmp_dir)

            else:
                return custom_json_response(_("Please select csv/txt file"),
                                            STATUS_CODES.get('UNPROCESSABLE_ENTITY'),
                                            MIME_TYPES.get('JSON'))

        except Exception as e:
            app.logger.info("Error occurred while uploading a file")
            app.logger.exception(e)
            return custom_json_response(_("Failed to upload a file."),
                                        STATUS_CODES.get('SERVICE_UNAVAILABLE'),
                                        MIME_TYPES.get('JSON'))


def file_allowed(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in conf['allowed_extensions']
