import json
import os

from pdcupdater.tests.handler_tests import (
    BaseHandlerTest, mock_pdc
)

here = os.path.dirname(__file__)

with open(here + '/data/composeinfo.json', 'r') as f:
    composeinfo = json.loads(f.read())

with open(here + '/data/images.json', 'r') as f:
    images = json.loads(f.read())

with open(here + '/data/rpms.json', 'r') as f:
    rpms = json.loads(f.read())


class TestNewCompose(BaseHandlerTest):
    handler_path = 'pdcupdater.handlers.compose:NewComposeHandler'
    config = {}

    def test_cannot_handle_fedbadges(self):
        idx = '2015-6c98c8e3-0dcb-497d-a0d8-0b3d026a4cfb'
        msg = self.get_fedmsg(idx)
        result = self.handler.can_handle(msg)
        self.assertEquals(result, False)

    def test_cannot_handle_new_compose_start(self):
        # Read the docs and code about the message producer for more info
        # https://pagure.io/pungi/blob/master/f/doc/configuration.rst#_566
        # https://pagure.io/pungi/blob/master/f/bin/pungi-fedmsg-notification
        msg = dict(
            topic='org.fedoraproject.prod.pungi.compose.start',
            msg=dict(
                # Probably some other info goes here too..
                # but this is all we know for now.
                compose_id='20151130.n.2',
            ),
        )
        result = self.handler.can_handle(msg)
        self.assertEquals(result, False)

    def test_can_handle_new_compose_finish(self):
        # Read the docs and code about the message producer for more info
        # https://pagure.io/pungi/blob/master/f/doc/configuration.rst#_566
        # https://pagure.io/pungi/blob/master/f/bin/pungi-fedmsg-notification
        msg = dict(
            topic='org.fedoraproject.prod.pungi.compose.finish',
            msg=dict(
                # Probably some other info goes here too..
                # but this is all we know for now.
                compose_id='20151130.n.2',
            ),
        )
        result = self.handler.can_handle(msg)
        self.assertEquals(result, True)

    @mock_pdc
    def test_handle_new_compose(self, pdc):
        # Read the docs and code about the message producer for more info
        # https://pagure.io/pungi/blob/master/f/doc/configuration.rst#_566
        # https://pagure.io/pungi/blob/master/f/bin/pungi-fedmsg-notification
        msg = dict(
            topic='org.fedoraproject.prod.pungi.compose.finish',
            msg=dict(
                # Probably some other info goes here too..
                # but this is all we know for now.
                compose_id='20151130.n.2',
            ),
        )
        self.handler.handle(pdc, msg)

        # Check compose images
        compose_images = pdc.calls['compose-images']
        self.assertEquals(len(compose_images), 1)
        self.assertDictEqual(compose_images[0][1], dict(
            release_id=u'rawhide',
            composeinfo=composeinfo,
            image_manifest=images,
        ))
        # Check compose rpms
        compose_rpms = pdc.calls['compose-rpms']
        self.assertEquals(len(compose_rpms), 1)
        self.assertEquals(compose_rpms[0][1], dict(
            release_id=u'rawhide',
            composeinfo=composeinfo,
            rpm_manifest=rpms,
        ))
