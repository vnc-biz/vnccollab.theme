from zope.publisher.browser import TestRequest

from vnccollab.theme.tests.base import FunctionalTestCase
from vnccollab.theme.testing import createObject
from vnccollab.theme.browser.wizarduploader import WizardUploadView, \
    WizardUploadInit


class TestLiveSearchReplyViewView(FunctionalTestCase):
    def test_wizarduploadview(self):
        view = WizardUploadView(self.portal, self.app.REQUEST)
        result = view.script_content()
        self.assertIn('addUploadFields_uploader', result)
        self.assertIn('wizardUpload_NextStep_uploader', result)
        self.assertIn('sendDataAndUpload_uploader', result)
        self.assertIn('clearQueue_uploader', result)
        self.assertIn('onUploadComplete_uploader', result)
        self.assertIn('createUploader_uploader', result)
        self.assertIn('jQuery(document).ready(createUploader_uploader', result)

    def test_wizarduploadinit(self):
        view = WizardUploadInit(self.portal, self.app.REQUEST)
        result = view()
        self.assertIn('addUploadFields_uploader', result)
        self.assertIn('wizardUpload_NextStep_uploader', result)
        self.assertIn('sendDataAndUpload_uploader', result)
        self.assertIn('clearQueue_uploader', result)
        self.assertIn('onUploadComplete_uploader', result)
        self.assertIn('createUploader_uploader', result)
        self.assertIn('jQuery(document).ready(createUploader_uploader);', result)

        settings = view.upload_settings()
        keys = ['ul_msg_failed', 'ul_error_maxsize_is', 'ul_error_empty_file',
                'typeupload', 'physical_path', 'ul_error_onlyallowed',
                'ul_fill_descriptions', 'ul_msg_all_sucess', 'ul_id',
                'ul_error_disallowed_type', 'ul_error_zodb_conflict',
                'ul_file_description', 'ul_error_file_large', 'ul_auto_upload',
                'ul_size_limit', 'ul_error_already_exists',
                'ul_file_extensions', 'ul_xhr_size_limit', 'ul_fill_titles',
                'context_url', 'ul_button_text', 'ul_error_bad_ext',
                'ul_msg_some_sucess', 'ul_error_server', 'portal_url',
                'ul_error_empty_extension', 'ul_msg_some_errors',
                'ul_error_no_permission', 'ul_draganddrop_text',
                'ul_file_extensions_list', 'ul_error_try_again_wo',
                'ul_sim_upload_limit', 'ul_error_try_again']
        for key in keys:
            self.assertIn(key, settings)

        self.assertEqual(settings['ul_file_extensions'], '*.*;')
        self.assertEqual(settings['ul_file_extensions_list'], '[]')
        self.assertEqual(settings['ul_file_description'], 'Choose files to upload')

        SESSION = {'typeupload': 'Image'}
        self.app.REQUEST['SESSION'] = SESSION
        view = WizardUploadInit(self.portal, self.app.REQUEST)
        view()
        settings = view.upload_settings()
        for key in keys:
            self.assertIn(key, settings)

        self.assertEqual(settings['ul_file_extensions'], '*.jpg;*.jpeg;*.gif;*.png;')
        self.assertEqual(settings['ul_file_extensions_list'], "['jpg', 'jpeg', 'gif', 'png']")
        self.assertEqual(settings['ul_file_description'], 'Choose images to upload')
