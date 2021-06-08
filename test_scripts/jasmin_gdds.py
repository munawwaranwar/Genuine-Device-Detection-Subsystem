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
import requests
from time import strftime
from flask import Flask, request


app = Flask(__name__)

ERROR_MSG = "Incorrect Technology-Name is provided"


# noinspection PyUnusedLocal,HttpUrlsUsage
@app.route('/gdds-jasmin', methods=['POST'])
def main():

    if request.method == 'POST':

        # Extracting parameters from API
        # kwargs = request.data.decode()
        kwargs = request.values
        #kwargs = request.get_json(force=True)

        # MSISDN Validation
        sender = msisdn_validation(kwargs['from'])

        # Fetching Mobile Operator's name
        operator = kwargs['origin-connector']

        # Fetching receiver's number or Shortcode
        receiver = kwargs['to']

        ussd_time = strftime("%Y-%m-%d %H:%M:%S")

        # striping white spaces from start and end
        sms_text = kwargs['content'].strip()

        ussd_keyword = sms_text.split(',')[0]

        if ussd_keyword in ['GDDS', 'gdds']:

            headers = {'content-type': 'application/json'}
            payload = {"sender_no": sender, "receiver": receiver, "time": ussd_time, "operator": operator,
                       "ussd_keyword": ussd_keyword, "msg_text": sms_text}

            response = requests.get(url="http://192.168.100.252/api/v2/gdds-ussd",
                                    params=payload,
                                    headers=headers)
            tmp = json.loads(response.content.decode('utf-8'))

            if isinstance(tmp, list):
                result = tmp[0]
            elif isinstance(tmp, dict):
                result = tmp["message"]
            else:
                result = tmp

            # Calling Jasmin SMS Rest API to send Release-Pair APIs' response back to sender via SMS
            # jasmin_sms(sender, receiver, result)

            # Calling DNS SMS-API to send DPS API's response back to sender
            dns_sms(sender, receiver, result, operator)
            return result

        else:
            dns_sms(sender, receiver, ERROR_MSG, operator)
            return ERROR_MSG, 422


def msisdn_validation(sender_no):
    """Function to modify Sender's MSISDN to DPS accepted format. """

    if sender_no[0:2] == '92':
        return sender_no
    elif sender_no[0:3] == '009':
        return sender_no[2:]
    elif sender_no[0:3] == '+92':
        return sender_no[1:]
    elif sender_no[0:2] == '03':
        return '92' + sender_no[1:]
    elif sender_no[0:3] == '%2B':
        return sender_no[3:]
    else:
        return sender_no


# noinspection HttpUrlsUsage
def jasmin_sms(sender, receiver, sms_content):
    """Function to call Jasmin Single-SMS Rest API."""

    url = "http://192.168.100.40:8080/secure/send"
    params = {"to": sender, "from": receiver, "coding": 0, "content": sms_content}
    headers = {'content-type': 'application/json', 'Authorization': "Basic em9uZzoxMjM="}
    response = requests.post(url=url, data=json.dumps(params), headers=headers)
    print(response.status_code, response.text)


# noinspection HttpUrlsUsage
def dns_sms(*args):
    """Function to call DNS SMS-API."""

    # url = "http://192.168.100.40:8080/secure/send"
    URL = "http://192.168.100.53/sms/"

    data = {}
    if len(args) == 3:
        data = {
            "sms_to": args[0],
            "sms_from": args[1],
            "sms_content": args[2],
            "subsystem": "GDDS",
        }
    elif len(args) == 4:
        data = {
            "sms_to": args[0],
            "sms_from": args[1],
            "sms_content": args[2],
            "operator": args[3],
            "subsystem": "GDDS",
        }

    headers = {'content-type': 'application/json'}
    response = requests.post(url=URL, data=json.dumps(data), headers=headers)
    print(response.status_code, response.text)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port='5001', debug=True)
