var vncchat = (function (jarnxmpp, $, console) {
    var ob = xmppchat;
    ob.collections.getCollections = function(jid, start, callback) {
        if (!start) {
            start = '';
        }
        var bare_jid = Strophe.getBareJidFromJid(jid),
            iq = $iq({'type':'get'})
                    .c('list', {'xmlns': this.URI,
                                'with': bare_jid,
                                'start':start,
                                });

        xmppchat.connection.sendIQ(iq, 
                    callback,
                    function () { 
                        console.log('Error while retrieving collections'); 
                    });
    };

        ob.collections.getMessages = function (jid, start, callback) {
        var that = this;
        this.getCollections(jid, start, function (result) {
            var $collections = $(result).find('chat')
            for (i=0;i<$collections.length;i++) {
                $collection = $($collections[i]);
                jid = $collection.attr('with'),
                start = $collection.attr('start'),
                iq = $iq({'type':'get'})
                        .c('retrieve', {'start': start,
                                    'xmlns': that.URI,
                                    'with': jid
                                    });
                xmppchat.connection.sendIQ(iq, callback);
            };

        });
    };
    return ob;
})(jarnxmpp || {}, jQuery, console || {log: function(){}});

vncchat.VncChatTab = Backbone.View.extend({

    tagName:'li',
    className:'chatTab',

    template: _.template( '<a href="#<%=box_id%>" class="tabLink"><%=user_id%></a>' +
                          '<a href="javascript:void(0)" class="close-chattab-button">X</a>'),
    events: {
        'click .tabLink': 'activate',
        'click .close-chattab-button': 'closeTab',
    },
    initialize: function (body_view) {
        this.body = body_view.body
    },
    render: function () {
        $(this.el).attr('id', 'tab-' + this.body.model.get('box_id'));
        $(this.el).html(this.template(this.body.model.toJSON()));
        return this;
    },

    show: function() {
        this.$el.show();
    },

    activate: function(event) {
        event.preventDefault();
        var jid = this.body.model.get('id');
        vncchat.chatboxesview.showChat(jid);
    },

    closeTab: function() {
      $('#tab-'+this.body.model.get('box_id')).hide('fast');
      vncchat.chatboxesview.closeChat(this.body.model.get('jid'));
    },

});

vncchat.VncChatRoomTab = vncchat.VncChatTab.extend({

    template: _.template( '<a href="#<%=box_id%>" class="tabLink"><%=name%></a>' +
                          '<a href="javascript:void(0)" class="close-chattab-button">X</a>'),

    closeTab: function() {
      $('#tab-'+this.body.model.get('box_id')).remove();
      vncchat.chatboxesview.closeChat(this.body.model.get('jid'));
    },

});

vncchat.VncChatBoxView = vncchat.ChatBoxView.extend({
    tagName: 'div',
    className: 'vncChatbox',

    template: _.template(
    // TODO: custom message implementation.
    /*            '<div class="chat-head chat-head-chatbox">' +
                    '<div class="chat-title"> <%= user_id %> </div>' +
                    '<a href="javascript:void(0)" class="chatbox-button close-chatbox-button">X</a>' +
                    '<p class="user-custom-message"><p/>' +
                '</div>' + */
                '<div id="history-box">' +
                   '<span>View Erlier Messages</span>' +
                   '<ul>' +
                   '<li><a id="one-day-history" class="historyControl" href="#">1 Day</a>|</li>' +
                   '<li><a id="one-week-history" class="historyControl" href="#">1 Week</a>|</li>' +
                   '<li><a id="two-weeks-history" class="historyControl" href="#">2 Weeks</a>|</li>' +
                   '<li><a id="one-month-history" class="historyControl" href="#">1 Month</a>|</li>' +
                   '<li><a id="six-months-history" class="historyControl" href="#">6 Months</a>|</li>' +
                   '<li><a id="one-year-history" class="historyControl" href="#">1 Year</a>|</li>' +
                   '<li><a id="forever-history"  class="historyControl" href="#">Forever</a></li>' +
                '</div>' +
                '<div class="chat-content"></div>' +
                '<form class="sendXMPPMessage" action="" method="post">' +
                '<textarea ' +
                    'type="text" ' +
                    'class="chat-textarea" ' +
                    'placeholder="Personal message"/>'+
                '</form>'),

    message_template: _.template(
                        '<div class="chat-message <%=extra_classes%>">' + 
                            '<span class="chat-message-<%=sender%>"><%=username%></span>' + 
                            '<span class="messageTimeStamp"><%=time%></span>' +
                            '<p class="chat-message-content"><%=message%></p>' + 
                        '</div>'),
    events: {
        'click .close-chattab-button': 'closeChat',
        'keypress textarea.chat-textarea': 'keyPressed',
        'click .historyControl':'getHistory'
    },

    initialize: function (){
        $('body').append($(this.el).hide());
        this.tab = new vncchat.VncChatTab({ body:this });
        xmppchat.roster.on('change', function (item, changed) {
            if (_.has(changed.changes, 'presence_type')) {
                if (this.$el.is(':visible')) {
                    if (item.get('presence_type') === 'offline') {
                        this.insertStatusNotification(this.model.get('user_id'), 'has gone offline');
                    } else if (item.get('presence_type') === 'away') {
                        this.insertStatusNotification(this.model.get('user_id'), 'has gone away');
                    } else if ((item.get('presence_type') === 'busy') || (item.get('presence_type') === 'dnd')) {
                        this.insertStatusNotification(this.model.get('user_id'), 'is busy');
                    } else if (item.get('presence_type') === 'online') {
                        this.$el.find('div.chat-event').remove();
                    }
                }
            } else if (_.has(changed.changes, 'status')) {
                if (item.get('jid') ===  this.model.get('jid')) {
                    this.$el.find('p.user-custom-message').text(item.get('status'));
                }
            }
        }, this);
    },
    getHistoryDate: function(timedelta) {
        date = new Date();
        if (timedelta.hasOwnProperty('years') && timedelta.years > 0) {
            date.setYear(date.getYear() - timedelta.years)
        }
        if (timedelta.hasOwnProperty('months') && timedelta.months> 0) {
            date.setMonth(date.getMonth() - timedelta.months)
        }
        if (timedelta.hasOwnProperty('days') && timedelta.days > 0) {
            date.setDate(date.getDate() - timedelta.days)
        }
        return date.toISOString()
    },
    showMessage: function(message, start) {
        var sender,
            seneder_username;
        if (message.tagName == 'to' ){
            sender = 'me';
            sender_username = vncchat.username;
        } else if (message.tagName == 'from') {
            sender = 'them';
            sender_username = this.model.get('jid');
        } else {
            return;
        }
        time = new Date(Date.parse(start));
        time.setSeconds(time.getSeconds() +
                parseInt($(message).attr('secs')));
        $chat_content = $(this.el).find('.chat-content')
        $chat_content.append(this.message_template({
            'sender': sender,
            'time': time.toLocaleFormat('%d.%m.%Y %H:%M'),
            'message': $('body', message).text(), 
            'username': sender_username,
            'extra_classes': ''
        }));
    },
    loadHistoryMessages: function (start) {
        var that = this;
        $chat_content = $(this.el).find('.chat-content')
        $chat_content.empty();
        vncchat.collections.getMessages(jid, start, function (results) {
            $results = $(results).find('chat')
            if ($results.length > 0) {
                start = $results.attr('start');
                messages = $results.children()
                  .filter(function (index, value) {
                    return value.tagName == 'to' || value.tagName == 'from'});
                $.each(messages, function (index, message) {
                    that.showMessage(message, start);
                });
            }
        })
    },
    getHistory: function(event){
        /* TODO: We SHOULD use Result Set Management to limit the number
                 of messages returned by the server in a single stanza,
                 taking care not to request a page of messages that is so big
                 it might exceed rate limiting restrictions.*/

        // TODO: there should be better way to do this.
        event.preventDefault();
        jid = this.model.get('jid');
        if (event.target.id == 'one-day-history') {
           this.loadHistoryMessages(this.getHistoryDate({days:1}))
        }
        else if (event.target.id == 'one-week-history') {
           this.loadHistoryMessages(this.getHistoryDate({days:7}))
        }
        else if (event.target.id == 'two-weeks-history') {
           this.loadHistoryMessages(this.getHistoryDate({days:14}))
        }
        else if (event.target.id == 'one-month-history') {
           this.loadHistoryMessages(this.getHistoryDate({months:1}))
        }
        else if (event.target.id == 'six-months-history') {
           this.loadHistoryMessages(this.getHistoryDate({months:6}))
        }
        else if (event.target.id == 'one-year-history') {
           this.loadHistoryMessages(this.getHistoryDate({years:1}))
        }
        //TODO: we need to think how to properly load all history
        else if (event.target.id == 'forever-history') {
           this.loadHistoryMessages()
        }
    },
    render: function () {
        this.tab.render();
        $(this.el).attr('id', this.model.get('box_id'));
        $(this.el).html(this.template(this.model.toJSON()));
        this.insertClientStoredMessages();
        return this;
    },
    show: function() {
        $(this.el).show();
        this.tab.show();
        this.tab.$el.addClass('selected');
    },
    closeChat: function () {
        $('#'+this.model.get('box_id')).hide();
        this.removeChatFromCookie(this.model.get('id'));
        this.tab.$el.removeClass('selected');
    }
});



vncchat.VncChatBoxesView = vncchat.ChatBoxesView.extend({
    el: '#chat-block',

    initialize: function () {
        this.options.model.on("add", function (item) {
            this.showChat(item.get('id'));
        }, this);

        this.tabs = [];
        this.views = {};
        this.restoreOpenChats();
    },

    renderChat: function (jid) {
        var box, view, tab;
        if (this.isChatRoom(jid)) {
            box = new vncchat.ChatRoom(jid);
            view = new vncchat.VncChatRoomView({ model: box });
        } else {
            box = new vncchat.ChatBox({'id': jid, 'jid': jid});
            view = new vncchat.VncChatBoxView({ model:box });
        }
        this.views[jid] = view.render();
        view.tab.$el.appendTo('#chat-tabs');
        view.$el.appendTo(this.$el);
        this.options.model.add(box);
        this.tabs.push(jid);
        return view;
    },

    showChat: function (jid) {
        var chat = this.views[jid];
        if (chat.isVisible()) {
            chat.focus();
            chat.tab.$el.addClass('selected');
        }
        else {
            chat.show();
            chat.addChatToCookie();
        }
        $.each(this.views, function(name, view) {
            if (name != jid) {
                view.closeChat();
            }
        });
        this.tabs.push(jid);
        return chat;
    },

    closeChat: function (jid) {
        var view = this.views[jid];
        if (view) {
            if (this.isChatRoom(jid)) {
                view.closeChatRoom();
            } else {
                view.closeChat();
            }
            this.tabs = $(this.tabs).filter( function() {
                return this != jid
            });
        }
        var tab = $.makeArray(this.tabs).pop();
        if (tab) { this.showChat(tab); }
    },
});

vncchat.VncChatRoomView = vncchat.VncChatBoxView.extend({
    length: 300,
    tagName: 'div',
    className: 'chatroom',

    template: _.template(
        //TODO: chat room topic
        /*    '<div class="chat-head chat-head-chatroom">' +
                '<div class="chat-title"> <%= name %> </div>' +
                '<a href="javascript:void(0)" class="chatbox-button close-chatbox-button">X</a>' +
                '<p class="chatroom-topic"><p/>' +
            '</div>' +*/
            '<div class="roomParticipants">' +
                '<span>Participants:</span>' +
                '<ul class="participant-list">' +
                  '<li>Add ...</li>' +
                '</ul>' +
            '</div>' +
            '<div id="history-box">' +
               '<span>View Erlier Messages</span>' +
               '<ul>' +
               '<li><a id="one-day-history" class="historyControl" href="#">1 Day</a>|</li>' +
               '<li><a id="one-week-history" class="historyControl" href="#">1 Week</a>|</li>' +
               '<li><a id="two-weeks-history" class="historyControl" href="#">2 Weeks</a>|</li>' +
               '<li><a id="one-month-history" class="historyControl" href="#">1 Month</a>|</li>' +
               '<li><a id="six-months-history" class="historyControl" href="#">6 Months</a>|</li>' +
               '<li><a id="one-year-history" class="historyControl" href="#">1 Year</a>|</li>' +
               '<li><a id="forever-history"  class="historyControl" href="#">Forever</a></li>' +
            '</div>' +
            '<div>' +
            '<div class="chat-area">' +
                '<div class="chat-content">' +
                    '<div class="room-name"></div>' +
                    '<div class="room-topic"></div>' +
                '</div>' +
                '<form class="sendXMPPMessage" action="" method="post">' +
                    '<textarea ' +
                        'type="text" ' +
                        'class="chat-textarea" ' +
                        'placeholder="Message"/>' +
                '</form>' +
            '</div>' +
            '</div>'),

    events: {
        'click .close-chattab-button': 'closeChatRoom',
        'keypress textarea.chat-textarea': 'keyPressed',
        'click .historyControl':'getHistory',
        'click .addParticipants':'addParticipants'
    },

    initialize: function () {
        this.tab = new vncchat.VncChatRoomTab({ body:this });
        xmppchat.connection.muc.join(
                        this.model.get('jid'), 
                        this.model.get('nick'), 
                        $.proxy(this.onMessage, this), 
                        $.proxy(this.onPresence, this), 
                        $.proxy(this.onRoster, this));
    },

    closeChatRoom: function () {
        this.closeChat();
        xmppchat.connection.muc.leave(
                        this.model.get('jid'), 
                        this.model.get('nick'), 
                        this.onLeave,
                        undefined);
        delete xmppchat.chatboxesview.views[this.model.get('jid')];
        xmppchat.chatboxesview.model.remove(this.model.get('jid'));
        this.remove();
        vncchat.controlbox_view.roomspanel.updateRoomsList();
    },

    keyPressed: function (ev) {
        var $textarea = $(ev.target),
            message,
            notify,
            composing,
            that = this;

        if(ev.keyCode == 13) {
            message = $textarea.val();
            message = message.replace(/^\s+|\s+jQuery/g,"");
            $textarea.val('').focus();
            if (message !== '') {
                this.sendGroupMessage(message);
            }
        } 
    },

    sendGroupMessage: function (body) {
        var match = body.replace(/^\s*/, "").match(/^\/(.*?)(?: (.*))?$/);
        var args = null;
        if (match) {
            if (match[1] === "msg") {
                // TODO: Private messages
            } else if (match[1] === "topic") {
                xmppchat.connection.muc.setTopic(this.model.get('jid'), match[2]);

            } else if (match[1] === "kick") {
                xmppchat.connection.muc.kick(this.model.get('jid'), match[2]);

            } else if (match[1] === "ban") {
                xmppchat.connection.muc.ban(this.model.get('jid'), match[2]);

            } else if (match[1] === "op") {
                xmppchat.connection.muc.op(this.model.get('jid'), match[2]);

            } else if (match[1] === "deop") {
                xmppchat.connection.muc.deop(this.model.get('jid'), match[2]);
            } else {
                this.last_msgid = xmppchat.connection.muc.groupchat(this.model.get('jid'), body);
            }
        } else {
            this.last_msgid = xmppchat.connection.muc.groupchat(this.model.get('jid'), body);
        }
    },

    onLeave: function () {
        var controlboxview = xmppchat.chatboxesview.views['online-users-container'];
        if (controlboxview) {
            controlboxview.roomspanel.trigger('update-rooms-list');
        }
    },

    onPresence: function (presence, room) {
        var nick = room.nick,
            from = $(presence).attr('from');
        if ($(presence).attr('type') !== 'error') {
            // check for status 110 to see if it's our own presence
            if ($(presence).find("status[code='110']").length > 0) {
                // check if server changed our nick
                if ($(presence).find("status[code='210']").length > 0) {
                    this.model.set({'nick': Strophe.getResourceFromJid(from)});
                }
            }
        }
        return true;
    },

    onMessage: function (message) {
        var body = $(message).children('body').text(),
            jid = $(message).attr('from'),
            composing = $(message).find('composing'),
            $chat_content = $(this.el).find('.chat-content'),
            sender = Strophe.getResourceFromJid(jid),
            subject = $(message).children('subject').text();

        if (subject) {
            this.$el.find('.chatroom-topic').text(subject);
        }
        if (!body) {
            if (composing.length > 0) {
                this.insertStatusNotification(sender, 'is typing');
                return true;
            }
        } else {
            if (sender === this.model.get('nick')) {
                this.appendMessage(body);
            } else {
                $chat_content.find('div.chat-event').remove();

                match = body.match(/^\/(.*?)(?: (.*))?$/);
                if ((match) && (match[1] === 'me')) {
                    body = body.replace(/^\/me/, '*'+sender);
                    $chat_content.append(
                            this.action_template({
                                'sender': 'room', 
                                'time': (new Date()).toLocaleTimeString().substring(0,5),
                                'message': body, 
                                'username': sender,
                                'extra_classes': ($(message).find('delay').length > 0) && 'delayed' || ''
                            }));
                } else {
                    $chat_content.append(
                            this.message_template({
                                'sender': 'room', 
                                'time': (new Date()).toLocaleTimeString().substring(0,5),
                                'message': body,
                                'username': sender,
                                'extra_classes': ($(message).find('delay').length > 0) && 'delayed' || ''
                            }));
                }
                $chat_content.scrollTop($chat_content[0].scrollHeight);
            }
        }
        return true;
    },

    onRoster: function (roster, room) {
        var controlboxview = xmppchat.chatboxesview.views['online-users-container'];
        if (controlboxview) {
            controlboxview.roomspanel.trigger('update-rooms-list');
        }
        $participants = this.$el.find('.participant-list')
        $participants.empty();
        for (var i=0; i<_.size(roster); i++) {
            $participants.append('<li>' + _.keys(roster)[i] +
                                  '<a href="javascript:void(0)">X</a>' +
                                 '</li>');
        }
        $participants
            .append('<li>' +
                      '<a href="javascript:void(0)" class="addParticipants">' +
                        'Add ...' +
                      '</a>' +
                    '</li>');
        return true;
    },

    show: function() {
        $(this.el).show();
        this.tab.show();
        this.tab.$el.addClass('selected');
    },

    render: function () {
        this.tab.render();
        $(this.el).attr('id', this.model.get('box_id'));
        $(this.el).html(this.template(this.model.toJSON()));
        return this;
    },

    showMessage: function(message, start) {
        var sender,
            seneder_username;
            $message = $(message);
            from = $message.attr('name');
            time = new Date(Date.parse(start));
        time.setSeconds(time.getSeconds() + parseInt($(message).attr('secs')));
        $chat_content = $(this.el).find('.chat-content')
        $chat_content.append(this.message_template({
            'sender': (from == vncchat.username) ? 'me':'them',
            'time': time.toLocaleFormat('%d.%m.%Y %H:%M'),
            'message': $('body', message).text(),
            'username':vncchat.username,
            'extra_classes': ''
        }));
    },

    recipients_template: _.template('<input type="checkbox" name="<%=node%>" ' +
                                   'value="<%=jid%>" /><%=node%></br>'),

    addParticipants: function (event) {
        event.preventDefault();
        var participants,
            $participants =this.$el.find('.participant-list li')
                .clone().children().remove().end();
            recipients = [];
        participants = {};
        $participants.each(function() {
            name = $(this).text();
            if (name) { participants[name] = 1 };
        });
        roster = vncchat.roster.sort().models;
        for (var i=0;i<roster.length;i++) {
            jid = roster[i].id
            node = Strophe.getNodeFromJid(jid);
            if  (node in participants) { continue; };
            recipients.push({'name':node, 'jid':jid});
        };
        $request_dialog = $('<html>' +
                              '<body>' +
                                '<form action="">' +
                                  '<p>Nobody to invite</p>' +
                                '</form>' +
                              '</body>' +
                            '</html>');
        if (recipients.length == 0) {
            $request_dialog.dialog();
        } else {
            $request_dialog.empty();
            var that = this;
            $.each(recipients, function (index, recipient) {
               $request_dialog
                .append(that.recipients_template('{"node":"'+recipient.name+'",' +
                                                '"jid":"'+recipient.jid+'"}'));
            });
            var that = this;
            $request_dialog.dialog({
                resizable: false,
                buttons : {
                    'join' : {
                        'text':'Join',
                        'click': function() {
                            selected = $('input', this)
                                .filter(function (){
                                    return $(this).attr('checked');
                                });
                            if (selected.length == 0) { 
                                alert('Please select someone');
                            } else {
                                selected.each(function(index, input) {
                                    vncchat.connection.muc
                                    .invite(that.model.get('jid'),
                                                    $(input).attr('value'));
                                });
                                $(this).dialog('close');
                            }
                        },
                    },
                }
            });

        }
    },

});

vncchat.VncRoomsPanel = vncchat.RoomsPanel.extend({

    createChatRoom: function (ev) {
        vncchat.RoomsPanel.prototype.createChatRoom(ev);
        this.updateRoomsList();
    },

    invitationReceived: function (invitation) {
        var room = $(invitation).attr('from');
            from = $(invitation).find('invite').attr('from');
            that = this;
        $("<span></span>").dialog({
            title: from + ' invites you to join ' + room + ' room.',
            dialogClass: 'roomInvitationDialog',
            resizable: false,
            width: 200,
            position: {
                my: 'center',
                at: 'center',
                of: '#online-users-container'
                },
            modal: true,
            buttons: {
                "Join": function() {
                     vncchat.chatboxesview.openChat(room);
                     that.updateRoomsList();
                    $(this).dialog( "close" );
                },
                "Cancel": function() {
                    $(this).dialog( "close" );
                }
            }
        });
    },
});

vncchat.VncControlBoxView = vncchat.ControlBoxView.extend({

    initialize: function () {
        var userspanel; 
        $('ul.tabs').tabs('div.panes > div');
        this.contactspanel = new xmppchat.ContactsPanel();
        this.roomspanel = new xmppchat.VncRoomsPanel();
        this.settingspanel = new xmppchat.SettingsPanel();
    },

});
