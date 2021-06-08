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

import yaml
import sys
from flask_cors import CORS
from flask_babel import Babel
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from elasticsearch import Elasticsearch
from gdds.app.api.common.lazy_text_encoder import JSON_Encoder


app = Flask(__name__)
CORS(app)
app.j_encoder = JSON_Encoder()
babel = Babel(app)

try:
    with open('config.yml', 'r') as yaml_file:
        global_config = yaml.safe_load(yaml_file)
except Exception as e:  # pragma: no cover
    app.logger.error('Exception encountered during loading the config file')
    app.logger.exception(e)
    sys.exit(1)

conf = global_config['global']

es_ip = conf['es_ip']
es = Elasticsearch(es_ip)

app.config['SQLALCHEMY_DATABASE_URI'] = '''postgresql://{}:{}@{}/{}'''.format(conf['db_username'], conf['db_password'],
                                                                              conf['db_host'], conf['db_name'])

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_POOL_SIZE'] = int(conf['pool_size'])
app.config['SQLALCHEMY_POOL_RECYCLE'] = int(conf['pool_recycle'])
app.config['SQLALCHEMY_MAX_OVERFLOW'] = int(conf['overflow_size'])
app.config['SQLALCHEMY_POOL_TIMEOUT'] = int(conf['pool_timeout'])
app.config['BABEL_DEFAULT_LOCALE'] = conf['supported_languages']['default_language']
app.config['SUPPORTED_LANGUAGES'] = conf['supported_languages']

db = SQLAlchemy()
db.init_app(app)

from gdds.app.api.common.db_connection import connect
pg_connect = connect()

from gdds.app.api.routes import *


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(app.config['SUPPORTED_LANGUAGES'])


@app.after_request
def add_no_cache(response):
    """Making sure no API responses are cached by setting headers on the response."""
    response.cache_control.no_cache = True
    response.cache_control.no_store = True
    response.cache_control.must_revalidate = True
    response.cache_control.max_age = 0
    response.headers['Pragma'] = 'no-cache'
    response.expires = 0

    return response


@app.after_request
def add_security_headers(response):
    """Makes sure appropriate security headers are added for each API."""
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'

    return response
