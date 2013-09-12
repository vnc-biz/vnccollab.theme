from Acquisition import aq_inner

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.ATContentTypes.interfaces import IImageContent

from collective.quickupload import siteMessageFactory as _
from collective.quickupload.browser.quick_upload import QuickUploadView, \
    QuickUploadInit, _listTypesForInterface


class WizardUploadView(QuickUploadView):
    """ The Wizard Upload View
    """

    template = ViewPageTemplateFile("templates/wizard_upload.pt")

    def script_content(self) :
        context = aq_inner(self.context)
        return context.unrestrictedTraverse('@@wizard_upload_init')(for_id = self.uploader_id)



XHR_UPLOAD_JS = """
    var fillTitles = %(ul_fill_titles)s;
    var fillDescriptions = %(ul_fill_descriptions)s;
    var auto = %(ul_auto_upload)s;
    addUploadFields_%(ul_id)s = function(file, id) {
        var uploader = xhr_%(ul_id)s;
        WizardUpload.addUploadFields(uploader, uploader._element, file, id, fillTitles, fillDescriptions);
    }
    wizardUpload_NextStep_%(ul_id)s = function() {
        var uploader = xhr_%(ul_id)s;
        WizardUpload.wizardUpload_NextStep(uploader, 'xhr_%(ul_id)s');
    }
    sendDataAndUpload_%(ul_id)s = function(action) {
        var uploader = xhr_%(ul_id)s;
        WizardUpload.sendDataAndUpload(uploader, action); //, '%(typeupload)s');
    }
    clearQueue_%(ul_id)s = function() {
        var uploader = xhr_%(ul_id)s;
        WizardUpload.clearQueue(uploader, uploader._element);
    }
    onUploadComplete_%(ul_id)s = function(id, fileName, responseJSON) {
        var uploader = xhr_%(ul_id)s;
        WizardUpload.onUploadComplete(uploader, uploader._element, id, fileName, responseJSON);
    }
    createUploader_%(ul_id)s= function(){
        xhr_%(ul_id)s = new wizard_qq.WizardFileUploader({
            element: jQuery('#%(ul_id)s')[0],
            action: '%(context_url)s/@@quick_upload_file',
            autoUpload: auto,
            onAfterSelect: addUploadFields_%(ul_id)s,
            onComplete: onUploadComplete_%(ul_id)s,
            allowedExtensions: %(ul_file_extensions_list)s,
            sizeLimit: %(ul_xhr_size_limit)s,
            simUploadLimit: %(ul_sim_upload_limit)s,
            template: '<div class="wizard_qq-uploader">' +
                      '<div class="wizard_qq-upload-button"></div>' +
                      '<ul class="wizard_qq-upload-list"></ul>' +
                      '</div>',
            fileTemplate: '<li>' +
                    '<a class="wizard_qq-upload-cancel" href="#">&nbsp;</a>' +
                    '<div class="wizard_qq-upload-infos"><span class="wizard_qq-upload-file"></span>' +
                    '<span class="wizard_qq-upload-spinner"></span>' +
                    '<span class="wizard_qq-upload-failed-text">%(ul_msg_failed)s</span></div>' +
                    '<div class="wizard_qq-upload-size"></div>' +
                '</li>',
            messages: {
                serverError: "%(ul_error_server)s",
                serverErrorAlreadyExists: "%(ul_error_already_exists)s {file}",
                serverErrorZODBConflict: "%(ul_error_zodb_conflict)s {file}, %(ul_error_try_again)s",
                serverErrorNoPermission: "%(ul_error_no_permission)s",
                serverErrorDisallowedType: "%(ul_error_disallowed_type)s",
                typeError: "%(ul_error_bad_ext)s {file}. %(ul_error_onlyallowed)s {extensions}.",
                sizeError: "%(ul_error_file_large)s {file}, %(ul_error_maxsize_is)s {sizeLimit}.",
                emptyError: "%(ul_error_empty_file)s {file}, %(ul_error_try_again_wo)s",
                missingExtension: "%(ul_error_empty_extension)s {file}"
            }
        });
    }
    jQuery(document).ready(createUploader_%(ul_id)s);
"""


class WizardUploadInit(QuickUploadInit):
    """ Initialize uploadify js
    """

    def __call__(self, for_id="uploader"):
        self.uploader_id = for_id
        settings = self.upload_settings()

        if self.qup_prefs.use_flashupload or self.use_flash_as_fallback():
            return FLASH_UPLOAD_JS % settings
        return XHR_UPLOAD_JS % settings

    def upload_settings(self):
        context = aq_inner(self.context)
        request = self.request
        try:
            session = request.get('SESSION', {})
            mediaupload = session.get('mediaupload',
                    request.get('mediaupload', ''))
            typeupload = session.get('typeupload',
                    request.get('typeupload', ''))
        except SessionDataManagerErr:
            logger.debug('Error occurred getting session data. Falling back to '
                    'request.')
            mediaupload = request.get('mediaupload', '')
            typeupload = request.get('typeupload', '')
        portal_url = getToolByName(context, 'portal_url')()

        settings = dict(
            portal_url             = portal_url,
            typeupload             = '',
            context_url            = context.absolute_url(),
            physical_path          = "/".join(context.getPhysicalPath()),
            ul_id                  = self.uploader_id,
            ul_fill_titles         = self.qup_prefs.fill_titles and 'true' or 'false',
            ul_fill_descriptions   = self.qup_prefs.fill_descriptions and 'true' or 'false',
            ul_auto_upload         = self.qup_prefs.auto_upload and 'true' or 'false',
            ul_size_limit          = self.qup_prefs.size_limit and str(self.qup_prefs.size_limit*1024) or '',
            ul_xhr_size_limit      = self.qup_prefs.size_limit and str(self.qup_prefs.size_limit*1024) or '0',
            ul_sim_upload_limit    = str(self.qup_prefs.sim_upload_limit),
            ul_button_text         = self._translate(_(u'Browse')),
            ul_draganddrop_text    = self._translate(_(u'Drag and drop files to upload')),
            ul_msg_all_sucess      = self._translate(_(u'All files uploaded with success.')),
            ul_msg_some_sucess     = self._translate(_(u' files uploaded with success, ')),
            ul_msg_some_errors     = self._translate(_(u" uploads return an error.")),
            ul_msg_failed          = self._translate(_(u"Failed")),
            ul_error_try_again_wo  = self._translate(_(u"please select files again without it.")),
            ul_error_try_again     = self._translate(_(u"please try again.")),
            ul_error_empty_file    = self._translate(_(u"Selected elements contain an empty file or a folder:")),
            ul_error_empty_extension = self._translate(_(u"This file has no extension:")),
            ul_error_file_large    = self._translate(_(u"This file is too large:")),
            ul_error_maxsize_is    = self._translate(_(u"maximum file size is:")),
            ul_error_bad_ext       = self._translate(_(u"This file has invalid extension:")),
            ul_error_onlyallowed   = self._translate(_(u"Only allowed:")),
            ul_error_no_permission = self._translate(_(u"You don't have permission to add this content in this place.")),
            ul_error_disallowed_type = self._translate(_(u"This type of element is not allowed in this folder.",)),
            ul_error_already_exists = self._translate(_(u"This file already exists with the same name on server:")),
            ul_error_zodb_conflict = self._translate(_(u"A data base conflict error happened when uploading this file:")),
            ul_error_server        = self._translate(_(u"Server error, please contact support and/or try again.")),
        )

        settings['typeupload'] = typeupload
        if typeupload :
            imageTypes = _listTypesForInterface(context, IImageContent)
            if typeupload in imageTypes :
                ul_content_types_infos = self.ul_content_types_infos('image')
            else :
                ul_content_types_infos = self.ul_content_types_infos(mediaupload)
        else :
            ul_content_types_infos = self.ul_content_types_infos(mediaupload)

        settings['ul_file_extensions'] = ul_content_types_infos[0]
        settings['ul_file_extensions_list'] = str(ul_content_types_infos[1])
        settings['ul_file_description'] = ul_content_types_infos[2]

        return settings
