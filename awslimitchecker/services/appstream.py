"""
awslimitchecker/services/appstream.py

The latest version of this package is available at:
<https://github.com/jantman/awslimitchecker>

################################################################################
Copyright 2015-2017 Jason Antman <jason@jasonantman.com>

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
bugs please submit them at <https://github.com/jantman/pydnstest> or
to me via email, and that you send any contributions or improvements
either as a pull request on GitHub, or to me via email.
################################################################################

AUTHORS:
Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>
################################################################################
"""

import abc  # noqa
import logging
import boto3

from .base import _AwsService
from ..limit import AwsLimit

logger = logging.getLogger(__name__)


class _AppstreamService(_AwsService):

    service_name = 'Appstream'
    api_name = 'appstream'  # AWS API name to connect to (boto3.client)

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
        self._find_usage_stacks()
        self._find_usage_fleets()
        #TODO:
        #self._find_usage_streaming_instances()
        self._find_usage_images()
        self._find_usage_image_builders()
        self._find_usage_users()
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
        
        limits['Stacks'] = AwsLimit(
            'Stacks',
            self,
            5,
            self.warning_threshold,
            self.critical_threshold,
            limit_type='AWS::AppStream',
        )

        limits['Fleets'] = AwsLimit(
            'Fleets',
            self,
            5,
            self.warning_threshold,
            self.critical_threshold,
            limit_type='AWS::AppStream',
        )
        # TODO
        # limits['Streaming instances'] = AwsLimit(
        #     'Streaming instances',
        #     self,
        #     5,
        #     self.warning_threshold,
        #     self.critical_threshold,
        #     limit_type='AWS::AppStream',
        # )

        limits['Images'] = AwsLimit(
            'Images',
            self,
            5,
            self.warning_threshold,
            self.critical_threshold,
            limit_type='AWS::AppStream',
        )

        limits['Image builders'] = AwsLimit(
            'Image builders',
            self,
            5,
            self.warning_threshold,
            self.critical_threshold,
            limit_type='AWS::AppStream',
        )
        limits['Users'] = AwsLimit(
            'Users',
            self,
            5,
            self.warning_threshold,
            self.critical_threshold,
            limit_type='AWS::AppStream',
        )

        self.limits = limits
        return limits

    def _find_usage_stacks(self):
        resp = self.conn.describe_stacks()
        count = len(resp['Stacks'])
        if 'NextToken' in resp:
            next_token = resp['NextToken']
            while(next_token is not None):
                resp = self.conn.describe_stacks(NextToken=next_token)
                count = count + len(resp["Stacks"])
                if 'NextToken' in resp:
                    next_token = resp['NextToken']
                else:
                    next_token = None
        self.limits['Stacks']._add_current_usage(
            count, aws_type='AWS::AppStream'
        )

    def _find_usage_fleets(self):
        resp = self.conn.describe_fleets()
        count = len(resp['Fleets'])
        if 'NextToken' in resp:
            next_token = resp['NextToken']
            while(next_token is not None):
                resp = self.conn.describe_fleets(NextToken=next_token)
                count = count + len(resp["Fleets"])
                if 'NextToken' in resp:
                    next_token = resp['NextToken']
                else:
                    next_token = None
        self.limits['Fleets']._add_current_usage(
            count, aws_type='AWS::AppStream'
        )

    def _find_usage_images(self):
        resp = self.conn.describe_images()
        count = len(resp['Images'])
        if 'NextToken' in resp:
            next_token = resp['NextToken']
            while(next_token is not None):
                resp = self.conn.describe_images(NextToken=next_token)
                count = count + len(resp["Images"])
                if 'NextToken' in resp:
                    next_token = resp['NextToken']
                else:
                    next_token = None
        self.limits['Images']._add_current_usage(
            count, aws_type='AWS::AppStream'
        )
    
    def _find_usage_image_builders(self):
        resp = self.conn.describe_image_builders()
        count = len(resp['ImageBuilders'])
        if 'NextToken' in resp:
            next_token = resp['NextToken']
            while(next_token is not None):
                resp = self.conn.describe_image_builders(NextToken=next_token)
                count = count + len(resp["ImageBuilders"])
                if 'NextToken' in resp:
                    next_token = resp['NextToken']
                else:
                    next_token = None
        self.limits['Image builders']._add_current_usage(
            count, aws_type='AWS::AppStream'
        )

    def _find_usage_users(self):
        """
        Number of users are the same as registered directory in workspace
        """
        # Temporarily use workspaces api client
        self.api_name = 'workspaces'
        self.conn = None
        self.connect()
        paginator = self.conn.get_paginator('describe_workspace_directories')
        count = 0
        iter = paginator.paginate()
        for page in iter:
            for directory in page['Directories']:
                if directory['State'] == 'REGISTERED':
                    count += 1
        self.limits['Users']._add_current_usage(
            count, aws_type='AWS::AppStream'
        )
        # Reset api client to appstream
        self.api_name = 'appstream' 
        self.conn = None
        self.connect()       

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
            "Appstream:describe*",
            "Workspaces:describe*"
        ]
