/**
 *
 * JQuery Helpers for Wizard Upload
 *
 */

var WizardUpload = {};

WizardUpload.addUploadFields = function(uploader, domelement, file, id, fillTitles, fillDescriptions) {
    var blocFile;
    jQuery('#upload-place').css('border', 'none');
    if (fillTitles || fillDescriptions)  {
        blocFile = uploader._getItemByFileId(id);
        if (typeof id == 'string') id = parseInt(id.replace('wizard_qq-upload-handler-iframe',''));
    }
    if (fillDescriptions)  {
        var labelfiledescription = jQuery('#uploadify_label_file_description').val();
        jQuery('.wizard_qq-upload-cancel', blocFile).before('\
                  <div class="uploadField">\
                      <label>' + labelfiledescription + '&nbsp;:&nbsp;</label> \
                      <textarea rows="2" \
                             class="file_description_field" \
                             id="description_' + id + '" \
                             name="description" \
                             value="" />\
                  </div>\
                   ')
    }
    if (fillTitles)  {
        var labelfiletitle = jQuery('#uploadify_label_file_title').val();
        jQuery('.wizard_qq-upload-cancel', blocFile).before('\
                  <div class="uploadField">\
                      <label>' + labelfiletitle + '&nbsp;:&nbsp;</label> \
                      <input type="text" \
                             class="file_title_field" \
                             id="title_' + id + '" \
                             name="title" \
                             value="" />\
                  </div>\
                   ')
    }
    WizardUpload.showButtons(uploader, domelement);
};

WizardUpload.showButtons = function(uploader, domelement) {
    var handler = uploader._handler;
    if (handler._files.length) {
        jQuery('.wizard_qq-uploadifybuttons').show();
        return 'ok';
    }
    return false;
};

WizardUpload.wizardUpload_NextStep = function(uploader, variable) {
    var handler = uploader._handler;
    var files = handler._files;
    var missing = 0;
    jQuery(".step2 .step-content").html('<input type="hidden" value="" id="wizard-uploader-marker" />');
    jQuery("#wizard-uploader-marker").attr('value', variable);
    jq('#tab_2').addClass('blocked').removeClass('active');

    animateContentWizardStep(3);

    var firstTree = false;
    if ( jq('#tree').find('.dynatree-container')[0] == undefined ) {
      firstTree = true;
    }

    jq("#tree").dynatree({
      initAjax: { url: portal_url+'/@@wizard_get_initial_tree.json',
                  cache: false
                },
      onLazyRead: function(node){
                    node.appendAjax({
                      'url': portal_url+'/@@wizard_get_tree.json',
                      'data': {'uid': node.data.key},
                    });
                },
      fx: { height: "toggle", duration: 200 },
      onRender: function(node, nodeSpan) {
        if( node.data.unselectable == true ){
          jq(nodeSpan).addClass("disabled")
          return false;
        }
      },
      onActivate: function(node, e){

        if( node.data.unselectable == true ){
          jq('.selectedContainer').html('');
          jq('input[name=selected_destination]').get(0).setAttribute('data', '');
          return false;
        }

        var newcontainter = '';
        var newactionform = '';
        var newcontenturl = '/portal_factory';

        newcontainter = node.data.path;
        newcontenturl += ''; //jq('form[name=edit_form]').attr('action').split('portal_factory')[1];
        newactionform = window.location.protocol + '//' + window.location.host + newcontainter + newcontenturl;

        jq('.selectedContainer').html(newcontainter);
        jq('input[name=selected_destination]').get(0).setAttribute('data', newcontainter);
        //jq('form[name=edit_form]').get(0).setAttribute('action', newactionform);
      },
      onPostInit: function (isReloading, isError) {
        if ( isError == true ) {
          jq('input#send-wizard').hide();
        } else {
          jq('input#send-wizard').show();
        }
        this.reactivate();
        return false;
      }
    });

    if( firstTree == false ) {
     jq("#tree").dynatree("getTree").reload();
    }
};

WizardUpload.sendDataAndUpload = function(uploader, action) { //, typeupload) {
    var handler = uploader._handler;
    var files = handler._files;
    var missing = 0;
    uploader._options.action = action + '/@@quick_upload_file'
    handler._options.action = action + '/@@quick_upload_file'

    for ( var id = 0; id < files.length; id++ ) {
        if (files[id]) {
            var fileContainer = jQuery('.wizard_qq-files-to-upload li')[id-missing];
            var file_title = '';
            if (fillTitles)  {
                file_title = jQuery('.file_title_field', fileContainer).val();
            }
            var file_description = '';
            if (fillDescriptions)  {
                file_description = jQuery('.file_description_field', fileContainer).val();
            }
            uploader._queueUpload(id, {'title': file_title, 'description': file_description, 'typeupload' : ''});
        }
        // if file is null for any reason jq block is no more here
        else missing++;
    }
};

WizardUpload.onAllUploadsComplete = function(){
    jQuery(document).trigger('wizard_qq-allfiles-uploaded');
    window.location.href = jQuery('input[name=selected_destination]').attr('data');
};

WizardUpload.clearQueue = function(uploader, domelement) {
    var handler = uploader._handler;
    var files = handler._files;
    for ( var id = 0; id < files.length; id++ ) {
        if (files[id]) {
            handler.cancel(id);
        }
        jQuery('.wizard_qq-files-to-upload li').remove();
        handler._files = [];
        if (typeof handler._inputs != 'undefined') handler._inputs = {};
    }
    jQuery('.wizard_qq-uploadifybuttons').hide();
};

WizardUpload.onUploadComplete = function(uploader, domelement, id, fileName, responseJSON) {
    var uploadList = jQuery('.wizard_qq-files-to-upload');
    if (responseJSON.success) {
        window.setTimeout( function() {
            jQuery(uploader._getItemByFileId(id)).remove();
            // after the last upload, if no errors, reload the page
            var newlist = jQuery('li', uploadList);
            jQuery(document).trigger('wizard_qq-file-uploaded', responseJSON);
            if (! newlist.length) window.setTimeout( WizardUpload.onAllUploadsComplete, 5);
        }, 50);
    }
};
