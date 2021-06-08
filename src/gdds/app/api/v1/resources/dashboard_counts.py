
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

import json
from flask import Response
from gdds.app import db, app
from flask_restful import Resource
from gdds.app.api.v1.models.oem_logins import OemLogins
from gdds.app.api.v1.models.gsma_tac_data import GsmaDb
from gdds.app.api.v1.models.brand_mapping import BrandMapping
from gdds.app.api.common.response import STATUS_CODES, MIME_TYPES


class DashboardCounts(Resource):
    """Flask resource to retrieve Dashboard Counts"""

    @staticmethod
    def get():
        """method to get Dashboard Counts"""

        try:
            brand_count, approved_logins, pending_logins, total_tacs = dashboard_counts("counters")

            return Response(json.dumps({"unique_brands": brand_count, "total_tacs": total_tacs,
                                        "approved_logins": approved_logins, "pending_logins": pending_logins}),
                            status=STATUS_CODES.get('OK'), mimetype=MIME_TYPES.get('JSON'))

        except Exception as e:
            app.logger.info("Error occurred while retrieving dashboard counts.")
            app.logger.exception(e)
            db.session.rollback()

        finally:
            db.session.close()


# noinspection PyComparisonWithNone
def dashboard_counts(purpose):
    """ To fetch different counters for Dashboard """

    brand_count = BrandMapping.query.filter().distinct(BrandMapping.brand_name).count()
    approved_logins = OemLogins.query.filter(OemLogins.oem_status == 'approved').count()
    pending_logins = OemLogins.query.filter(OemLogins.oem_status == 'new-request').count()
    total_tacs = GsmaDb.query.filter().count()

    if purpose is "counters":
        return brand_count, approved_logins, pending_logins, total_tacs

    else:
        total_oems = OemLogins.query.filter().count()
        deleted_oems = OemLogins.query.filter(OemLogins.oem_status == 'deleted').count()
        associated_brands = BrandMapping.query.filter(BrandMapping.oem_id != None).count()
        unassociated_brands = brand_count - associated_brands

        return brand_count, approved_logins, pending_logins, total_tacs, total_oems, deleted_oems, associated_brands,\
               unassociated_brands
