# -*- coding: utf-8 -*-
# Copyright 2014-2020 CERN
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Authors:
# - Joaquín Bogado <jbogado@linti.unlp.edu.ar>, 2014-2018
# - Cedric Serfon <cedric.serfon@cern.ch>, 2015
# - Martin Barisits <martin.barisits@cern.ch>, 2019
# - Benedikt Ziemons <benedikt.ziemons@cern.ch>, 2020

from __future__ import print_function

import unittest
from os import remove

from rucio.common.utils import generate_uuid as uuid, execute


def file_generator(size=2048, namelen=10):
    """ Create a bogus file and returns it's name.
    :param size: size in bytes
    :returns: The name of the generated file.
    """
    fn = '/tmp/rucio_testfile_' + uuid()
    execute('dd if=/dev/urandom of={0} count={1} bs=1'.format(fn, size))
    return fn


def delete_rules(did):
    # get the rules for the file
    print('Deleting rules')
    cmd = "rucio list-rules --did {0} | grep {0} | cut -f1 -d\ ".format(did)  # NOQA: W605
    print(cmd)
    exitcode, out, err = execute(cmd)
    print(out, err)
    rules = out.split()
    # delete the rules for the file
    for rule in rules:
        cmd = "rucio delete-rule {0}".format(rule)
        print(cmd)
        exitcode, out, err = execute(cmd)


class TestRucioClient(unittest.TestCase):
    running_with_unittest = False

    def setUp(self):
        self.marker = '$ > '
        self.scope = 'mock'
        self.rse = 'MOCK-POSIX'
        self.generated_dids = []

    def tearDown(self):
        for did in self.generated_dids:
            delete_rules(did)
            self.generated_dids.remove(did)

    def test_ping(self):
        """CLIENT (USER): rucio ping"""
        cmd = 'rucio ping'
        print(self.marker + cmd)
        exitcode, out, err = execute(cmd)
        print(out, err)
        if self.running_with_unittest:
            self.assertEqual(exitcode, 0)
        else:
            assert exitcode == 0

    def test_whoami(self):
        """CLIENT (USER): rucio whoami"""
        cmd = 'rucio whoami'
        print(self.marker + cmd)
        exitcode, out, err = execute(cmd)
        print(out, err)

        if self.running_with_unittest:
            self.assertEqual(exitcode, 0)
        else:
            assert exitcode == 0

    def test_upload_download(self):
        """CLIENT(USER): rucio upload files to dataset/download dataset"""
        tmp_file1 = file_generator()
        tmp_file2 = file_generator()
        tmp_file3 = file_generator()
        tmp_dsn = 'tests.rucio_client_test_server_' + uuid()

        # Adding files to a new dataset
        cmd = 'rucio upload --rse {0} --scope {1} {2} {3} {4} {1}:{5}'.format(self.rse, self.scope, tmp_file1, tmp_file2, tmp_file3, tmp_dsn)
        print(self.marker + cmd)
        exitcode, out, err = execute(cmd)
        print(out)
        print(err)
        remove(tmp_file1)
        remove(tmp_file2)
        remove(tmp_file3)

        if self.running_with_unittest:
            self.assertEqual(exitcode, 0)
        else:
            assert exitcode == 0

        # List the files
        cmd = 'rucio list-files {0}:{1}'.format(self.scope, tmp_dsn)
        print(self.marker + cmd)
        exitcode, out, err = execute(cmd)
        print(out)
        print(err)

        if self.running_with_unittest:
            self.assertEqual(exitcode, 0)
        else:
            assert exitcode == 0

        # List the replicas
        cmd = 'rucio list-file-replicas {0}:{1}'.format(self.scope, tmp_dsn)
        print(self.marker + cmd)
        exitcode, out, err = execute(cmd)
        print(out)
        print(err)

        if self.running_with_unittest:
            self.assertEqual(exitcode, 0)
        else:
            assert exitcode == 0

        # Downloading dataset
        cmd = 'rucio download --dir /tmp/ {0}:{1}'.format(self.scope, tmp_dsn)
        print(self.marker + cmd)
        exitcode, out, err = execute(cmd)
        print(out)
        print(err)
        # The files should be there
        cmd = 'ls /tmp/{0}/rucio_testfile_*'.format(tmp_dsn)
        print(self.marker + cmd)
        exitcode, out, err = execute(cmd)
        print(err, out)

        if self.running_with_unittest:
            self.assertEqual(exitcode, 0)
        else:
            assert exitcode == 0

        # cleaning
        remove('/tmp/{0}/'.format(tmp_dsn) + tmp_file1[5:])
        remove('/tmp/{0}/'.format(tmp_dsn) + tmp_file2[5:])
        remove('/tmp/{0}/'.format(tmp_dsn) + tmp_file3[5:])
        self.generated_dids + '{0}:{1} {0}:{2} {0}:{3} {0}:{4}'.format(self.scope, tmp_file1, tmp_file2, tmp_file3, tmp_dsn).split(' ')
