function attachPortletUpDowns() {
  // add up/down links to portlet headers, which will expand/contract
  // portlet bodies
  jq('.portlet dt.portletHeader .portletTopRight').before(
    '<a href="#" class="portletToggleLink" onclick="jq(this).parents(\'.portlet\').toggleClass(\'closed\');return false;" title="Toggle Portlet">toggle</a>');
}

function attachHeaderViewletCloseOpen() {
  jq('.headerTimeViewlet a.closeLink').click(function(event){
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
  jq('.headerTimeViewletShort a.openLink').click(function(event){
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
  attachPortletUpDowns();
});
