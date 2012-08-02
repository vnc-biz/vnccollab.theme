// add outerHTML support to jQuery
jq.fn.outerHTML = function(s) {
  return (s) ? this.before(s).remove():
    jQuery("&lt;p&gt;").append(this.eq(0).clone()).html();
};

function attachPortletButtons() {
  // add up/down and left/right links to portlet headers,
  // which will expand/contract and make portlets wide
  jq('.portletWrapper dt.portletHeader .portletTopRight').before(
    '<a href="#" class="portletToggleLink" title="Toggle ' +
    'Portlet">toggle</a>');
  jq('.portletWrapper dt.portletHeader a.portletToggleLink').click(function(event){
    // toggle html class
    var a = jq(event.target);
    var portlet = a.parents('.portletWrapper');
    portlet.toggleClass('closed');
    
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
  jq('#dashboard .portletWrapper dt.portletHeader .portletTopRight').before(
    '<a href="#" class="portletWideNarrowLink" title="Wide/Narrow">wide/narrow'
    + '</a>');
  jq('#dashboard .portletWrapper dt.portletHeader a.portletWideNarrowLink').click(function(event){
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

var vncStreamLoading = false;
var vncStreamDelay = 10000;

function checkVNCStream() {
  // request is already in process
  if (vncStreamLoading == true) {
    return false;
  }
  
  // mark request busy
  vncStreamLoading = true;
  
  var stream = jq('#vnc-stream');
  if (stream.length == 0) {
    vncStreamLoading = false;
    return false;
  }
  
  // find first item in the stream
  var item = jq('.vncStreamItem:first', stream);
  var data = {};
  if (item.length > 0) {
    data = {'since': item.find('.dt').text(),
      'uid': item.find('.uid').text()};
  }
  
  // do ajax request to the server to get fresh stream items
  jq.ajax({
    'type': 'GET',
    'dataType': 'html',
    'url': portal_url + '/@@vnc-stream-check',
    'data': data,
    'success': function(data){
      if (item.length > 0) {
        item.before(data);
      } else {
        jq('.vncStreamBodyItems', stream).append(data);
      }
      vncStreamLoading = false;
      setTimeout(checkVNCStream, vncStreamDelay);
    },
    'error': function(){
      vncStreamLoading = false;
      setTimeout(checkVNCStream, vncStreamDelay);
    }
  });
  
  return true;
}

function attachStreamButton() {
  // xmpp Messages onclick load stream from the server
  // do we need to load it from the server?
  jq('#site-stream-link').click(function(event){
    var stream = jq('#vnc-stream');
    if (stream.length == 0) {
      // it's already being loaded
      if (vncStreamLoading) {
        return false;
      }
      
      // load from the server
      vncStreamLoading = true;
      
      // add spinner
      if (jq('#xmpp-viewlet-container .spinner').length == 0) {
        jq('#xmpp-viewlet-container').prepend('<span class="spinner">' +
          '<img src="' + portal_url + '/dots-white.gif" /></span>');
      } else {
        jq('#xmpp-viewlet-container .spinner').show();
      }
      
      jq.ajax({
        'url': portal_url + '/@@vnc-stream',
        'dataType': 'html',
        'success': function(data, textStatus, jqXHR){
          jq('#portal-top').append(data);
          attachStreamActions();
          jq('#vnc-stream').hide().slideDown();
          // attach slim scrolling
          jq('.vncStreamBodyItems').slimScroll({'height': '293px'});
          vncStreamLoading = false;
          // remove spinner
          jq('#xmpp-viewlet-container .spinner').hide();
          setTimeout(checkVNCStream, vncStreamDelay);
        },
        'error': function() {
          alert('Sorry, something went wrong on the server. Please, try ' +
            'a bit later.');
          vncStreamLoading = false;
          // remove spinner
          jq('#xmpp-viewlet-container .spinner').hide();
          setTimeout(checkVNCStream, vncStreamDelay);
        },
        'data': {}
        });
    } else if (stream.is(':visible')) {
      stream.slideUp();
    } else {
      stream.slideDown();
    }
    return false;
  });
}

function attachStreamActions() {
  // attach stream tabs clicks
  var tabs = jq('#vnc-stream .vncStreamTabs');
  if (tabs.length > 0) {
    jq('a', tabs).click(function(event){
      var target = jq(event.target);
      var parent = target.parents('li');
      var klass = parent.attr('id').slice('stream-type-'.length-1);
    
      // change tabs class to display only filtered stream items
      target.parents('.vncStreamMsgs').removeClass().addClass("vncStreamMsgs " +
        klass);
    
      // add selected class to current tab
      parent.parent().find('li').removeClass('selected');
      parent.addClass('selected');
    
      return false;
    });
  };
  
  // TODO: make drag button increase stream area height
  // attach drag button click
  var drag = jq('#vnc-stream .dragButton');
  if (drag.length > 0) {
    drag.click(function(event){
      jq('#vnc-stream').slideUp();
      return false;
    });
  };
  
  // attach form post handler
  var form1 = jq('#vnc-stream form#stream-quick-post');
  if (form1.length > 0) {
    form1.submit(function(event){
      var field = jq('[name="stream_quick_post_message"]:input', form1),
          text = jq.trim(field.attr('value')),
          node = field.attr('data-post-node'),
          button = jq('[name="stream_quick_post_submit"]:input', form1);
      
      // skip empty input
      if (!text) {
        field.attr('value', '');
        return false;
      }
      
      // temporarily reset and disable form controls
      field.attr('disabled', 'disabled');
      field.attr('value', '');
      button.attr('disabled', 'disabled');
      
      // actually post new message to the server
      jarnxmpp.PubSub.publish(node, '',  text, null);
      
      // try to update vnc stream
      setTimeout(checkVNCStream, 2000);
      
      // activate form again
      field.attr('disabled', '');
      button.attr('disabled', '');
      
      return false;
    });
  }
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
  attachSocialBookmarksLink();
  attachStreamButton();
  attachStreamActions();
});
