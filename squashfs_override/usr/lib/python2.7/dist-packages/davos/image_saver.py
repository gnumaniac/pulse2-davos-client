# -*- coding: utf-8; -*-
#
# (c) 2007-2015 Mandriva, http://www.mandriva.com/
#
# $Id$
#
# This file is part of Pulse 2, http://pulse2.mandriva.org
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2.  If not, see <http://www.gnu.org/licenses/>.

import os
import subprocess
import json
import time

class imageSaver(object):

    def __init__(self, manager):

        self.manager = manager
        self.logger = manager.logger
        self.imaging_api = manager.rpc.imaging_api

    
    def start(self):
        
        # Get image UUID
        self.image_uuid = self.imaging_api.computerCreateImageDirectory(self.manager.mac)

        # Set Fake Parclone mode
        self.logger.debug('Setting f.clone CLMODE env var to SAVE_IMAGE') 
        os.environ['CLMODE'] = 'SAVE_IMAGE'

        # Start the image saver
        error_code = subprocess.call('yes 2>/dev/null|/usr/sbin/ocs-sr -nogui -q2 -c -j2 -z1p -i 100 -sc -p true savedisk %s sda 1>/dev/null' % self.image_uuid, shell=True)

        if error_code != 0:
            self.logger.warning('An error was encountered while creating image, check the log for more details.')

        image_dir = os.path.join('/home/partimag/', self.image_uuid) + '/'

        # Save image JSON and LOG
        info = {}
        current_ts = time.strftime("%Y-%m-%d %H:%M:%S")
        info['title'] = 'Image of %s at %s' % (self.manager.hostname, current_ts)
        info['description'] = ''
        info['size'] = sum(os.path.getsize(image_dir+f) for f in os.listdir(image_dir) if os.path.isfile(image_dir+f))
        info['has_error'] = (error_code == 0)

        log_path = os.path.join(image_dir, 'davos.log')
        json_path = os.path.join(image_dir, 'davosInfo.json')

        open(log_path, 'w').write(open('/var/log/davos.log', 'r').read())
        open(json_path, 'w').write(json.dumps(info))

        # Send save img request
        self.imaging_api.imageDone(self.manager.mac, self.image_uuid)


