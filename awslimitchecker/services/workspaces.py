"""
awslimitchecker/services/ecs.py

The latest version of this package is available at:
<https://github.com/di1214/awslimitchecker>

################################################################################
Copyright 2015-2017 Di Zou <zou@pythian.com>

    This file is part of awslimitchecker, also known as awslimitchecker.

    awslimitchecker is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    awslimitchecker is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with awslimitchecker.  If not, see <http://www.gnu.org/licenses/>.

The Copyright and Authors attributions contained herein may not be removed or
otherwise altered, except to add the Author attribution of a contributor to
this work. (Additional Terms pursuant to Section 7b of the AGPL v3)
################################################################################
While not legally required, I sincerely request that anyone who finds
bugs please submit them at <https://github.com/di1214/pydnstest> or
to me via email, and that you send any contributions or improvements
either as a pull request on GitHub, or to me via email.
################################################################################

AUTHORS:
Di Zou <zou@pythian.com>
################################################################################
"""

import abc  # noqa
import logging

from .base import _AwsService
from ..limit import AwsLimit

logger = logging.getLogger(__name__)


class _WorkspacesService(_AwsService):

    service_name = 'Workspaces'
    api_name = 'workspaces'  # AWS API name to connect to (boto3.client)

    def find_usage(self):
        """
        Determine the current usage for each limit of this service,
        and update corresponding Limit via
        :py:meth:`~.AwsLimit._add_current_usage`.
        """
        logger.debug("Checking usage for service %s", self.service_name)
        self.connect()
        for lim in self.limits.values():
            lim._reset_usage()

        bundles_map={}
        paginator = self.conn.get_paginator('describe_workspace_bundles')
        iter = paginator.paginate()
        for page in iter:
            for bundle in page['Bundles']:
                bundles_map[bundle['BundleId']]=bundle['ComputeType']['Name']

        count_value=0
        count_standard=0
        count_performance=0
        paginator = self.conn.get_paginator('describe_workspaces')
        iter = paginator.paginate()
        for page in iter:
            for workspace in page['Workspaces']:
                if workspace['BundleId'] in bundles_map:
                    if bundles_map[workspace['BundleId']] == 'VALUE':
                        count_performance += 1
                    elif bundles_map[workspace['BundleId']] == 'STANDARD':
                        count_standard += 1
                    elif bundles_map[workspace['BundleId']] == 'PERFORMANCE':
                        count_performance += 1
        self.limits['VALUE']._add_current_usage(
            count_value,
            aws_type='AWS::Workspaces'
        )
        self.limits['STANDARD']._add_current_usage(
            count_standard,
            aws_type='AWS::Workspaces'
        )
        self.limits['PERFORMANCE']._add_current_usage(
            count_performance,
            aws_type='AWS::Workspaces'
        ) 

                
        self._have_usage = True
        logger.debug("Done checking usage.")

    def get_limits(self):
        """
        Return all known limits for this service, as a dict of their names
        to :py:class:`~.AwsLimit` objects.

        :returns: dict of limit names to :py:class:`~.AwsLimit` objects
        :rtype: dict
        """
        if self.limits != {}:
            return self.limits
        limits = {}
        limits['VALUE'] = AwsLimit(
            'VALUE',
            self,
            1,
            self.warning_threshold,
            self.critical_threshold,
            limit_type='AWS::Workspaces',
        )
        limits['STANDARD'] = AwsLimit(
            'STANDARD',
            self,
            1,
            self.warning_threshold,
            self.critical_threshold,
            limit_type='AWS::Workspaces',
        )
        limits['PERFORMANCE'] = AwsLimit(
            'PERFORMANCE',
            self,
            1,
            self.warning_threshold,
            self.critical_threshold,
            limit_type='AWS::Workspaces',
        )
        self.limits = limits
        return limits

    def required_iam_permissions(self):
        """
        Return a list of IAM Actions required for this Service to function
        properly. All Actions will be shown with an Effect of "Allow"
        and a Resource of "*".

        :returns: list of IAM Action strings
        :rtype: list
        """
        # TODO: update this to be all IAM permissions required for find_usage() to work
        return [
            "Workspaces:describe*",
        ]
