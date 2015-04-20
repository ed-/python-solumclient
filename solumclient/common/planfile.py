# Copyright (c) 2015 Rackspace
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Tools for creating plan definitions.


import re

from solumclient.common import exc
from solumclient.common import yamlutils
from solumclient.openstack.common import cliutils


def lpname_is_valid(string):
    try:
        re.match(r'^([a-z0-9-_]{1,100})$', string).group(0)
    except (TypeError, AttributeError):
        return False
    return True


def name_is_valid(string):
    try:
        re.match(r'^([a-zA-Z0-9-_]{1,100})$', string).group(0)
    except AttributeError:
        return False
    return True


class PlanDefinition(object):

    def __init__(self, client, planfile, cmdline_args):
        self._client = client
        self._plan = planfile
        self._artifact = planfile['artifacts'][0]
        self._args = vars(cmdline_args)
        self._repo_token = None

    @property
    def artifact_name(self):
        error_message = ("Application name must be 1-100 characters and must "
                         "only contain a-z,A-Z,0-9,-,_")
        if self._args.get('name'):
            if name_is_valid(self._args['name']):
                return self._args['name']

    @property
    def artifact_type(self):
        return self._artifact.get('artifact_type', 'heroku')

    @property
    def description(self):
        return self._args.get('desc') or self._plan.get('description', '')

    @property
    def git_url(self):
        if self._args.get('git_url'):
            return self._args['git_url']
        if self._artifact['content'].get('href'):
            return self._artifact['content']['href']
        return raw_input("Please specify a git repository URL for "
                         "your application.\n> ")

    @property
    def is_private(self):
        if self._args.get('private'):
            return self._args['private']
        if self._artifact['content'].get('private'):
            return self._artifact['content']['private']
        return False

    @property
    def language_pack(self):
        if self._args.get('lp'):
            return self._args['lp']
        languagepack = self._artifact.get('language_pack')
        if languagepack == 'auto':
            return languagepack
        try:
            lps = self._client.languagepacks.find(name_or_id=languagepack)
        except Exception as e:
            if type(e).__name__ == 'NotFound':
                raise exc.CommandError("Languagepack %s not registered" %
                                       languagepack)
        filtered_list = [lp for lp in lps if lp.status == 'READY']
        if len(filtered_list) <= 0:
            raise exc.CommandError("Languagepack %s not READY" % languagepack)

        lpnames = [lp.name for lp in lps]
        lp_uuids = [lp.uuid for lp in lps]
        fields = ['uuid', 'name', 'description', 'status', 'source_uri']
        cliutils.print_list(languagepacks, fields)

        languagepack = raw_input("Please choose a languagepack from "
                                 "the above list.\n> ")
        while languagepack not in lpnames + lp_uuids:
            languagepack = raw_input("You must choose one of the named "
                                     "language packs.\n> ")
        return languagepack

    @property
    def name(self):
        error_message = ("Application name must be 1-100 characters and "
                         "must only contain a-z,A-Z,0-9,-,_")
        if self._args.get('name'):
            if not name_is_valid(self._args['name']):
                raise exc.CommandError(message=error_message)
            return self._args['name']
        if self._plan.get('name'):
            if not name_is_valid(self._plan.get('name')):
                raise exc.CommandError(message=error_message)
            return self._plan.get('name')
        return ''

    @property
    def parameters(self):
        if self._args.get('param_file'):
            param_file = self._args['param_file']
            try:
                with open(param_file) as param_f:
                    param_def = param_f.read()
                    return yamlutils.load(param_def)
            except IOError:
                message = "Could not open param file %s." % param_file
                raise exc.CommandError(message=message)
            except ValueError:
                message = ("Param file %s was not YAML." % param_file)
                raise exc.CommandError(message=message)

    @property
    def ports(self):
        if self._args.get('port'):
            return [int(self._args['port'])]
        if self._artifact.get('ports'):
            return self._artifact['ports']
        print("No application port specified in plan file.")
        print("Defaulting to port 80.")
        return [80]

    @property
    def public_key(self):
        if self._artifact['content'].get('public_key'):
            return self._artifact['content']

    @property
    def repo_token(self):
        if self._repo_token:
            return self._repo_token
        if self._args.get('access_token'):
            return self._args['access_token']
        if self._artifact.get('repo_token'):
            return self._artifact['repo_token']

    @property
    def run_cmd(self):
        if self._args.get('run_cmd'):
            return self._args['run_cmd']
        if self._artifact.get('run_cmd'):
            return self._artifact['run_cmd']
        return raw_input("Please specify start/run command for your "
                         "application.\n> ")

    @property
    def unittest_cmd(self):
        if self._artifact.get('unittest_cmd'):
            return self._artifact['unittest_cmd']

    def dump(self):
        return {
            'version': 1,
            'name': self.name,
            'description': self.description,
            'parameters': self.parameters,
            'artifacts': [
                {
                    'artifact_type': self.artifact_type,
                    'language_pack': self.language_pack,
                    'name': self.artifact_name,
                    'repo_token': self.repo_token,
                    'content': {
                        'href': self.git_url,
                        'run_cmd': self.run_cmd,
                        'unittest_cmd': self.unittest_cmd,
                        'ports': self.ports,
                        'public_key': self.public_key,
                        'private': self.is_private,
                        },
                },
            ]
        }
