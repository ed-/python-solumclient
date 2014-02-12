# Copyright 2013 - Noorul Islam K M
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from solumclient.common import base as solum_base
from solumclient.openstack.common.apiclient import base as apiclient_base


class Component(apiclient_base.Resource):
    def __repr__(self):
        return "<Component %s>" % self._info


class ComponentManager(solum_base.CrudManager):
    resource_class = Component
    collection_key = 'components'

    def list(self, **kwargs):
        return super(ComponentManager, self).list(base_url="/v1", **kwargs)
