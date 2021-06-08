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
from gdds.app import app, db, conf
from flask_restful import Resource
from flask_apispec import use_kwargs
from datetime import datetime, timedelta
from gdds.app.api.common.error_handlers import custom_json_response
from gdds.app.api.v1.models.duplication_list import DupList
from gdds.app.api.v1.schema.input_schema import DetailedResponseSchema
from gdds.app.api.common.response import STATUS_CODES, MIME_TYPES


# noinspection PyComparisonWithNone
class DupListDetails(Resource):
    """Flask resource to provide detailed Information of Duplication-List Table"""

    @staticmethod
    @use_kwargs(DetailedResponseSchema().fields_dict, locations=['querystring'])
    def get(**kwargs):
        """ Method to provide detailed Information of Duplication-List Table """

        try:

            if kwargs['filter'] == "all_imeis":

                total_count = db.session.query(DupList).count()

                qry = [d for d in db.session.query(DupList).order_by(DupList.id).offset(kwargs['start'])
                                            .limit(kwargs['limit']).all()]

                search = row_formatter(qry)
                search["total_count"] = total_count

                return Response(json.dumps(search), status=STATUS_CODES.get('OK'), mimetype=MIME_TYPES.get('JSON'))

            elif kwargs['filter'] == "processed_imeis":

                total_count = DupList.query.filter(DupList.imei_status != None).count()

                qry = DupList.query.filter(DupList.imei_status != None).order_by(DupList.id).offset(kwargs['start'])\
                                   .limit(kwargs['limit']).all()

                search = row_formatter(qry)
                search["total_count"] = total_count

                return Response(json.dumps(search), status=STATUS_CODES.get('OK'), mimetype=MIME_TYPES.get('JSON'))

            elif kwargs['filter'] == "pending_imeis":

                total_count = DupList.query.filter(DupList.imei_status == None).count()

                qry = DupList.query.filter(DupList.imei_status == None).order_by(DupList.id).offset(kwargs['start']) \
                                   .limit(kwargs['limit']).all()

                search = row_formatter(qry)
                search["total_count"] = total_count

                return Response(json.dumps(search), status=STATUS_CODES.get('OK'), mimetype=MIME_TYPES.get('JSON'))

            elif kwargs['filter'] == "genuine_imeis":

                total_count = DupList.query.filter(DupList.imei_status == True).count()

                qry = DupList.query.filter(DupList.imei_status == True).order_by(DupList.id).offset(kwargs['start']) \
                                   .limit(kwargs['limit']).all()

                search = row_formatter(qry)
                search["total_count"] = total_count

                return Response(json.dumps(search), status=STATUS_CODES.get('OK'), mimetype=MIME_TYPES.get('JSON'))

            elif kwargs['filter'] == "duplicated_imeis":

                total_count = DupList.query.filter(DupList.imei_status == False).count()

                qry = DupList.query.filter(DupList.imei_status == False).order_by(DupList.id).offset(kwargs['start']) \
                                   .limit(kwargs['limit']).all()

                search = row_formatter(qry)
                search["total_count"] = total_count

                return Response(json.dumps(search), status=STATUS_CODES.get('OK'), mimetype=MIME_TYPES.get('JSON'))

            elif kwargs['filter'] == "sms_notified_imeis":

                total_count = DupList.query.filter(DupList.sms_notification == True).count()

                qry = DupList.query.filter(DupList.sms_notification == True).order_by(DupList.id)\
                                   .offset(kwargs['start']).limit(kwargs['limit']).all()

                search = row_formatter(qry)
                search["total_count"] = total_count

                return Response(json.dumps(search), status=STATUS_CODES.get('OK'), mimetype=MIME_TYPES.get('JSON'))

            elif kwargs['filter'] == "sms_pending_imeis":

                total_count = DupList.query.filter(DupList.sms_notification == None).count()

                qry = DupList.query.filter(DupList.sms_notification == None).order_by(DupList.id)\
                                   .offset(kwargs['start']).limit(kwargs['limit']).all()

                search = row_formatter(qry)
                search["total_count"] = total_count

                return Response(json.dumps(search), status=STATUS_CODES.get('OK'), mimetype=MIME_TYPES.get('JSON'))

            elif kwargs['filter'] == "threshold_crossed_imeis":

                start_date = (datetime.today() - timedelta(days=conf['threshold_days'])).date()

                total_count = DupList.query.filter(DupList.list_upload_date < start_date).count()

                qry = DupList.query.filter(DupList.list_upload_date < start_date).order_by(DupList.id)\
                                   .offset(kwargs['start']).limit(kwargs['limit']).all()

                search = row_formatter(qry)
                search["total_count"] = total_count

                return Response(json.dumps(search), status=STATUS_CODES.get('OK'), mimetype=MIME_TYPES.get('JSON'))

            else:
                return custom_json_response(_("selected Filter is not applicable"),
                                            STATUS_CODES.get('BAD_REQUEST'), MIME_TYPES.get('JSON'))

        except Exception as e:
            app.logger.info(_("Error occurred while retrieving Duplication-List Details."))
            app.logger.exception(e)
            db.session.rollback()

        finally:
            db.session.close()


def row_formatter(qry):
    """Function to arrange json into Grid-rows for OEM details"""

    duplist_res = {"Duplist_Details": []}
    row = {}

    for q in qry:
        row["id"] = q.id
        row["imei"] = q.imei
        row["imsi"] = q.imsi
        row["msisdn"] = q.msisdn
        row["mno"] = q.mno
        row["uid"] = q.uid
        row["sms_notified"] = q.sms_notification
        row["imei_status"] = q.imei_status
        row["uploaded_date"] = str(q.list_upload_date)

        duplist_res["Duplist_Details"].append(dict(row))

    return duplist_res
