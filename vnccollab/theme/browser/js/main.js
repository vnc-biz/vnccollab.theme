// TODO: add state html classes to portlet wrapper

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

jq(function() {
  attachHeaderViewletCloseOpen();
  attachPortletButtons();
});
