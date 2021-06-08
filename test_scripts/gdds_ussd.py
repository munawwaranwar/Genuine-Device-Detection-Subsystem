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
import sys
import json
import requests
from urllib.parse import unquote


def main(argv):

    msisdn = "+923040519543"
    # msisdn = argv[0]
    receiver = 8483
    # receiver = argv[1]
    time = 123
    # time = argv[2]
    smsc_id = "huawei"
    # smsc_id = argv[3]
    # msg_data = "USSD,11,923201746577"
    msg_data = "GDDS,822e05645731660006,Serial-1234,11111111111111|22222222222222,Magenta,Infinx,Note-8"

    ussd_keyword = msg_data.split(',')[0]
    sender_no = validations(msisdn)

    headers = {'content-type': 'application/json'}
    payload = {"sender_no": sender_no, "receiver": receiver, "time": time, "operator": smsc_id,
               "ussd_keyword": ussd_keyword, "msg_text": msg_data}

    response = requests.get(url="http://127.0.0.1:5000/api/v2/gdds-ussd", params=payload, headers=headers)
    result = json.loads(response.content.decode('utf-8'))

    if isinstance(result, list):
        print(result)
    elif isinstance(result, dict):
        print(result["message"])
    else:
        print(result)

    return


def validations(sender_no):
    if sender_no[0:3] == '%2B':
        sender_no = sender_no[3:]
    elif sender_no[0:3] == '009':
        sender_no = sender_no[2:]
    elif sender_no[0:3] == '+92':
        sender_no = sender_no[1:]
    elif sender_no[0:2] == '03':
        sender_no = '92' + sender_no[1:]

    return sender_no


if __name__ == "__main__":
    main(sys.argv[1:])
