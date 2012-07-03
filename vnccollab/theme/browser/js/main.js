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
  jq('#dashboard-portlets1 .portletBody:not(.noSlimScroll)').slimScroll({
    'height': '300px'
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
        $content.find('.portletBody').slimScroll({'height': '300px'});
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

function initNewTicketForm() {
  var $create = jq('#form-buttons-create');
  var $typeOfTicket = jq('#form-widgets-type_of_ticket');

  // Inputs to keep sinchronized
  var $subject_ = jq('#form-widgets-subject_');
  var $startDateDay = jq('#form-widgets-startDate-day');
  var $startDateMonth = jq('#form-widgets-startDate-month');
  var $startDateYear = jq('#form-widgets-startDate-year');
  var $endDateDay = jq('#form-widgets-endDate-day');
  var $endDateMonth = jq('#form-widgets-endDate-month');
  var $endDateYear = jq('#form-widgets-endDate-year');
  var $content = jq('#form-widgets-content');
  var $zimbra = [$subject_, $startDateDay, $startDateMonth, $startDateYear, 
                 $endDateDay, $endDateMonth, $endDateYear, $content]

  var $subject = jq('#form-widgets-subject');
  var $start_dateDay = jq('#form-widgets-start_date-day');
  var $start_dateMonth = jq('#form-widgets-start_date-month');
  var $start_dateYear = jq('#form-widgets-start_date-year');
  var $due_dateDay = jq('#form-widgets-due_date-day');
  var $due_dateMonth = jq('#form-widgets-due_date-month');
  var $due_dateYear = jq('#form-widgets-due_date-year');
  var $description = jq('#form-widgets-description');
  var $redmine = [$subject, $start_dateDay, $start_dateMonth, $start_dateYear, 
                  $due_dateDay, $due_dateMonth, $due_dateYear, $description]


  function showNewTaskWidgets(classToShow) {
    // Shows a subform and hides the other one
    var $form = jq('#new_ticket_form');
    var $zimbraWidgets = $form.find('div:has(.zimbra-widget)');
    var $redmineWidgets = $form.find('div:has(.redmine-widget)');

    console.log('showNewTaskWidgets init');
    console.log(jQuery.fn.jquery);
    console.log(classToShow);
    console.log($zimbraWidgets);
    console.log($redmineWidgets);
    if (classToShow === 'zimbra') {
        $zimbraWidgets.show();
        $redmineWidgets.hide();
    } else {
        $zimbraWidgets.hide();
        $redmineWidgets.show();
    }
    console.log('showNewTaskWidgets end');
  }

  function onTypeOfTicketChange() {
    // Event to show the right subform
    showNewTaskWidgets($typeOfTicket.val());
  }

  function genericOnChange($from, $to) {
      return function() {
        if ($to.val() !== $from.val()) {
              $to.val($from.val());
        }
      }
  }

  function onSubjectChange() {
    // Activate or deactivate "Create" button
    if (($subject.val()==='') && ($subject_.val()==='')) {
      $create.enable(false);    
    } else {
      $create.enable(true);
    }
  }

  function sinchronizeOnChange() {
      for (var i = 0; i < $zimbra.length; i++) {
          $zimbra[i].change(genericOnChange($zimbra[i], $redmine[i]));
          $redmine[i].change(genericOnChange($redmine[i], $zimbra[i]));
      }
      $subject.bind('hastext', onSubjectChange);
      $subject_.bind('hastext', onSubjectChange);
      $subject.bind('notext', onSubjectChange);
      $subject_.bind('notext', onSubjectChange);
  }

  sinchronizeOnChange();
  $typeOfTicket.change(onTypeOfTicketChange);
  onTypeOfTicketChange();
  onSubjectChange();
}

function attachNewTicketAction() {
  console.log('attaching');
  jq('#document-action-new_ticket a').prepOverlay({
    'subtype': 'ajax',
    'filter': common_content_filter,
    'formselector': 'form#new_ticket_form',
    'noform': function(el) {return noformerrorshow(el, 'reload');},
    'afterpost': function(obj, paren) {console.log(obj.html()); console.log(paren);}, //initNewTicketForm,
    'config' : {
        'onBeforeLoad' : function(e) {
            initNewTicketForm();
        }
    }
  }); 
  console.log('attached');
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
});
