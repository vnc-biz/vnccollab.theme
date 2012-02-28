function attachPortletButtons() {
  // add up/down and left/right links to portlet headers,
  // which will expand/contract and make portlets wide
  jq('.portlet dt.portletHeader .portletTopRight').before(
    '<a href="#" class="portletToggleLink" onclick="jq(this).parents(\'.portlet\').toggleClass(\'closed\');return false;" title="Toggle Portlet">toggle</a>');
  jq('.portlet dt.portletHeader .portletTopRight').before(
    '<a href="#" class="portletWideNarrowLink" onclick="jq(this).parents(\'.portlet\').toggleClass(\'wide\');return false;" title="Wide/Narrow">wide/narrow</a>');
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
