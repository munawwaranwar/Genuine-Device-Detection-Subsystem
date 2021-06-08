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


from gdds.app import app
from flask_restful import Api
from gdds.app.api.v1.resources.oem_bulk_upload import OemBulkUpload
from gdds.app.api.v1.resources.download_error_files import ErrorFiles
from gdds.app.api.v1.resources.keyclock_input import KeyClockInput
from gdds.app.api.v1.resources.brands_list import BrandsList
from gdds.app.api.v1.resources.get_oem_logins import GetOemLogins
from gdds.app.api.v1.resources.oem_brands_association import AssociateBrands
from gdds.app.api.v1.resources.asociated_brands import AssociatedBrands
from gdds.app.api.v1.resources.user_response_web import WebUserResponse
from gdds.app.api.v1.resources.oem_single_imei_response import OemSingleImei
from gdds.app.api.v1.resources.oem_home_page import OemHomePage
from gdds.app.api.v1.resources.oem_bulk_imeis_download import BulkImeiDownload
from gdds.app.api.v1.resources.dashboard_counts import DashboardCounts
from gdds.app.api.v1.resources.duplist_summary import DupListStats
from gdds.app.api.v1.resources.oem_logins_brands_summary import LoginBrandsSummary
from gdds.app.api.v1.resources.user_response_summary import UserResponseSummary
from gdds.app.api.v1.resources.oem_response_summary import OemResponseSummary
from gdds.app.api.v1.resources.duplist_details import DupListDetails
from gdds.app.api.v1.resources.oem_response_details import OemResponseDetails
from gdds.app.api.v1.resources.user_response_details import UserResponseDetails
from gdds.app.api.v2.resources.gdds_ussd import GddsUssd

api = Api(app, prefix='/api/v1')
api_v2 = Api(app, prefix='/api/v2')

api.add_resource(OemBulkUpload, '/oem-bulk-upload')
api.add_resource(ErrorFiles, '/download-error-file')
api.add_resource(KeyClockInput, '/keyclock-input')
api.add_resource(BrandsList, '/brands-list')
api.add_resource(GetOemLogins, '/get-oem-logins')
api.add_resource(AssociateBrands, '/associate-brands')
api.add_resource(AssociatedBrands, '/already-associated-brands')
api.add_resource(WebUserResponse, '/user-response-web')
api.add_resource(OemSingleImei, '/single-imei-response')
api.add_resource(OemHomePage, '/oem-home-page')
api.add_resource(BulkImeiDownload, '/bulk-imei-download')
api.add_resource(DashboardCounts, '/get-dashboard-counts')
api.add_resource(DupListStats, '/duplication-list-summary')
api.add_resource(LoginBrandsSummary, '/oem-logins-brands-summary')
api.add_resource(UserResponseSummary, '/user-response-summary')
api.add_resource(OemResponseSummary, '/oem-response-summary')
api.add_resource(DupListDetails, '/duplication-list-details')
api.add_resource(OemResponseDetails, '/oem-response-details')
api.add_resource(UserResponseDetails, '/user-response-details')

api_v2.add_resource(GddsUssd, '/gdds-ussd')
