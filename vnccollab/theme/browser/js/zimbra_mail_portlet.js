function zimbra_refreshEmails(event, folder) {
  var target = jq(event.target);
  var portlet = target.parents('.portletWrapper');
  var container = target.parents('.portletBody');
  var body = jq('.emailsView', container);
  
  function success(data, textStatus, jqXHR) {
    // update main emails listing
    body.html(data['emails']);
    // select first email
    jq(jq('.emailItem', container)[0]).addClass('selected');
    // update folder label unread messages counter
    jq('.navBarEmails .label .count', container).html(
      jq('.emailItem.unread', container).length);
    // remove progress state
    container.removeClass('inprogress');
  }
  
  // load folder emails from the server
  container.addClass('inprogress');
  jq.post(portal_url + '/@@zimbra-mail-portlet-view',
    {'action': 'emails',
     'folder': folder,
     'portlethash': portlet.attr('id').slice('portletwrapper-'.length)},
    success, "json");

}

jq(function(event) {
// load inbox emails on page load
jq('.portletZimbraMail .refreshButton').click();
});
