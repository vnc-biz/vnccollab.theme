from Acquisition import aq_inner

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.quickupload.browser.quick_upload import QuickUploadView, \
    QuickUploadInit


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
