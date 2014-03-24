/**
 * Wizard uploader based on:
 *
 * http://github.com/valums/file-uploader
 *
 * Multiple file upload component with progress-bar, drag-and-drop.
 * © 2010 Andrew Valums andrew(at)valums.com
 *
 * Licensed under GNU GPL 2 or later, see license.txt.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program. If not, see <http://www.gnu.org/licenses/>.
 */

var wizard_qq = wizard_qq || {};

/**
 * Class that creates our multiple file upload widget
 */
wizard_qq.WizardFileUploader = function(o){
    this._options = {
        // container element DOM node (ex. $(selector)[0] for jQuery users)
        element: null,
        // url of the server-side upload script, should be on the same domain
        action: '/server/upload',
        // additional data to send, name-value pairs
        params: {},
        // ex. ['jpg', 'jpeg', 'png', 'gif'] or []
        allowedExtensions: [],
        // size limit in bytes, 0 - no limit
        // this option isn't supported in all browsers
        sizeLimit: 0,
        // method executed after selection and before upload
        onAfterSelect: function(id, fileName){},
        // if autoUpload is set to false nothing is done
        // after selection excepted onAfterSelect method
        autoUpload: true,
        // simultnaeous uploads limit (2 by default)
        simUploadLimit: 2,
        onSubmit: function(id, fileName){},
        onComplete: function(id, fileName, responseJSON){},
        //
        // UI customizations
        template: '<div class="wizard_qq-uploader">' +
                '<div class="wizard_qq-upload-drop-area"><span>Drop files here to upload</span></div>' +
                '<div class="wizard_qq-upload-button">Browse for a file</div>' +
                '<ul class="wizard_qq-upload-list"></ul>' +
             '</div>',

        // template for one item in file list
        fileTemplate: '<li>' +
                '<a class="wizard_qq-upload-cancel" href="#">&nbsp;</a>' +
                '<div class="wizard_qq-upload-infos"><span class="wizard_qq-upload-file"></span>' +
                '<span class="wizard_qq-upload-spinner"></span>' +
                '<span class="wizard_qq-upload-failed-text">Failed</span></div>' +
                '<div class="wizard_qq-upload-size"></div>' +
            '</li>',

        classes: {
            // used to get elements from templates
            button: 'wizard_qq-upload-button',
            drop: 'wizard_qq-upload-drop-area',
            dropActive: 'wizard_qq-upload-drop-area-active',
            list: 'wizard_qq-files-to-upload',
            listContainer: 'wizard_qq-files-to-upload-container',
            uploader: 'uploaderContainer',
            uploadForm: 'upload-form',
            hideForm: 'hide-form',

            file: 'wizard_qq-upload-file',
            spinner: 'wizard_qq-upload-spinner',
            size: 'wizard_qq-upload-size',
            cancel: 'wizard_qq-upload-cancel',

            // added to list item when upload completes
            // used in css to hide progress spinner
            success: 'wizard_qq-upload-success',
            fail: 'wizard_qq-upload-fail'
        },
        messages: {
            //serverError: "Some files were not uploaded, please contact support and/or try again.",
            typeError: "{file} has invalid extension. Only {extensions} are allowed.",
            sizeError: "{file} is too large, maximum file size is {sizeLimit}.",
            emptyError: "{file} is empty, please select files again without it."
        },
        showMessage: function(message){
            alert(message);
        },
        debugMode: false
    };

    wizard_qq.extend(this._options, o);

    this._element = this._options.element;

    if (this._element.nodeType != 1){
        throw new Error('element param of WizardFileUploader should be dom node');
    }

    base_template  =  this._options.template;
    debug_template = '<div class="wizard_qq-upload-debug">' +
                     '  <strong>Current Uploads : </strong><span class="wizard_qq-upload-debug-curruploads"></span>' +
                     '</div>';
    if (this._options.debugMode) base_template = base_template + debug_template;
    this._element.innerHTML = base_template;


    // number of files being uploaded
    this._filesInProgress = 0;

    // easier access
    this._classes = this._options.classes;

    this._handler = this._createUploadHandler();

    this._debugConsole = this.getDebugConsole();

    this._bindCancelEvent();

    var self = this;
    this._button = new wizard_qq.WizardUploadButton({
        element: this._getElement('button'),
        multiple: wizard_qq.WizardUploadHandlerXhr.isSupported(),
        onChange: function(input){
            self._onInputChange(input);
        }
    });

    this._setupDragDrop();
};

wizard_qq.WizardFileUploader.prototype = {
    setParams: function(params){
        this._options.params = params;
    },
    getDebugConsole: function(){
        return wizard_qq.getByClass(this._element, 'wizard_qq-upload-debug')[0];
    },
    logDebug: function(type, logcontent) {
       blocdebug = wizard_qq.getByClass(this._debugConsole, 'wizard_qq-upload-debug-'+type);
       if (blocdebug) wizard_qq.setText(blocdebug[0], logcontent);
    },
    /**
     * Returns true if some files are being uploaded, false otherwise
     */
    isUploading: function(){
        return !!this._filesInProgress;
    },
    /**
     * Gets one of the elements listed in this._options.classes
     *
     * First optional element is root for search,
     * this._element is default value.
     *
     * Usage
     *  1. this._getElement('button');
     *  2. this._getElement(item, 'file');
     **/
    _getElement: function(parent, type){
        if (typeof parent == 'string'){
            // parent was not passed
            type = parent;
            parent = this._element;
        }

        var element = wizard_qq.getByClass(parent, this._options.classes[type])[0];

        if (!element){
            //element = $('.' + this._options.classes[type], parent);
            element = wizard_qq.getByClass(document, this._options.classes[type])[0];
        }
        if (!element){
            throw new Error('element not found ' + type);
        }

        return element;
    },
    _error: function(code, fileName, id){
        var message = this._options.messages[code];
        message = message.replace('{file}', this._formatFileName(fileName));
        message = message.replace('{extensions}', this._options.allowedExtensions.join(', '));
        message = message.replace('{sizeLimit}', this._formatSize(this._options.sizeLimit));
        // global alert message on client error selection
        if (typeof id=='undefined') this._options.showMessage(message);
        else {
            var item = this._getItemByFileId(id);
            var diverror = document.createElement("div");
            item.appendChild(diverror);
            eclass = document.createAttribute("class");
            eclass.nodeValue = "server-error";
            diverror.setAttributeNode(eclass);
            diverror.innerText = message;
            diverror.textContent = message;
        }
    },
    _formatFileName: function(name){
        if (name.length > 33){
            name = name.slice(0, 19) + '...' + name.slice(-13);
        }
        return name;
    },
    _isAllowedExtension: function(fileName){
        var ext = (-1 !== fileName.indexOf('.')) ? fileName.replace(/.*[.]/, '').toLowerCase() : '';
        var allowed = this._options.allowedExtensions;

        if (!allowed.length){return true;}

        for (var i=0; i<allowed.length; i++){
            if (allowed[i].toLowerCase() == ext){
                return true;
            }
        }

        return false;
    },
    _setupDragDrop: function(){
        function isValidDrag(e){
            var dt = e.dataTransfer,
                // do not check dt.types.contains in webkit, because it crashes safari 4
                isWebkit = navigator.userAgent.indexOf("AppleWebKit") > -1;

            // dt.effectAllowed is none in Safari 5
            // dt.types.contains check is for firefox
            return dt && dt.effectAllowed != 'none' &&
                (dt.files || (!isWebkit && dt.types.contains && dt.types.contains('Files')));
        }

        var self = this,
            dropArea = this._getElement('drop'),
            uploaderContainer = this._getElement('uploader'),
            uploadForm = this._getElement(document, 'uploadForm'),
            fileList = this._getElement(document, 'listContainer');

        dropArea.style.display = 'none';

        var hideTimeout;
        wizard_qq.attach(document, 'dragenter', function(e){
            e.preventDefault();
        });

        wizard_qq.attach(uploaderContainer, 'dragover', function(e){
            if (isValidDrag(e)){

                if (hideTimeout){
                    clearTimeout(hideTimeout);
                }

                dropArea.style.display = 'block';
                fileList.style.display = 'none';

                if (dropArea == e.target || wizard_qq.contains(dropArea,e.target)){
                    var effect = e.dataTransfer.effectAllowed;
                    if (effect == 'move' || effect == 'linkMove'){
                        e.dataTransfer.dropEffect = 'move'; // for FF (only move allowed)
                    } else {
                        e.dataTransfer.dropEffect = 'copy'; // for Chrome
                    }
                    wizard_qq.addClass(dropArea, self._classes.dropActive);
                    jQuery('#upload-place').css('border', '2px dashed rgba(255, 255, 255, 0.498)');
                    if (jQuery('ul.wizard_qq-files-to-upload li').length == 0) {
                        wizard_qq.addClass(uploadForm, self._classes.hideForm);
                    } else {
                        jQuery('.wizard_qq-files-to-upload-container').hide();
                    }
                    e.stopPropagation();
                } else {
                    e.dataTransfer.dropEffect = 'none';
                }

                e.preventDefault();
            }
        });

        wizard_qq.attach(dropArea, 'dragleave', function(e){
            if (isValidDrag(e)){

                dropArea.style.display = 'none';
                if (dropArea == e.target || wizard_qq.contains(dropArea,e.target)){
                    wizard_qq.removeClass(dropArea, self._classes.dropActive);
                    jQuery('#upload-place').css('border', '2px dashed rgba(255, 255, 255, 0.498)');
                    if (jQuery('ul.wizard_qq-files-to-upload li').length == 0) {
                        wizard_qq.removeClass(uploadForm, self._classes.hideForm);
                    } else {
                        jQuery('.wizard_qq-files-to-upload-container').show();
                    }
                    e.stopPropagation();
                } else {
                    if (hideTimeout){
                        clearTimeout(hideTimeout);
                    }

                    hideTimeout = setTimeout(function(){
                        uploadForm.style.display = 'block';
                    }, 77);
                }
            }
        });

        wizard_qq.attach(dropArea, 'drop', function(e){
            dropArea.style.display = 'none';
            self._addSelection(e.dataTransfer.files);
            e.preventDefault();
        });
    },
    _createUploadHandler: function(){
        var self = this,
            handlerClass;

        if(wizard_qq.WizardUploadHandlerXhr.isSupported()){
            handlerClass = 'WizardUploadHandlerXhr';
        } else {
            handlerClass = 'WizardUploadHandlerForm';
        }

        var handler = new wizard_qq[handlerClass]({
            action: this._options.action,
            onProgress: function(id, fileName, loaded, total){
                // is only called for xhr upload
                self._updateProgress(id, loaded, total);
            },
            onComplete: function(id, fileName, result){
                // mark completed
                var item = self._getItemByFileId(id);
                wizard_qq.remove(self._getElement(item, 'spinner'));

                if (result.success){
                    wizard_qq.remove(self._getElement(item, 'cancel'));
                    wizard_qq.addClass(item, self._classes.success);
                } else {
                    wizard_qq.addClass(item, self._classes.fail);

                    if (result.error){
                       self._error(result.error, fileName, id);
                    }
                }
                self._filesInProgress--;
                self._options.onComplete(id, fileName, result);
            }
        });

        return handler;
    },
    _onInputChange: function(input){
        var self = this,
            dropArea = this._getElement('drop'),
            uploadForm = this._getElement(document, 'uploadForm');
        if (this._handler instanceof wizard_qq.WizardUploadHandlerXhr){
            this._addSelection(input.files);

            dropArea.style.display = 'none';
            wizard_qq.addClass(uploadForm, self._classes.hideForm);
            if (jQuery('ul.wizard_qq-files-to-upload li').length == 0) {
                wizard_qq.removeClass(uploadForm, self._classes.hideForm);
            } else {
                jQuery('.wizard_qq-files-to-upload-container').show();
            }
        } else {
            if (this._validateFile(input)){
                this._addFile(input);
            }
        }

        this._button.reset();
    },
    _addSelection: function(files) {
        var valid = true;
        var i = files.length;
        while (i--){
            if (!this._validateFile(files[i])){
                valid = false;
                break;
            }
        }
        if (valid){
            var i = files.length;
            while (i--){
                this._addFile(files[i]);
            }
        }
    },
    _addFile: function(file) {
        var id = this._handler.add(file);
        var name = this._handler.getName(id);
        this._options.onSubmit(id, name);
        this._addToList(id, name);
        if (this._options.autoUpload) {
            this._queueUpload(id, this._options.params);
        }
        else this._options.onAfterSelect(file, id);
    },
    _uploadAll: function() {
        var allfiles = this._handler._files;
        for ( var id = 0; id < allfiles.length; id++ ) {
            if (allfiles[id]) {
                this._queueUpload(id, this._options.params);
            }
        }
    },
    _queueUpload: function(id, params) {
        var simUploadLimit = this._options.simUploadLimit;
        if (this._options.debugMode) this.logDebug('curruploads', this._filesInProgress);
        //alert(simUploadLimit + ' - ' + this._filesInProgress);
        if (this._filesInProgress < simUploadLimit || !simUploadLimit) {
            this._filesInProgress++;
            if (this._handler instanceof wizard_qq.WizardUploadHandlerXhr) var uid=id;
            else if (typeof id=='number') {
                var uid = 'wizard_qq-upload-handler-iframe' + id;
            }
            else  var uid = id;
            var item = this._getItemByFileId(uid);
            var spinner = this._getElement(item, 'spinner');
            wizard_qq.css(spinner, {'display':'inline-block'});
            this._handler.upload(id, params);
        }
        else {
            var self = this;
            window.setTimeout(function(){self._queueUpload(id, params)}, 100);}
    },
    _cancelAll: function() {
        var allfiles = this._handler._files;
        for ( var id = 0; id < allfiles.length; id++ ) {
            if (allfiles[id]) this._handler.cancel(id);
        }
    },
    _validateFile: function(file){
        var name,size;

        if (file.value){
            // it is a file input
            // get input value and remove path to normalize
            name = file.value.replace(/.*(\/|\\)/, "");
        } else {
            // fix missing properties in Safari
            name = file.fileName != null ? file.fileName : file.name;
            size = file.fileSize != null ? file.fileSize : file.size;
        }

        if (! this._isAllowedExtension(name)){
            this._error('typeError',name);
            return false;

        } else if (size === 0){
            this._error('emptyError',name);
            return false;

        } else if (size && this._options.sizeLimit && size > this._options.sizeLimit){
            this._error('sizeError',name);
            return false;
        }

        return true;
    },
    _addToList: function(id, fileName){
        var item = wizard_qq.toElement(this._options.fileTemplate);
        item.wizard_qqFileId = id;

        var fileElement = this._getElement(item, 'file');
        wizard_qq.setText(fileElement, this._formatFileName(fileName));
        this._getElement(document, 'list').appendChild(item);
        this._getElement(document, 'listContainer').style.display = 'block';
        // not the good place
        //this._filesInProgress++;
    },
    _updateProgress: function(id, loaded, total){
        var item = this._getItemByFileId(id);
        var size = this._getElement(item, 'size');
        var text1;
        var text2;
        if (loaded != total){
            text1 = Math.round(loaded / total * 100);
        } else {
            text1 = 100;
        }
        text2 = '&nbsp;' + this._formatSize(total);
        wizard_qq.setProgressBar(size, text1, text2);
    },
    _formatSize: function(bytes){
        var i = -1;
        do {
            bytes = bytes / 1024;
            i++;
        } while (bytes > 99);

        return Math.max(bytes, 0.1).toFixed(1) + ['kB', 'MB', 'GB', 'TB', 'PB', 'EB'][i];
    },
    _getItemByFileId: function(id){
        var item = this._getElement('list').firstChild;

        // there can't be text nodes in our dynamically created list
        // because of that we can safely use nextSibling
        while (item){
            if (item.wizard_qqFileId == id){
                return item;
            }

            item = item.nextSibling;
        }
    },
    /**
     * delegate click event for cancel link
     **/
    _bindCancelEvent: function(){
        var self = this,
            list = this._getElement('list');

        wizard_qq.attach(list, 'click', function(e){
            e = e || window.event;
            var target = e.target || e.srcElement;

            if (wizard_qq.hasClass(target, self._classes.cancel)){
                wizard_qq.preventDefault(e);

                var item = target.parentNode;
                self._handler.cancel(item.wizard_qqFileId);
                wizard_qq.remove(item);
            }
        });

    }
};

wizard_qq.WizardUploadButton = function(o){
    this._options = {
        element: null,
        // if set to true adds multiple attribute to file input
        multiple: false,
        // name attribute of file input
        name: 'file',
        onChange: function(input){},
        hoverClass: 'wizard_qq-upload-button-hover',
        focusClass: 'wizard_qq-upload-button-focus'
    };

    wizard_qq.extend(this._options, o);

    this._element = this._options.element;

    // make button suitable container for input
    wizard_qq.css(this._element, {
        position: 'relative',
        overflow: 'hidden',
        // Make sure browse button is in the right side
        // in Internet Explorer
        direction: 'ltr'
    });

    this._input = this._createInput();
};

wizard_qq.WizardUploadButton.prototype = {
    /* returns file input element */
    getInput: function(){
        return this._input;
    },
    /* cleans/recreates the file input */
    reset: function(){
        if (this._input.parentNode){
            wizard_qq.remove(this._input);
        }

        wizard_qq.removeClass(this._element, this._options.focusClass);
        this._input = this._createInput();
    },
    _createInput: function(){
        var div = document.createElement("div");
        var input = document.createElement("input");

        if (this._options.multiple){
            input.setAttribute("multiple", "multiple");
        }

        div.setAttribute('class', 'input-button-text');
        input.setAttribute("type", "file");
        input.setAttribute("name", this._options.name);

        wizard_qq.css(input, {
            position: 'absolute',
            // in Opera only 'browse' button
            // is clickable and it is located at
            // the right side of the input
            right: 0,
            top: 0,
            fontFamily: 'Arial',
            // if larger button becomes visible (filter is not applied in IE8 on SOME PCs)
            // probably related to http://social.msdn.microsoft.com/forums/en-US/iewebdevelopment/thread/29d0b0e7-4326-4b3e-823c-51420d4cf253
            fontSize: '243px',
            margin: 0,
            padding: 0,
            cursor: 'pointer',
            opacity: 0
        });

        // I had to set the text here to be into the button container.
        //div.innerHTML = 'Browse Files';
        this._element.appendChild(div);

        this._element.appendChild(input);

        var self = this;
        wizard_qq.attach(input, 'change', function(){
            self._options.onChange(input);
        });

        wizard_qq.attach(input, 'mouseover', function(){
            wizard_qq.addClass(self._element, self._options.hoverClass);
        });
        wizard_qq.attach(input, 'mouseout', function(){
            wizard_qq.removeClass(self._element, self._options.hoverClass);
        });
        wizard_qq.attach(input, 'focus', function(){
            wizard_qq.addClass(self._element, self._options.focusClass);
        });
        wizard_qq.attach(input, 'blur', function(){
            wizard_qq.removeClass(self._element, self._options.focusClass);
        });

        // IE and Opera, unfortunately have 2 tab stops on file input
        // which is unacceptable in our case, disable keyboard access
        if (window.attachEvent){
            // it is IE or Opera
            input.setAttribute('tabIndex', "-1");
        }

        return input;
    }
};

/**
 * Class for uploading files using form and iframe
 */
wizard_qq.WizardUploadHandlerForm = function(o){
    this._options = {
        // URL of the server-side upload script,
        // should be on the same domain to get response
        action: '/upload',
        // fires for each file, when iframe finishes loading
        onComplete: function(id, fileName, response){}
    };
    wizard_qq.extend(this._options, o);

    this._inputs = {};
    this._files = [];
};
wizard_qq.WizardUploadHandlerForm.prototype = {
    /**
     * Adds file input to the queue
     * Returns id to use with upload, cancel
     **/
    add: function(fileInput){
        fileInput.setAttribute('name', 'wizard_qqfile');
        var uid = wizard_qq.getUniqueId();
        var id = 'wizard_qq-upload-handler-iframe' + uid;

        this._inputs[id] = fileInput;
        this._files[uid] = fileInput;

        // remove file input from DOM
        if (fileInput.parentNode){
            wizard_qq.remove(fileInput);
        }

        return id;
    },
    /**
     * Sends the file identified by id and additional query params to the server
     * @param {Object} params name-value string pairs
     */
    upload: function(id, params){
        if (typeof id=='number') {
            var id = 'wizard_qq-upload-handler-iframe' + id;
        }

        var input = this._inputs[id];

        if (!input){
            throw new Error('file with passed id was not added, or already uploaded or cancelled');
        }

        var fileName = this.getName(id);

        var iframe = this._createIframe(id);
        var form = this._createForm(iframe, params);
        form.appendChild(input);
        var self = this;
        this._attachLoadEvent(iframe, function(){
            self._options.onComplete(id, fileName, self._getIframeContentJSON(iframe));

            delete self._inputs[id];
            uid = id.replace('wizard_qq-upload-handler-iframe','');
            self._files[uid] = null;
            // timeout added to fix busy state in FF3.6
            setTimeout(function(){
                wizard_qq.remove(iframe);
            }, 1);
        });

        form.submit();
        wizard_qq.remove(form);

        return id;
    },
    cancel: function(id){
        if (id in this._inputs){
            delete this._inputs[id];
            uid = id.replace('wizard_qq-upload-handler-iframe','');
            this._files[uid] = null;
        }

        var iframe = document.getElementById(id);
        if (iframe){
            // to cancel request set src to something else
            // we use src="javascript:false;" because it doesn't
            // trigger ie6 prompt on https
            iframe.setAttribute('src', 'javascript:false;');

            wizard_qq.remove(iframe);
        }
    },
    getName: function(id){
        // get input value and remove path to normalize
        return this._inputs[id].value.replace(/.*(\/|\\)/, "");
    },
    _attachLoadEvent: function(iframe, callback){
        wizard_qq.attach(iframe, 'load', function(){
            // when we remove iframe from dom
            // the request stops, but in IE load
            // event fires
            if (!iframe.parentNode){
                return;
            }

            // fixing Opera 10.53
            if (iframe.contentDocument &&
                iframe.contentDocument.body &&
                iframe.contentDocument.body.innerHTML == "false"){
                // In Opera event is fired second time
                // when body.innerHTML changed from false
                // to server response approx. after 1 sec
                // when we upload file with iframe
                return;
            }

            callback();
        });
    },
    /**
     * Returns json object received by iframe from server.
     */
    _getIframeContentJSON: function(iframe){
        // iframe.contentWindow.document - for IE<7
        var doc = iframe.contentDocument ? iframe.contentDocument: iframe.contentWindow.document,
            response;

        try{
            response = eval("(" + doc.body.innerHTML + ")");
        } catch(err){
            response = {};
        }

        return response;
    },
    /**
     * Creates iframe with unique name
     */
    _createIframe: function(id){
        // We can't use following code as the name attribute
        // won't be properly registered in IE6, and new window
        // on form submit will open
        // var iframe = document.createElement('iframe');
        // iframe.setAttribute('name', id);

        var iframe = wizard_qq.toElement('<iframe src="javascript:false;" name="' + id + '" />');
        // src="javascript:false;" removes ie6 prompt on https

        iframe.setAttribute('id', id);

        iframe.style.display = 'none';
        document.body.appendChild(iframe);

        return iframe;
    },
    /**
     * Creates form, that will be submitted to iframe
     */
    _createForm: function(iframe, params){
        // We can't use the following code in IE6
        // var form = document.createElement('form');
        // form.setAttribute('method', 'post');
        // form.setAttribute('enctype', 'multipart/form-data');
        // Because in this case file won't be attached to request
        var form = wizard_qq.toElement('<form method="post" enctype="multipart/form-data"></form>');

        var queryString = '?' + wizard_qq.obj2url(params);

        form.setAttribute('action', this._options.action + queryString);
        form.setAttribute('target', iframe.name);
        form.style.display = 'none';
        document.body.appendChild(form);

        return form;
    }
};

/**
 * Class for uploading files using xhr
 */
wizard_qq.WizardUploadHandlerXhr = function(o){
    this._options = {
        // url of the server-side upload script,
        // should be on the same domain
        action: '/upload',
        onProgress: function(id, fileName, loaded, total){},
        onComplete: function(id, fileName, response){}
    };
    wizard_qq.extend(this._options, o);

    this._files = [];
    this._xhrs = [];
};

// static method
wizard_qq.WizardUploadHandlerXhr.isSupported = function(){
    var input = document.createElement('input');
    input.type = 'file';

    return (
        'multiple' in input &&
        typeof File != "undefined" &&
        typeof (new XMLHttpRequest()).upload != "undefined" );
};

wizard_qq.WizardUploadHandlerXhr.prototype = {
    /**
     * Adds file to the queue
     * Returns id to use with upload, cancel
     **/
    add: function(file){
        return this._files.push(file) - 1;
    },
    /**
     * Sends the file identified by id and additional query params to the server
     * @param {Object} params name-value string pairs
     */
    upload: function(id, params){
        var file = this._files[id],
            name = this.getName(id),
            size = this.getSize(id);

        if (!file){
            throw new Error('file with passed id was not added, or already uploaded or cancelled');
        }

        var xhr = this._xhrs[id] = new XMLHttpRequest();

        var self = this;

        xhr.upload.onprogress = function(e){
            if (e.lengthComputable){
                self._options.onProgress(id, name, e.loaded, e.total);
            }
        };

        xhr.onreadystatechange = function(){
            // the request was aborted/cancelled
            if (!self._files[id]){
                return;
            }

            if (xhr.readyState == 4){

                self._options.onProgress(id, name, size, size);

                if (xhr.status == 200){
                    var response;

                    try {
                        response = eval("(" + xhr.responseText + ")");
                    } catch(err){
                        response = {};
                    }

                    self._options.onComplete(id, name, response);

                } else {
                    self._options.onComplete(id, name, {});
                }

                self._files[id] = null;
                self._xhrs[id] = null;
            }
        };

        // build query string
        var queryString = '?wizard_qqfile=' + encodeURIComponent(name) + '&' + wizard_qq.obj2url(params);
        xhr.open("POST", this._options.action + queryString, true);
        xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
        xhr.setRequestHeader("X-File-Name", encodeURIComponent(name));
        // important : without content-type zope HTTPRequest don't accept the file
        // so, for webkit which don't send content-type header
        // but also with Mozilla sometimes
        // we just set a bad octet/stream mime-type
        // (not important since server side will do the good job around mime-type)
        xhr.setRequestHeader("Content-Type", 'application/octet-stream');
        xhr.send(file);

    },
    cancel: function(id){
        this._files[id] = null;

        if (this._xhrs[id]){
            this._xhrs[id].abort();
            this._xhrs[id] = null;
        }
    },
    getName: function(id){
        // fix missing name in Safari 4
        var file = this._files[id];
        return file.fileName != null ? file.fileName : file.name;
    },
    getSize: function(id){
        // fix missing size in Safari 4
        var file = this._files[id];
        return file.fileSize != null ? file.fileSize : file.size;
    }
};

//
// Helper functions
//

var wizard_qq = wizard_qq || {};

//
// Useful generic functions

/**
 * Adds all missing properties from obj2 to obj1
 */
wizard_qq.extend = function(obj1, obj2){
    for (var prop in obj2){
        obj1[prop] = obj2[prop];
    }
};

/**
 * @return {Number} unique id
 */
wizard_qq.getUniqueId = (function(){
    var id = 0;
    return function(){
        return id++;
    };
})();

//
// Events

wizard_qq.attach = function(element, type, fn){
    if (element.addEventListener){
        element.addEventListener(type, fn, false);
    } else if (element.attachEvent){
        element.attachEvent('on' + type, fn);
    }
};
wizard_qq.detach = function(element, type, fn){
    if (element.removeEventListener){
        element.removeEventListener(type, fn, false);
    } else if (element.attachEvent){
        element.detachEvent('on' + type, fn);
    }
};

wizard_qq.preventDefault = function(e){
    if (e.preventDefault){
        e.preventDefault();
    } else{
        e.returnValue = false;
    }
};
//
// Node manipulations

/**
 * Insert node a before node b.
 */
wizard_qq.insertBefore = function(a, b){
    b.parentNode.insertBefore(a, b);
};
wizard_qq.remove = function(element){
    element.parentNode.removeChild(element);
};

wizard_qq.contains = function(parent, descendant){
    if (parent.contains){
        return parent.contains(descendant);
    } else {
        return !!(descendant.compareDocumentPosition(parent) & 8);
    }
};

/**
 * Creates and returns element from html string
 * Uses innerHTML to create an element
 */
wizard_qq.toElement = (function(){
    var div = document.createElement('div');
    return function(html){
        div.innerHTML = html;
        var element = div.firstChild;
        div.removeChild(element);
        return element;
    };
})();

//
// Node properties and attributes

/**
 * Sets styles for an element.
 * Fixes opacity in IE6-8.
 */
wizard_qq.css = function(element, styles){
    if (styles.opacity != null){
        if (typeof element.style.opacity != 'string' && typeof(element.filters) != 'undefined'){
            styles.filter = 'alpha(opacity=' + Math.round(100 * styles.opacity) + ')';
        }
    }
    wizard_qq.extend(element.style, styles);
};
wizard_qq.hasClass = function(element, name){
    var re = new RegExp('(^| )' + name + '( |$)');
    return re.test(element.className);
};
wizard_qq.addClass = function(element, name){
    if (!wizard_qq.hasClass(element, name)){
        element.className += ' ' + name;
    }
};
wizard_qq.removeClass = function(element, name){
    var re = new RegExp('(^| )' + name + '( |$)');
    element.className = element.className.replace(re, ' ').replace(/^\s+|\s+$/g, "");
};
wizard_qq.setText = function(element, text){
    element.innerText = text;
    element.textContent = text;
};
wizard_qq.setProgressBar = function(element, text1, text2){
    if (! element.hasChildNodes()) {
        if (! text1 ) size='2px';
        else size = text1+ '%';
        var progressBar = '<div class="sizeContainer"><div class="sizeBar" style="width:' + size + '"></div></div>';
        var total = '<div class="sizeTotal">' + text2 + '</div>';
        element.innerHTML = total + progressBar;
    }
    else {
        var sizeBar = wizard_qq.getByClass(element, "sizeBar")[0];
        sizeBar.style.width = text1+ '%';
    }
};

//
// Selecting elements

wizard_qq.children = function(element){
    var children = [],
    child = element.firstChild;

    while (child){
        if (child.nodeType == 1){
            children.push(child);
        }
        child = child.nextSibling;
    }

    return children;
};

wizard_qq.getByClass = function(element, className){
    if (element.querySelectorAll){
        return element.querySelectorAll('.' + className);
    }

    var result = [];
    var candidates = element.getElementsByTagName("*");
    var len = candidates.length;

    for (var i = 0; i < len; i++){
        if (wizard_qq.hasClass(candidates[i], className)){
            result.push(candidates[i]);
        }
    }
    return result;
};

/**
 * obj2url() takes a json-object as argument and generates
 * a querystring. pretty much like jQuery.param()
 *
 * @param  Object JSON-Object
 * @param  String current querystring-part
 * @return String encoded querystring
 */
wizard_qq.obj2url = function(obj, temp){
    var uristrings = [],
        add = function(nextObj, i){

            var nextTemp = temp
              ? (/\[\]$/.test(temp)) /* prevent double-encoding */
                  ? temp
                  : temp+'['+i+']'
              : i;

          uristrings.push(typeof nextObj === 'object'
              ? wizard_qq.obj2url(nextObj, nextTemp)
              : (Object.prototype.toString.call(nextObj) === '[object Function]')
                  ? encodeURIComponent(nextTemp) + '=' + encodeURIComponent(nextObj())
                  : encodeURIComponent(nextTemp) + '=' + encodeURIComponent(nextObj));
        };

    if (Object.prototype.toString.call(obj) === '[object Array]'){
        // we wont use a for-in-loop on an array (performance)
        for (var i = 0, len = obj.length; i < len; ++i){
            add(obj[i], i);
        }

    } else if ((obj !== undefined) &&
               (obj !== null) &&
               (typeof obj === "object")){

        // for anything else but a scalar, we will use for-in-loop
        for (var i in obj){
            add(obj[i], i);
        }
    } else {
        uristrings.push(encodeURIComponent(temp) + '=' + encodeURIComponent(obj));
    }

    return uristrings.join('&').replace(/%20/g, '+');
};
