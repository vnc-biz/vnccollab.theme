function zimbra_refreshEmails(event, folder) {
  var target = jq(event.target);
  var portlet = target.parents('.portletWrapper');
  var container = target.parents('.portletBody');
  var body = jq('.emailsView', container);
  
  function success(data, textStatus, jqXHR) {
    // TODO: update inbox number of unread messages label
    body.html(data['emails']);
    jq(jq('.emailItem', container)[0]).addClass('selected');
    container.removeClass('inprogress');
  }
  
  // load folder emails from the server
  // TODO: add loading state to container
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
