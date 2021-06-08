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
from flask_babel import _
from flask import Response
from flask_restful import Resource
from gdds.app import app, db, conf
from gdds.app.api.common.response import STATUS_CODES, MIME_TYPES
from gdds.app.api.v1.models.duplication_list import DupList
from datetime import datetime, timedelta


# noinspection PyComparisonWithNone
class DupListStats(Resource):
    """ Flask resource to provide statistics of uploaded duplication lists """

    @staticmethod
    def get():
        """ Method to provide statistics of uploaded duplication lists """

        try:
            tmp = "duplication_list_Stats"
            duplist_stat = {tmp: {}}

            duplist_stat[tmp]["total_imeis"] = DupList.query.filter().count()

            duplist_stat[tmp]["processed_imeis"] = DupList.query.filter(DupList.imei_status != None).count()

            duplist_stat[tmp]["pending_imeis"] = duplist_stat[tmp]["total_imeis"] - duplist_stat[tmp]["processed_imeis"]

            duplist_stat[tmp]["genuine_imeis"] = DupList.query.filter(DupList.imei_status == True).count()

            duplist_stat[tmp]["duplicated_imeis"] = DupList.query.filter(DupList.imei_status == False).count()

            duplist_stat[tmp]["sms_notified_imeis"] = DupList.query.filter(DupList.sms_notification == True).count()

            duplist_stat[tmp]["sms_awaited_imeis"] = DupList.query.filter(DupList.sms_notification == None).count()

            start_date = (datetime.today() - timedelta(days=conf['threshold_days'])).date()
            duplist_stat[tmp]["threshold_crossed_imeis"] = DupList.query.filter(DupList.list_upload_date < start_date)\
                                                                        .count()

            return Response(json.dumps(duplist_stat),
                            status=STATUS_CODES.get('OK'), mimetype=MIME_TYPES.get('JSON'))

        except Exception as e:
            app.logger.info(_("Error occurred while retrieving Duplication List detail."))
            app.logger.exception(e)
            db.session.rollback()

        finally:
            db.session.close()
