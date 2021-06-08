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
import os
import magic
import click
import tempfile
import pandas as pd
from shutil import rmtree
from ..app import conf, app
from gdds.app.api.common.db_connection import connect


# noinspection PyUnusedLocal
@click.command()
@click.argument('path', type=click.Path(exists=False))
def update(path):
    """update brand_mapping table with new brands via GSMA TAC data."""

    t_path, filename = path.rsplit('/', 1)
    result = GsmaTacData.list_update(t_path, filename)
    click.echo(result)


# noinspection SqlDialectInspection,SqlNoDataSourceInspection,PyUnboundLocalVariable
class GsmaTacData:
    """class for OEM segregation via updating brand_mapping table."""

    @staticmethod
    def list_update(f_path, filename):
        """method to accept and process gsma_tac_data file and update the brand_mapping table"""

        try:
            if Miscellaneous.file_allowed(filename):
                filepath = os.path.join(f_path, filename)
                tmp_dir = tempfile.mkdtemp()
                temp_path = os.path.join(tmp_dir, filename)
                print("Reading file .................................")
                filetype = magic.from_file(filepath, mime=True)

                if filename != '' and filetype == 'text/plain':
                    try:
                        spaces = ['', ' ', '  ', '   ', '    ', '     ', '      ', '       ', '        ', '         ']
                        with open(filepath, 'r') as newfile:
                            df = pd.read_csv(newfile, sep='|', dtype=dict(TAC=str), na_values=spaces,
                                             keep_default_na=True)
                        newfile.close()
                    except Exception as e:
                        if e:
                            newfile.close()
                            return "File content is not Correct", 403

                    if not df.empty:
                        df['Manufacturer'] = df['Manufacturer'].str.strip()

                        df1 = df[df['Manufacturer'].isnull()]  # to detect null values in any column
                        df3 = df[~(df.TAC.astype(str).str.match(conf['validation_regex']['tac']))]
                        if df1.empty and df3.empty:

                            con = connect()
                            cur = con.cursor()
                            Miscellaneous.create_temp_table(cur)

                            df.to_csv(temp_path, index=False, header=False, sep='|')

                            with open(temp_path, 'r') as f:
                                cur.copy_from(f, 'test_gsma_tac_data', sep='|')
                            f.close()

                            Miscellaneous.copy_temp_table(cur)
                            cur.execute("""drop table if exists test_gsma_tac_data; """)
                            # Miscellaneous.brands_mapper(cur)

                            print("File processing started ..............................")

                            cur.execute("""SELECT DISTINCT manufacturer FROM gsma_tac_data; """)
                            t_manufacturer = cur.fetchall()
                            manufacturer = Miscellaneous.manufacturer_modifications(t_manufacturer)

                            cur.execute("""SELECT brand_name FROM brand_mapping; """)
                            tmp_brands = cur.fetchall()
                            brands = [t[0] for t in tmp_brands]

                            t_brands = list(set(manufacturer) - set(brands))
                            new_brands = set(t_brands)

                            print("---------------------------------------------")
                            print("New Brands to insert :")

                            for b in new_brands:
                                cur.execute("""INSERT INTO brand_mapping(brand_name) VALUES ('{}'); """.format(b))
                                print(b)

                            print("---------------------------------------------")
                            print("Total New Brands added : ", len(new_brands))
                            print("---------------------------------------------")

                            con.commit()
                            cur.close()
                            con.close()

                            return "GSMA TAC Database successfully updated", 200
                        else:
                            return "File contains Invalid TACs or Manufacturer names", 403
                    else:
                        return "GSMA-TAC File is empty", 403
                else:
                    return "System only accepts csv/txt files", 403
            else:
                return "Please select csv/txt file", 422

        except Exception as e:
            app.logger.info("Error occurred while processing TAC-Data-File.")
            app.logger.exception(e)

        finally:
            rmtree(tmp_dir)

        return


# noinspection SqlDialectInspection,SqlNoDataSourceInspection,SpellCheckingInspection
class Miscellaneous:
    """Class to provide different support methods """

    @staticmethod
    def file_allowed(filename):
        return '.' in filename and filename.rsplit('.', 1)[1] in conf['allowed_extensions']

    @staticmethod
    def manufacturer_modifications(brand_names):
        result = []
        for names in brand_names:
            b_name = names[0]
            b_name = b_name.strip()
            result.append((re.sub(r'\W+', ' ', b_name)).lower())
        return result

    @staticmethod
    def create_temp_table(cur):
        """Method to create temporary Table for GSMA TAC Data."""
        cur.execute("""create Table test_gsma_tac_data (
                        tac VARCHAR(8) UNIQUE ,
                        marketing_name text,
                        manufacturer text NOT NULL,
                        bands text,
                        FiveG_Bands text,
                        LPWAN text,
                        allocation_date text,
                        country_code text,
                        fixed_code text,
                        manufacturer_code text,
                        radio_interface text,
                        brand_name text,
                        model_name text,
                        operating_system text,
                        nfc_value text,
                        bluetooth text,
                        wlan text,
                        device_type text,
                        oem text,
                        removable_uicc text,
                        removable_euicc text,
                        nonremovable_uicc text,
                        nonremovable_euicc text,
                        simslot text,
                        imeiquantitysupport text);
                    """)
        return

    @staticmethod
    def copy_temp_table(cur):
        """Method to update/insert GSMA TAC data via test_gsma_tac_data table"""

        cur.execute("""insert into gsma_tac_data(tac,  Marketing_Name,  Manufacturer, Bands, FiveG_Bands, LPWAN, 
                        Allocation_Date, Country_Code, Fixed_Code, Manufacturer_Code, Radio_Interface, Brand_Name, 
                        Model_Name, Operating_System, NFC_value, Bluetooth, WLAN, Device_Type, OEM, Removable_UICC, 
                        Removable_EUICC, NonRemovable_UICC, NonRemovable_EUICC,  Simslot, Imeiquantitysupport) 
                        select TAC,  Marketing_Name,  Manufacturer, Bands, FiveG_Bands, LPWAN, Allocation_Date, 
                        Country_Code, Fixed_Code, Manufacturer_Code, Radio_Interface, Brand_Name, Model_Name, 
                        Operating_System, NFC_value, Bluetooth, WLAN, Device_Type, OEM, Removable_UICC, Removable_EUICC,
                        NonRemovable_UICC, NonRemovable_EUICC, Simslot, Imeiquantitysupport 
                        from test_gsma_tac_data 
                        on conflict (tac)
                        do nothing; """)
        return

    @staticmethod
    def brands_mapper(cur):
        """Method to upload/update brand_mapping table with new brands from GSMA TAC DATA."""

        cur.execute("""INSERT INTO brand_mapping(brand_name)
                       SELECT DISTINCT Manufacturer
                       FROM gsma_tac_data
                       ON CONFLICT (brand_name)
                       DO NOTHING;
                    """)
        return
