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

from gdds.app import db
from sqlalchemy import CheckConstraint


class GsmaDb(db.Model):
    """ Class to create DB table gsma_tac_data """

    __tablename__ = 'gsma_tac_data'

    id = db.Column(db.BIGINT, primary_key=True, autoincrement=True)
    tac = db.Column(db.Text, CheckConstraint('tac > 7'), unique=True)
    marketing_name = db.Column(db.Text)
    manufacturer = db.Column(db.Text, nullable=False)
    bands = db.Column(db.Text)
    fiveg_bands = db.Column(db.Text)
    lpwan = db.Column(db.Text)
    allocation_date = db.Column(db.Text)
    country_code = db.Column(db.Text)
    fixed_code = db.Column(db.Text)
    manufacturer_code = db.Column(db.Text)
    radio_interface = db.Column(db.Text)
    brand_name = db.Column(db.Text)
    model_name = db.Column(db.Text)
    operating_system = db.Column(db.Text)
    nfc_value = db.Column(db.Text)
    bluetooth = db.Column(db.Text)
    wlan = db.Column(db.Text)
    device_type = db.Column(db.Text)
    oem = db.Column(db.Text)
    removable_uicc = db.Column(db.Text)
    removable_euicc = db.Column(db.Text)
    nonremovable_uicc = db.Column(db.Text)
    nonremovable_euicc = db.Column(db.Text)
    simslot = db.Column(db.Text)
    imeiquantitysupport = db.Column(db.Text)

    # CheckConstraint('char_length(tac) > 7', name='tac_length_chk')
