// add strip method to String class
if(typeof(String.prototype.strip) === "undefined") {
  String.prototype.strip = function(){
    return String(this).replace(/^\s+|\s+$/g, '');
  };
};

function pad (str, max) {
  str = str.toString();
  return str.length < max ? pad("0" + str, max) : str;
}

// add outerHTML support to jQuery
jq.fn.outerHTML = function(s) {
  return (s) ? this.before(s).remove():
    jQuery("&lt;p&gt;").append(this.eq(0).clone()).html();
};

function attachPortletButtons() {
  // Handle DeferredPorletLoaded event
  jq('body').on('DeferredPorletLoaded', function(event, data) {
    setPortletButtons('#' + data.id);
  });

  setPortletButtons('.portletWrapper');
}

function setPortletButtons(selector) {

  // add up/down and left/right links to portlet headers,
  // which will expand/contract and make portlets wide
  jq(selector + ' dt.portletHeader .portletTopRight').before(
    '<a href="#" class="portletToggleLink" title="Toggle ' +
    'Portlet">toggle</a>');
  jq(selector + ' dt.portletHeader a.portletToggleLink').click(function(event){
    // toggle html class
    var a = jq(event.target);
    var portlet = a.parents(selector);
    portlet.toggleClass('closed');

    if (!portlet.attr('id')) {
      return false;
    }

    // record change on the server side
    var hash = portlet.attr('id').slice('portletwrapper-'.length);
    if (hash) {
      jq.post(portal_url + '/@@record-portlet-state',
        {'hash': hash,
         'action': 'closed',
         'value': portlet.is('.closed') ? '1' : '0'});
    }
    return false;
  });
  jq('#dashboard ' + selector + ' dt.portletHeader .portletTopRight').before(
    '<a href="#" class="portletWideNarrowLink" title="Wide/Narrow">wide/narrow'
    + '</a>');
  jq('#dashboard ' + selector + ' dt.portletHeader a.portletWideNarrowLink').click(function(event){
    // toggle html class
    var a = jq(event.target);
    var portlet = a.parents('.portletWrapper');
    portlet.toggleClass('wide');

    // record change on the server side
    var hash = portlet.attr('id').slice('portletwrapper-'.length);
    if (hash) {
      jq.post(portal_url + '/@@record-portlet-state',
        {'hash': hash,
         'action': 'wide',
         'value': portlet.is('.wide') ? '1' : '0'});
    }
    return false;
  });
}

function attachHeaderViewletCloseOpen() {
  // add close link
  if (jq('#vnccollab-header a.closeLink').length == 0) {
    jq('#vnccollab-header').append('<a class="actionLink closeLink" '+
      'title="Click to contract" href="#">Close</a>');
  }

  jq('#vnccollab-header a.closeLink').click(function(event){
    var container = jq(event.target).parents('#vnccollab-header');
    if (container.length == 0) {
      return false;
    }

    if (container.is('.opened')) {
      container.removeClass('opened').addClass('closed');
      createCookie('vnccollab_header_state', 'closed', 365);
    }

    return false;
  });
  jq('#vnccollab-header a.openLink').click(function(event){
    var container = jq(event.target).parents('#vnccollab-header');
    if (container.length == 0) {
      return false;
    }

    if (container.is('.closed')) {
      container.removeClass('closed').addClass('opened');
      createCookie('vnccollab_header_state', 'opened', 365);
    }

    return false;
  });
}

textile_settings = {
    nameSpace:           "textile", // Useful to prevent multi-instances CSS conflict
    onShiftEnter:        {keepDefault:false, replaceWith:'\n\n'},
    markupSet: [
        {name:'Heading 1', key:'1', openWith:'h1(!(([![Class]!]))!). ', placeHolder:'Your title here...' },
        {name:'Heading 2', key:'2', openWith:'h2(!(([![Class]!]))!). ', placeHolder:'Your title here...' },
        {name:'Heading 3', key:'3', openWith:'h3(!(([![Class]!]))!). ', placeHolder:'Your title here...' },
        {name:'Heading 4', key:'4', openWith:'h4(!(([![Class]!]))!). ', placeHolder:'Your title here...' },
        {name:'Heading 5', key:'5', openWith:'h5(!(([![Class]!]))!). ', placeHolder:'Your title here...' },
        {name:'Heading 6', key:'6', openWith:'h6(!(([![Class]!]))!). ', placeHolder:'Your title here...' },
        {name:'Paragraph', key:'P', openWith:'p(!(([![Class]!]))!). '},
        {separator:'---------------' },
        {name:'Bold', key:'B', closeWith:'*', openWith:'*'},
        {name:'Italic', key:'I', closeWith:'_', openWith:'_'},
        {name:'Stroke through', key:'S', closeWith:'-', openWith:'-'},
        {separator:'---------------' },
        {name:'Bulleted list', openWith:'(!(* |!|*)!)'},
        {name:'Numeric list', openWith:'(!(# |!|#)!)'},
        {separator:'---------------' },
        {name:'Picture', replaceWith:'![![Source:!:http://]!]([![Alternative text]!])!'},
        {name:'Link', openWith:'"', closeWith:'([![Title]!])":[![Link:!:http://]!]', placeHolder:'Your text to link here...' },
        {separator:'---------------' },
        {name:'Quotes', openWith:'bq(!(([![Class]!]))!). '},
        {name:'Code', openWith:'@', closeWith:'@'},
    ]
}

function set_textile_editor() {
  $this = jq(this);
  if ($this.val() === 'text/x-web-textile') {
    jq('#text').markItUp(textile_settings);
  } else {
    jq('#text').markItUpRemove();
  }
}

function init_textile_editor() {
  $text_text_format = jq('#text_text_format');
  $text_text_format.change(set_textile_editor);
  set_textile_editor.call($text_text_format);
}

function addSlimScrollingToDashboardPortlets() {
  jq('#dashboard-portlets .portletBody:not(.noSlimScroll)').slimScroll({
    'height': '246px'
  });
}

function init_special_rss_portlet() {
  function hide_all() {
    jq('.special-rss-item').hide().removeClass('selected');
  }

  function show_first(selector) {
    // Selects the first element with class special-rss-item
    jq(selector + ' .special-rss-item').first().show().addClass('selected');
  }

  function next() {
    var $item = jq('.special-rss-item.selected');
    var $sibling = $item.next();
    if ($sibling.length !== 0) {
      $item.removeClass('selected').hide();
      $sibling.show().addClass('selected');
    }
  }

  function prev() {
    var $item = jq('.special-rss-item.selected');
    var $sibling = $item.prev();
    if ($sibling.length !== 0) {
      $item.removeClass('selected').hide();
      $sibling.show().addClass('selected');
    }
  }

  function change_feed() {
    var feed = $(this).attr('feed');
    hide_all();
    show_first('#special-rss-feed-' + feed);
  }

  hide_all();
  jq('#special-rss-nav-prev').click(prev);
  jq('#special-rss-nav-next').click(next);
  jq('.special-rss-links a').click(change_feed);
  show_first('.portletSpecialRSS');
}

function initPortletDashlet() {
  function reloadPortletDashletContent(e) {
    var target = e.target;
    var url = target.getAttribute('href');
    var $container = jq(target).parents('.portletDashlet');
    var $content = $container.find('.portletBody');

    jq.get(url, function(r) {
        $content.html(r);
        // selecte current action
        jq(target).parents('ul').find('li').removeClass('selected');
        jq(target).parent().addClass('selected');
        $content.find('.portletBody').slimScroll({'height': '205px'});
    });
    e.preventDefault();
  }

  jq('.portletDashlet').delegate('.dashlet-action', 'click',
                                 reloadPortletDashletContent);
  jq('.dashlet-action').first().click();
}

function attachSocialBookmarksLink() {
  jq('#document-action-socialbookmark a').click(function(event) {
    jq('.sc_social_bookmarks_viewlet').toggleClass('visible');
    return false;
  });
}

function attachCalendarWidgets(container) {
  if (!container || container.length == 0) {
    var container = jq('body');
  }

  jq('input.datepicker-widget', container).each(function(elem, ids){
    var for_display = jq(this), field = for_display.parent();
    var input = field.find('input[type=hidden]'), iid = input.attr('id');

    // skip if widget is already initialized
    if (field.find('img.ui-datepicker-trigger').length > 0) {
      return;
    }

    // attach date picker
    // TODO: get below options from server side widget factory
    // TODO: add i18n
    var datepicker = input.datepicker({
      'dateFormat': "dd/mm/yy",
      'altField': for_display,
      // 'altField': "#" + iid + "-for-display",
      'shortYearCutoff': 10,
      'showAnim': "show",
      'maxDate': null,
      'isRTL': false,
      'dayNamesShort': ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
      'changeYear': true,
      'duration': "normal",
      'monthNames': ['January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November',
        'December'],
      'dayNames': ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday',
        'Friday', 'Saturday'],
      'constrainInput': true,
      'stepMonths': 1,
      'showButtonPanel': false,
      'changeFirstDay': true,
      'altFormat': "DD, d MM, yy",
      'beforeShowDay': null,
      'changeMonth': true,
      'monthNamesShort': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul',
        'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
      'gotoCurrent': false,
      'defaultDate': null,
      'yearRange': "-10:+10",
      'hideIfNoPrevNext': false,
      'showOtherMonths': false,
      'showOptions': {},
      'showInline': false,
      'buttonImageOnly': true,
      'numberOfMonths': 1,
      'prevText': "<Prev",
      'nextText': "Next>",
      'minDate': null,
      'buttonImage': "popup_calendar.gif",
      'beforeShow': null,
      'navigationAsDateFormat': false,
      'buttonText': "...",
      'firstDay': 0,
      'dayNamesMin': ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'],
      'currentText': "Today",
      'calculateWeek': "$.datepicker.iso8601Week",
      'closeText': "Close",
      'showOn': "both"
    });
    // set for-display field to read-only mode
    for_display.attr("readonly", "readonly");
    // add embed class to it
    for_display.addClass('embed');
    // and set it's value based on hidden widget value
    for_display.each(function() {
      jq(this).val(jq.datepicker.formatDate("DD, d MM, yy",
        input.datepicker('getDate'),
        {'shortYearCutoff': 10,
         'dayNamesShort': ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
         'dayNames': ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday',
           'Friday', 'Saturday'],
         'monthNamesShort': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul',
           'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
         'monthNames': ['January', 'February', 'March', 'April', 'May', 'June',
           'July', 'August', 'September', 'October', 'November', 'December']}
      ));
    });
    // attach calendar delete control
    jq("#" + iid + "-clear", container).click(function() {
      input.val('');
      for_display.val('');
    });

  });
}

function initNewTicketForm(container) {
  if (!container || container.length == 0) {
    var container = jq('body');
  }

  var $zimbraTaskForm = jq('#zimbra-contents', container),
      $redmineTaskForm = jq('#redmine-contents', container),
      $typeOfTicket = jq('#form-widgets-type_of_ticket', container);

  function toggleSubforms(toShow) {
    if (toShow == 'zimbra'){
      $zimbraTaskForm.show();
      $redmineTaskForm.hide();
    } else {
      $zimbraTaskForm.hide();
      $redmineTaskForm.show();
    }
  }

  function onTypeOfTicketChange() {
    // Event to show the right subform
    if ($typeOfTicket.length == 0) {
        // If there's no typeOfTicket, there's nothing to hide
        return;
    }
    toggleSubforms($typeOfTicket.val());
  }

  $typeOfTicket.change(onTypeOfTicketChange);
  onTypeOfTicketChange();
}

function attachNewTicketAction() {
  jq('#document-action-new_ticket a').prepOverlay({
      'subtype': 'ajax',
      'filter': '#content>*',
      'formselector': 'form#zimbra_task_form,form#file_ticket_form,form#new_ticket_form',
      'noform': function(el) {return noformerrorshow(el, 'reload');},
      'afterpost' : function(el) {
          initNewTicketForm(el);
          attachCalendarWidgets(el);
      },
      'config' : {
          'onBeforeLoad' : function(){
            initNewTicketForm();
            attachCalendarWidgets();
          }
      }
  });
}

//
// animateContentWizardStep
//
function animateContentWizardStep( stepNum, reset ) {
  if ( stepNum == 2 ) {
    // delete upload marker
    jq('#wizard-uploader-marker').remove();
  }
  if ( reset ) {
    jq('.tab_link').addClass('blocked').removeClass('inactive').removeClass('active');
  } else {
    jq('.tab_link').filter('.active').removeClass('active').addClass('inactive');
  }
  jq('#tab_'+stepNum).addClass('active').removeClass('blocked');
  jq('#tab_'+stepNum).removeClass('inactive');

  jq('#wizard-steps').animate({
    marginLeft: '-' + (960 * stepNum - 960)
  }, 400);
}

//
// simpleValidateFormWizard
//
function simpleValidateFormWizard() {
  var resp = true;

  jq('.wizard-required').find('input[type=text]').each(function() {
    if(jq(this).val() == '') {
      jq(this).addClass('error-required');
      jq(this).prev('.fieldErrorBox').show().html('This field is required !');
      resp = false;
    } else {
      jq(this).prev('.fieldErrorBox').hide();
      jq(this).removeClass('error-required');
    }
  });
  jq('.wizard-required').find('textarea').each(function() {
    if(jq(this).val() == '') {
      jq(this).addClass('error-required');
      jq(this).prev('.fieldErrorBox').show().html('This field is required !');
      resp = false;
    }  else {
      jq(this).prev('.fieldErrorBox').hide();
      jq(this).removeClass('error-required');
    }
  });
  jq('.wizard-required').find('input[type=file]').each(function() {
    if(jq(this).val() == '') {
      jq(this).addClass('error-required');
      jq(this).parent().siblings('.fieldErrorBox').show().html('This file is required !');
      resp = false;
    } else {
      jq(this).parent().siblings('.fieldErrorBox').hide();
      jq(this).removeClass('error-required');
    }
  });

  return resp;
}

//
// loadCreateWizard
//
function loadCreateWizard(href, callback) {

  // show overlay and ajax spinner
  jq('.wizard-overlay').show();

  jq.ajax({
    type: 'GET',
    url: href,
    dataType: 'html',
    async: true,
    cache: false,
    success: function( data ){

      var $newform = jq(data).find('form[name=edit_form]');

      $newform.find('fieldset').not('#fieldset-default').remove();
      $newform.find('.formTabs').remove();
      $newform.find('.editionComment').remove();
      $newform.find('.field:has(span.required)').addClass('wizard-required');
      $newform.find('#archetypes-fieldname-description').addClass('wizard-field');
      $newform.find('#archetypes-fieldname-title').addClass('wizard-field');
      $newform.find('.field:not(.wizard-required, .wizard-field)').hide();

      jq('#createWizard form[name="edit_form"]').remove();
      jq('.step2 .step-content').prepend($newform);
      jq('.wizard-overlay').hide();
      //jq('.step3 .destination-label').after(href);

      callback();
      initJsCalendar();

    },
    error: function(){
      // TODO: make smart alert only when something really goes wrong
      //       Now we get alerts even when user reloads page before ajax
      //       call hasn't finished
      // alert('Sorry, something went wrong on the server. Please, try ' +
      //       'a bit later.');
      jq('.wizard-overlay').hide();
    }

  });

}

//
// addDocumentContentShadows
//
function addDocumentContentShadows(){
  var document_container = jq('.portaltype-document #content-core');
  if (document_container.length == 0) {
    return false;
  }
    document_container.before('<div class="content-top-shadow"></div>');
    document_container.after('<div class="content-bottom-shadow"></div>');
}

//
// fixGeneralUI
//

function fixGeneralUI(){
  // removes wrong entry in Content TOC
  var $last = jq('.toc').find('li').last();
  if($last.text() == "Bookmark & Share") {
    $last.remove();
  }
}

//
// setHandlersWizard
//
function setHandlersWizard() {

  var wizard_container = jq('#createWizard');
  if (wizard_container.length == 0) {
    return false;
  }

  //set create Wizard handler
  jq('#wizard-steps').on('click', '.Item', function( event ) {
    event.preventDefault();

    jq('#tree').data('contentType', jq(this).attr('data'));
    jq('.selectedContainer').html('');
    jq('input[name=selected_destination]').get(0).setAttribute('data', '');

    loadCreateWizard(jq(this).attr('href'), function(){
      animateContentWizardStep(2);
      jq('#tab_3').removeClass('inactive').addClass('blocked');
    });
  });

  // set control Step Wizard handler
  jq('.tab').on('click', '.inactive', function( event ) {
    event.preventDefault();

    var stepNum = parseInt( jq(this).attr('rel'),10 );
    if( stepNum > 0 ) {
      animateContentWizardStep(stepNum);
    }
  });

  jq('.tab').on('click', '.blocked', function( event ) {
     event.preventDefault();
     event.stopPropagation();
  });

  jq('.tab').on('click', '.active', function( event ) {
     event.preventDefault();
     event.stopPropagation();
  });

  // set close Wizard
  jq('.close_link').click(function(event) {
    event.preventDefault();
    animateContentWizardStep(1);
    jq('#createWizard').slideUp('fast');
    jq(this).removeClass('open');
    jq('#add-arrow').removeClass('open');
    animateContentWizardStep(1, true);
  });

  // set Add New Content button handler
  jq('#add-plus').click(function() {
    if( jq('#createWizard').is(':hidden') ) {
      jq('#createWizard').slideDown('fast');
      jq(this).addClass('open');
      jq('#add-arrow').addClass('open');
    } else {
      jq('#createWizard').slideUp('fast');
      jq(this).removeClass('open');
      jq('#add-arrow').removeClass('open');
    }
    return false;
  });

  jq('#send-wizard').click(function() {
    if( jq('input[name=selected_destination]').attr('data') != undefined && jq('input[name=selected_destination]').attr('data') != "" ) {
      if (jq("#wizard-uploader-marker").length > 0) {
        // file upload
        uploader = window[jq("#wizard-uploader-marker").val()];
        WizardUpload.sendDataAndUpload(uploader, jq('input[name=selected_destination]').attr('data'));
      } else if( simpleValidateFormWizard() ) {
        jq('form[name="edit_form"]').get(0).submit();
      } else {
        animateContentWizardStep(2);
      }
    }
  });

  jq('#send-step2').click(function() {

    var firstTree = false,
        $tree = jq('#tree');

    if( !simpleValidateFormWizard() ) {
      return false;
    }

    animateContentWizardStep(3);
    attachSearchDestinationAutocomplete();

    if ( $tree.find('.dynatree-container')[0] == undefined ) {
      firstTree = true;
    }

    $tree.dynatree({
      initAjax: { url: cloudstream_url+'/@@wizard_get_initial_tree.json',
                  cache: false,
                  'data': {'type_': $tree.data('contentType')}
                },
      onLazyRead: function(node){
                    node.appendAjax({
                      'url': cloudstream_url+'/@@wizard_get_tree.json',
                      'data': {'uid': node.data.key, 'type_': $tree.data('contentType')},
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
        newcontenturl += jq('form[name=edit_form]').attr('action').split('portal_factory')[1];
        newactionform = window.location.protocol + '//' + window.location.host + newcontainter + newcontenturl;

        jq('.selectedContainer').html(newcontainter);
        jq('input[name=selected_destination]').get(0).setAttribute('data', newcontainter);
        jq('form[name=edit_form]').get(0).setAttribute('action', newactionform);
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
     $tree.dynatree("getTree").reload();
    }

  });

}

function initLanguageSelector() {
  var currentLanguage = jq('#vnc-languageselector').find('.currentLanguage').text();
  jq('#selected-language').text(currentLanguage);
}

function initSearchTooltip() {
    // set search tooltip event handler
  jq('.explain-prefix').css('display','none');
  jq('#portal-searchbox #searchGadget').focus( function(){
    jq('.explain-prefix').delay(1300).fadeTo(500, 1).delay(7000).fadeTo(300, 0);
  });

  jq('#portal-searchbox #searchGadget').blur( function(){
    jq('.explain-prefix').css('display', 'none');
  });
}

// initialize fields
function initJsCalendar() {
    $('.plone_jscalendar').each(function () {
      var self = this;
      var name = $(self).children().first().attr('name');
      var id = $(self).children().first().attr('id');
      var btn = $(this).append('<img src="' + portal_url + '/popup_calendar.png" class="dt-picker" alt="" title="" height="16" width="16"><input value="none" style="visibility:hidden; width:1px;" type="text" class="dt-value"/>');
      $(this).find('.dt-value').datetimepicker({
        todayButton: true,
        onClose: function(datetime) {
          var date = new Date(Date.parse(datetime.dateFormat('Y-m-d H:i:s')));
          hours = date.getHours();
          suffex = (hours >= 12)? 'PM' : 'AM';
          hours = (hours > 12)? hours -12 : hours;
          hours = (hours == '00')? 12 : hours;
          $(self).find('#' + id + '_year').val(date.getFullYear());
          $(self).find('#' + id + '_month').val(pad(date.getMonth()+1, 2));
          $(self).find('#' + id + '_day').val(pad(date.getDate(), 2));
          $(self).find('#' + id + '_hour').val(pad(hours, 2));
          $(self).find('#' + id + '_minute').val(pad(date.getMinutes(), 2));
          $(self).find('#' + id + '_ampm').val(suffex);
        }
      });
      $(this).find('.dt-picker').click(function() {
        var val_input = $(self).find('.dt-value');
        $(self).find('.dt-value').datetimepicker('show');
      });
    });
};

var selected;
var selected_destinations = [];
function attachSearchDestinationAutocomplete() {
  // prevent press enter key
  jq('input#search-destination').keypress(function(e){
    if ( e.which == 13 ) {
      e.preventDefault();
    }
  });

  jq('input#search-destination').autocomplete({
    delay: 300,
    cache: false,
    autoFocus: true,
    minLength: 1,
    dataType: 'json',
    position: {
      my: "left top",
      at: "left bottom"
    },
    source: function( request, response ) {
      // loads user/groups to invite
      var data = {'SearchableText': jq('#search-destination').val()};
      jq.ajax({
        type: 'GET',
        dataType: 'json',
        url: portal_url + '/@@wizard_search_destination.json?type_='+jq('#tree').data('contentType'),
        cache: false,
        data: extendCastData(data),
        success: function( data ){
          response($.map(data, function(item) {
              return {
                  label: item.title,
                  path: item.path,
                  data: item
              }
          }))
        },
        error: function(){
          response([]);
        }
      });
    },
    focus: function(event, ui) {
      return false;
    },
    select: function (event, ui) {
      event.preventDefault();
      // selected = true;
      //
      var ac_path = ui.item.path;
      var newcontainter = '';
      var newactionform = '';
      var newcontenturl = '/portal_factory';
      newcontainter = ui.item.path;
      newcontenturl += jq('form[name=edit_form]').attr('action').split('portal_factory')[1];
      newactionform = window.location.protocol + '//' + window.location.host + newcontainter + newcontenturl;

      jq('.selectedContainer').html(ac_path);
      jq('.selectedContainer').html(newcontainter);
      jq('input[name=selected_destination]').get(0).setAttribute('data', newcontainter);
      jq('form[name=edit_form]').get(0).setAttribute('action', newactionform);
      jq('input#search-destination').val(ui.item.label);
    },
    open: function() {
      var $autocompleteContainer = jq('#search-destination').autocomplete("widget");
      $autocompleteContainer.addClass("cast-destination-object-autocomplete")
          .removeClass('ui-menu ui-widget ui-widget-content ui-corner-all');
    }
  }).data('autocomplete')._renderItem = function (ul, item) {
        return jq('<li />')
            .data('item.autocomplete', item)
            .append('<a>' + item.label + '</span></a>')
            .appendTo(ul);
  };

}

jq(function() {
  attachNewTicketAction();
  attachHeaderViewletCloseOpen();
  attachPortletButtons();
  init_textile_editor();
  addSlimScrollingToDashboardPortlets();
  init_special_rss_portlet();
  initPortletDashlet();
  initNewTicketForm();
  initLanguageSelector();
  attachSocialBookmarksLink();
  initSearchTooltip();
  setHandlersWizard();
  addDocumentContentShadows();
  fixGeneralUI();
});
