var vncchat = (function (xmppchat, $, console) {
    var ob = xmppchat;
    ob.get_user_info  = function (user_id, callback) {
        info = store.get(user_id);
        if (info) {
            callback(info);
        } else {
            ob.Presence.getUserInfo(user_id, function (data) {
                if (data) {
                    store.set(user_id, data);
                    callback(data);
                } else {
                    callback(data);
                }
            })
        }
    };
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

vncchat.VncChatBox = vncchat.ChatBox.extend({

    initialize: function () {
        var jid = Strophe.getNodeFromJid(this.get('jid'));
        this.set({
            'user_id' : jid,
            'box_id' : this.hash(this.get('jid')),
            'fullname': jid,
            'portrait': ''
        });
        var that = this;
        vncchat.get_user_info(Strophe.unescapeNode(jid), function(data) {
            if (data) {
                that.set({
                    'fullname': data.fullname,
                    'portrait': data.portrait_url
                });
            };
        });
    }

});

vncchat.VncChatTab = Backbone.View.extend({

    tagName:'li',
    className:'chatTab',

    template: _.template( '<a href="#<%=box_id%>" class="tabLink"><%=fullname%></a>' +
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
        vncchat.roster.trigger('show-contact',
                               this.body.model.get('jid'));
    },

    activate: function(event) {
        event.preventDefault();
        var jid = this.body.model.get('id');
        vncchat.chatboxesview.showChat(jid);
        this.$el.removeClass('newMessage');
    },

    closeTab: function() {
      $('#tab-'+this.body.model.get('box_id')).hide();
      vncchat.chatboxesview.closeChat(this.body.model.get('jid'));
      this.body.removeChatFromCookie(this.body.model.get('id'));
      vncchat.roster.trigger('hide-contact', this.body.model.get('jid'));
    },

});

vncchat.VncChatRoomTab = vncchat.VncChatTab.extend({

    template: _.template( '<a href="#<%=box_id%>" class="tabLink"><%=name%></a>' +
                          '<a href="javascript:void(0)" class="close-chattab-button">X</a>'),

    show: function() {
        this.$el.show();
    },

    closeTab: function() {
      $('#tab-'+this.body.model.get('box_id')).hide();
      vncchat.chatboxesview.closeChat(this.body.model.get('jid'));
      this.body.removeChatFromCookie(this.body.model.get('id'));
    },
});

vncchat.VncChatBoxView = vncchat.ChatBoxView.extend({
    tagName: 'div',
    className: 'vncChatbox chatbody',

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
                this.sendMessage(message);
            }
            $(this.el).data('composing', false);
            return false;
        } else {
            composing = $(this.el).data('composing');
            if (!composing) {
                notify = $msg({'to':this.model.get('jid'), 'type': 'chat'})
                                .c('composing', {'xmlns':'http://jabber.org/protocol/chatstates'});
                vncchat.connection.send(notify);
                $(this.el).data('composing', true);
            }
        }
    },

    template: _.template(
    // TODO: custom message implementation.
    /*            '<div class="chat-head chat-head-chatbox">' +
                    '<div class="chat-title"> <%= user_id %> </div>' +
                    '<a href="javascript:void(0)" class="chatbox-button close-chatbox-button">X</a>' +
                    '<p class="user-custom-message"><p/>' +
                '</div>' + */
                '<div class="chat-content">' +
                '<div class="history-box">' +
                   '<span class="history-box-header">View Earlier Messages</span>' +
                   '<ul>' +
                   '<li><a class="historyControl one-day-history" href="#">1 Day</a></li>' +
                   '<li><a class="historyControl one-week-history" href="#">1 Week</a></li>' +
                   '<li><a class="historyControl two-weeks-history" href="#">2 Weeks</a></li>' +
                   '<li><a class="historyControl one-month-history" href="#">1 Month</a></li>' +
                   '<li><a class="historyControl six-months-history" href="#">6 Months</a></li>' +
                   '<li><a class="historyControl one-year-history" href="#">1 Year</a></li>' +
                   '<li><a class="historyControl all-history" href="#">All</a></li>' +
                '</div>' +
                '</div>' +
                '<form class="sendXMPPMessage" action="" method="post">' +
                '<textarea ' +
                    'type="text" ' +
                    'class="chat-textarea" ' +
                    'placeholder="Enter your message here..."/>'+
                '</form>'),

    message_template: _.template(
                        '<div class="chat-message <%=extra_classes%>">' + 
                          '<div class="chat-message-byline chat-message-<%=sender%>">' +
                            '<span class="messageTimeStamp"><%=time%></span>' +
                            '<span class="chat-message-author"><%=username%></span>' + 
                          '</div>' +
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
        vncchat.roster.on('change', function (item, changed) {
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
    formatTimeStamp: function(date) {
        if (date.toLocaleFormat) {
            return date.toLocaleFormat('%d.%m.%Y %H:%M')
        } else {
            var month = date.getMonth() + 1;
            var minutes = date.getMinutes();
            month = month.toString().length == 1 ? '0'+ month: month
            minutes = minutes.toString().length == 1 ? '0' + minutes: minutes
            return date.getDate() + '.' +
                   month + '.' +
                   date.getFullYear() +' ' +
                   date.getHours() + ':' +
                   minutes;
        }

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
            sender_username = vncchat.fullname;
        } else if (message.tagName == 'from') {
            sender = 'them';
            sender_username = this.model.get('fullname');
        } else {
            return;
        }
        time = new Date(Date.parse(start));
        time.setSeconds(time.getSeconds() +
                parseInt($(message).attr('secs')));
        $chat_content = $(this.el).find('.chat-content')
        body = $('body', message).text();
        match = body.match(/^\/(.*?)(?: (.*))?$/);
        if ((match) && (match[1] === 'me')) {
            body = body.replace(/^\/me/, '*'+ sender_username);
            $chat_content.append(this.action_template({
                                'sender': 'me', 
                                'time': this.formatTimeStamp(time),
                                'message': body, 
                                'username': sender_username,
                                'extra_classes': ''
                            }));
        } else {
            $chat_content.append(this.message_template({
                'sender': sender,
                'time': this.formatTimeStamp(time),
                'message': body,
                'username': sender_username,
                'extra_classes': ''
            }));
        }
        $chat_content.scrollTop($chat_content[0].scrollHeight);
    },
    loadHistoryMessages: function (start) {
        var that = this;
        $chat_content = $(this.el).find('.chat-content')
        $chat_content.find('div.chat-message').remove();
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
        var control = $(event.target);
        if (control.is('.one-day-history')) {
           this.loadHistoryMessages(this.getHistoryDate({days:1}))
        }
        else if (control.is('.one-week-history')) {
           this.loadHistoryMessages(this.getHistoryDate({days:7}))
        }
        else if (control.is('.two-weeks-history')) {
           this.loadHistoryMessages(this.getHistoryDate({days:14}))
        }
        else if (control.is('.one-month-history')) {
           this.loadHistoryMessages(this.getHistoryDate({months:1}))
        }
        else if (control.is('.six-months-history')) {
           this.loadHistoryMessages(this.getHistoryDate({months:6}))
        }
        else if (control.is('.one-year-history')) {
           this.loadHistoryMessages(this.getHistoryDate({years:1}))
        }
        //TODO: we need to think how to properly load all history
        else if (control.is('.all-history')) {
           this.loadHistoryMessages()
        }
        // TODO: remove clicked history link after messages load
        // remove currently clicked link + all previous links,
        // if All link was clicked: remove whole history controls area
        if (control.is('.all-history')) {
          control.parents('.history-box').remove();
        } else {
          var klass = control.attr('class');
          control.parent().parent().find('.historyControl').each(
            function(idx, elem){
              var link = $(elem);
              link.parent().remove();
              // stop if this is current element
              if (link.attr('class') == klass) {
                return false;
              }
            }
          );
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
        this.tab.$el.removeClass('selected');
    },

    appendMessage: function (message) {
        var time, 
            now = new Date(),
            minutes = now.getMinutes().toString(),
            list,
            $chat_content,
            match;
        message = message.replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/\"/g,"&quot;").replace(/^\s*/, "");
        list = message.match(/\b(http:\/\/www\.\S+\.\w+|www\.\S+\.\w+|http:\/\/(?=[^w]){3}\S+[\.:]\S+)[^ ]+\b/g);
        if (list) {
            for (i = 0; i < list.length; i++) {
                message = message.replace(list[i], "<a target='_blank' href='" + escape( list[i] ) + "'>"+ list[i] + "</a>" );
            }
        }

        if (minutes.length==1) {minutes = '0'+minutes;}
        time = this.formatTimeStamp(now),
        $chat_content = $(this.el).find('.chat-content');
        $chat_content.find('div.chat-event').remove();

        match = message.match(/^\/(.*?)(?: (.*))?$/);
        if ((match) && (match[1] === 'me')) {
            message = message.replace(/^\/me/, '*'+vncchat.fullname);
            $chat_content.append(this.action_template({
                                'sender': 'me', 
                                'time': time, 
                                'message': message, 
                                'username': vncchat.fullname,
                                'extra_classes': ''
                            }));
        } else {
            $chat_content.append(this.message_template({
                                'sender': 'me', 
                                'time': time, 
                                'message': message, 
                                'username': 'me',
                                'extra_classes': ''
                            }));
        }
        $chat_content.scrollTop($chat_content[0].scrollHeight);
    },

    showReceivedMessage: function (from_jid, from_name, message) {
        var body = $(message).children('body').text(),
            $chat_content = $(this.el).find('.chat-content'),
            composing = $(message).find('composing');

        if (vncchat.xmppstatus.getOwnStatus() === 'offline') {
            // only update the UI if the user is not offline
            return;
        }
        if (!body) {
            if (composing.length > 0) {
                this.insertStatusNotification(from_name, 'is typing');
                return;
            }
        } else {
            // TODO: ClientStorage 
            vncchat.messages.ClientStorage.addMessage(from_jid, body, 'from');
            $chat_content.find('div.chat-event').remove();

            match = body.match(/^\/(.*?)(?: (.*))?$/);
            if ((match) && (match[1] === 'me')) {
                $chat_content.append(this.action_template({
                            'sender': 'them', 
                            'time': this.formatTimeStamp(new Date()),
                            'message': body.replace(/^\/me/, '*'+from_name).replace(/<br \/>/g, ""),
                            'username': vncchat.fullname,
                            'extra_classes': ($(message).find('delay').length > 0) && 'delayed' || ''
                        }));
            } else {
                $chat_content.append(
                        this.message_template({
                            'sender': 'them', 
                            'time': this.formatTimeStamp(new Date()),
                            'message': body.replace(/<br \/>/g, ""),
                            'username': from_name,
                            'extra_classes': ($(message).find('delay').length > 0) && 'delayed' || ''
                        }));
            }
            $chat_content.scrollTop($chat_content[0].scrollHeight);
        }
    },
    messageReceived: function (message) {
        /* XXX: event.mtype should be 'xhtml' for XHTML-IM messages, 
            but I only seem to get 'text'. 

            XXX: Some messages might be delayed, we must get the time from the event.
        */
        var jid = $(message).attr('from'),
            user_id = Strophe.unescapeNode(Strophe.getNodeFromJid(jid));
            fullname = user_id;

        var that = this;
        vncchat.get_user_info(user_id, function (data) {
            if (data.fullname) {
                fullname = data.fullname;
            }
            that.showReceivedMessage(jid, fullname, message);
        });

    },

    insertClientStoredMessages: function () {
        vncchat.messages.getMessages(this.model.get('jid'), $.proxy(function (msgs) {
            var $content = this.$el.find('.chat-content');
            for (var i=0; i<_.size(msgs); i++) {
                var msg = msgs[i], 
                    msg_array = msg.split(' ', 2),
                    date = msg_array[0],
                    match;
                msg = String(msg).replace(/(.*?\s.*?\s)/, '');
                match = msg.match(/^\/(.*?)(?: (.*))?$/);
                if (msg_array[1] == 'to') {
                    if ((match) && (match[1] === 'me')) {
                        $content.append(
                            this.action_template({
                                'sender': 'me', 
                                'time': this.formatTimeStamp(new Date(Date.parse(date))),
                                'message': msg.replace(/^\/me/, '*'+vncchat.fullname),
                                'username': vncchat.username,
                                'extra_classes': 'delayed'
                        }));
                    } else {
                        $content.append(
                            this.message_template({
                                'sender': 'me', 
                                'time': this.formatTimeStamp(new Date(Date.parse(date))),
                                'message': msg, 
                                'username': 'me',
                                'extra_classes': 'delayed'
                        }));
                    }
                } else {
                    if ((match) && (match[1] === 'me')) {
                        $content.append(
                            this.action_template({
                                'sender': 'them', 
                                'time': this.formatTimeStamp(new Date(Date.parse(date))),
                                'message': msg.replace(/^\/me/, '*'+this.model.get('user_id')),
                                'username': this.model.get('fullname'),
                                'extra_classes': 'delayed'
                            }));
                    } else {
                        $content.append(
                            this.message_template({
                                'sender': 'them', 
                                'time': this.formatTimeStamp(new Date(Date.parse(date))),
                                'message': msg,
                                'username': this.model.get('fullname'),
                                'extra_classes': 'delayed'
                            }));
                    }
                }
            }
        }, this));
    },

    addChatToCookie: function () {
        var cookie = jQuery.cookie('chats-open-'+vncchat.username),
            jid = this.model.get('jid'),
            new_cookie,
            open_chats = [];

        if (cookie) {
            open_chats = cookie.split('|');
        };

        for (var i=0;i<open_chats.length;i++) {
            open_chats[i] = open_chats[i].split(':')[0]
        };

        if ($.inArray(jid, open_chats) == -1) {
            // Update the cookie if this new chat is not yet in it.
            open_chats.push(jid + ':current');
        } else {
            for (var i=0;i<open_chats.length;i++) {
                if (open_chats[i] == jid) {
                    open_chats[i] = open_chats[i] + ":current"
                }
            };
        };
        new_cookie = open_chats.join('|');
        jQuery.cookie('chats-open-'+vncchat.username, new_cookie, {path: '/'});
        console.log('updated cookie = ' + new_cookie + '\n');
    },

    removeChatFromCookie: function () {
        var cookie = jQuery.cookie('chats-open-'+vncchat.username),
            open_chats = [],
            new_chats = [];

        if (cookie) {
            open_chats = cookie.split('|');
        }
        for (var i=0; i < open_chats.length; i++) {
            if (open_chats[i].split(':')[0] != this.model.get('jid')) {
                new_chats.push(open_chats[i]);
            }
        }
        if (new_chats.length) {
            jQuery.cookie('chats-open-'+vncchat.username, new_chats.join('|'), {path: '/'});
        }
        else {
            jQuery.cookie('chats-open-'+vncchat.username, null, {path: '/'});
        }
    },
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
            box = new vncchat.VncChatBox({'id': jid, 'jid': jid});
            view = new vncchat.VncChatBoxView({ model:box });
        }
        this.views[jid] = view.render();
        view.tab.$el.appendTo('#chat-tabs');
        view.$el.appendTo(this.$el);
        this.options.model.add(box);
        this.tabs.push(jid);
        view.addChatToCookie();
        if (!this.isChatRoom(jid)) {
            vncchat.roster.trigger('show-contact', jid);
        }
        return view;
    },

    restoreOpenChats: function () {
        var cookie = jQuery.cookie('chats-open-'+vncchat.username),
            open_chats = [];

        jQuery.cookie('chats-open-'+vncchat.username, null, {path: '/'});
        if (cookie) {
            open_chats = cookie.split('|');
            var current_chat;
            for (var i=0; i<open_chats.length; i++) {
                var current = '',
                    chat = open_chats[i];
                if (open_chats[i].search(':') !== -1) {
                    if (chat.split(':')[1]) {
                        current_chat = chat.split(':')[0]
                        chat = current_chat;
                    }
                }
                this.openChat(chat);
            }
            if (current_chat) {
                this.showChat(current_chat)
            }
        }
    },

    showChat: function (jid) {
        var chat = this.views[jid];
        if (chat.isVisible()) {
            // chat.focus();
            // chat.tab.$el.addClass('selected');
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
        if (!this.isChatRoom(jid)) {
            vncchat.roster.trigger('show-contact', jid);
        }
        return chat;
    },

    closeChat: function (jid) {
        var view = this.views[jid];
        if (view) {
            view.closeChat();
            this.tabs = $(this.tabs).filter( function() {
                return this != jid
            });
        }
        var tab = $.makeArray(this.tabs).pop();
        if (tab) { this.showChat(tab); }
    },

    messageReceived: function (message) {
        var jid = $(message).attr('from'),
            bare_jid = Strophe.getBareJidFromJid(jid),
            resource = Strophe.getResourceFromJid(jid),
            view = this.views[bare_jid];

        if (!view) {
            view = this.renderChat(bare_jid);
        } else {
            if ($.makeArray(this.tabs).length == 0) {
                this.showChat(bare_jid);
            } else {
                if (!view.isVisible()) {
                    view.tab.show();
                    view.tab.$el.addClass('newMessage');
                }
            };

        }
        if (!this.isChatRoom(jid)) {
            view.messageReceived(message);
            // XXX: Is this the right place for this? Perhaps an event?
            vncchat.roster.addResource(bare_jid, resource);
        } else {
            view.onMessage(message);
        };

    },
});

vncchat.VncRosterItem = Backbone.Model.extend({

    initialize: function (jid, subscription, ask) {
        // FIXME: the fullname is set to user_id for now...
        var user_id = Strophe.unescapeNode(Strophe.getNodeFromJid(jid))
        this.set({
            'id': jid,
            'jid': jid,
            'ask': ask,
            'bare_jid': Strophe.getBareJidFromJid(jid),
            'user_id': user_id,
            'subscription': subscription,
            'fullname': user_id,
            'resources': [],
            'presence_type': 'offline',
            'status': 'offline',
            'portrait':'',
        }, {'silent': true});

        var that = this;
        vncchat.get_user_info(user_id, function(data) {
            if (data) {
                that.set({
                    'fullname': data.fullname,
                    'portrait': data.portrait_url
                });
            };
        });

    }
});

vncchat.VncChatRoomView = vncchat.VncChatBoxView.extend({
    length: 300,
    tagName: 'div',
    className: 'chatroom chatbody',

    template: _.template(
        //TODO: chat room topic
        /*    '<div class="chat-head chat-head-chatroom">' +
                '<div class="chat-title"> <%= name %> </div>' +
                '<a href="javascript:void(0)" class="chatbox-button close-chatbox-button">X</a>' +
                '<p class="chatroom-topic"><p/>' +
            '</div>' +*/
            '<div class="roomParticipants">' +
                '<span class="roomParticipantsHeader">Participants:</span>' +
                '<ul class="participant-list">' +
                '<li class="addParticipantsItem">' +
                  '<a href="javascript:void(0)" class="addParticipants">' +
                    'Add...' +
                  '</a>' +
                '</li>' +
                '</ul>' +
            '</div>' +
            '<div>' +
            '<div class="chat-area">' +
                '<div class="chat-content">' +
                    '<div class="room-name"></div>' +
                    '<div class="room-topic"></div>' +
                    '<div class="history-box">' +
                       '<span class="history-box-header">View Earlier Messages</span>' +
                       '<ul>' +
                       '<li><a class="historyControl one-day-history" href="#">1 Day</a></li>' +
                       '<li><a class="historyControl one-week-history" href="#">1 Week</a></li>' +
                       '<li><a class="historyControl two-weeks-history" href="#">2 Weeks</a></li>' +
                       '<li><a class="historyControl one-month-history" href="#">1 Month</a></li>' +
                       '<li><a class="historyControl six-months-history" href="#">6 Months</a></li>' +
                       '<li><a class="historyControl one-year-history" href="#">1 Year</a></li>' +
                       '<li><a class="historyControl all-history" href="#">All</a></li>' +
                    '</div>' +
                '</div>' +
                '<form class="sendXMPPMessage" action="" method="post">' +
                    '<textarea ' +
                        'type="text" ' +
                        'class="chat-textarea" ' +
                        'placeholder="Enter your message here..."/>' +
                '</form>' +
            '</div>' +
            '</div>'),

    events: {
        'click .close-chattab-button': 'closeChat',
        'keypress textarea.chat-textarea': 'keyPressed',
        'click .historyControl':'getHistory',
        'click .addParticipants':'addParticipants'
    },

    initialize: function () {
        this.tab = new vncchat.VncChatRoomTab({ body:this });
        muc = vncchat.connection.muc;
        muc.join(this.model.get('jid'), 
                 this.model.get('nick'),
                 $.proxy(this.onMessage, this),
                 $.proxy(this.onPresence, this));
        var that = this;
        //XXX temporary room configuration.
        //XXX we showd do this only if we are the owner
        muc.configure(this.model.get('jid'), function(configuration) {
            $('field', configuration).each(function (index, field) {
                if ($(field).attr('var') == 'muc#roomconfig_membersonly') {
                    $('value', field).text('1');
                };
                if ($(field).attr('var') == 'muc#roomconfig_publicroom') {
                    $('value', field).text('0');
                };
                if ($(field).attr('var') == 'muc#roomconfig_persistentroom') {
                    $('value', field).text('1');
                };
            });

            //XXX turn off history fetch.
            //$('x', configuration).append($('<field>').attr('type', 'text-single')
            //    .attr('label', 'Maximum Number of History Messages Returned by Room')
            //    .attr('var', 'muc#maxhistoryfetch')
            //    .append("<value>0</value>"))

            muc.saveConfiguration(
                  that.model.get('jid'),
                  $('x', configuration).children());
        });
        this.save_joined_room(this.model.get('jid'));
    },

    closeChatRoom: function () {
        this.closeChat();
        vncchat.connection.muc.leave(
                        this.model.get('jid'), 
                        this.model.get('nick'), 
                        this.onLeave,
                        undefined);
        delete vncchat.chatboxesview.views[this.model.get('jid')];
        vncchat.chatboxesview.model.remove(this.model.get('jid'));
        this.remove_joined_room(this.model.get('jid'));
        this.tab.$el.remove();
        this.remove();
        var controlboxview = vncchat.chatboxesview.views['online-users-container'];
        if (controlboxview) {
            controlboxview.roomspanel.trigger('update-rooms-list');
        }
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
          return false;
        }
    },

    sendGroupMessage: function (body) {
        var match = body.replace(/^\s*/, "").match(/^\/(.*?)(?: (.*))?$/);
        var args = null;
        if (match) {
            if (match[1] === "msg") {
                // TODO: Private messages
            } else if (match[1] === "topic") {
                vncchat.connection.muc.setTopic(this.model.get('jid'), match[2]);

            } else if (match[1] === "kick") {
                vncchat.connection.muc.kick(this.model.get('jid'), match[2]);

            } else if (match[1] === "ban") {
                vncchat.connection.muc.ban(this.model.get('jid'), match[2]);

            } else if (match[1] === "op") {
                vncchat.connection.muc.op(this.model.get('jid'), match[2]);

            } else if (match[1] === "deop") {
                vncchat.connection.muc.deop(this.model.get('jid'), match[2]);
            } else {
                this.last_msgid = vncchat.connection.muc.groupchat(this.model.get('jid'), body);
            }
        } else {
            this.last_msgid = vncchat.connection.muc.groupchat(this.model.get('jid'), body);
        }
    },

    onLeave: function () {
        var controlboxview = vncchat.chatboxesview.views['online-users-container'];
        if (controlboxview) {
            controlboxview.roomspanel.trigger('update-rooms-list');
        }
    },

    onPresence: function (presence, room) {
        var nick = room.nick,
            from = Strophe.getResourceFromJid($(presence).attr('from'));
            node = Strophe.unescapeNode(from);
            $participants = this.$el.find('.participant-list'),
            participants = [];
            fullname = node;

        if ($(presence).attr('type') !== 'error') {
            // check for status 110 to see if it's our own presence
            if ($(presence).find("status[code='110']").length > 0) {
                // check if server changed our nick
                if ($(presence).find("status[code='210']").length > 0) {
                    this.model.set({'nick': from});
                }
            }
        }

        if ($(presence).attr('type') == 'unavailable') {
            this.$el.find('.participant-list li#' + node).remove();
        } else {
            var that = this;
            vncchat.get_user_info(node, function (data) {
                if (data && data.fullname) {
                    fullname = data.fullname;
                }
                if (that.$el.find( '.participant-list li#' +
                        escapeSelector(node)).length == 0) {
                    $participants.prepend('<li id="'+node+'">' + fullname +
                                            '<a class="removeParticipantButton" href="javascript:void(0)">X</a>' +
                                          '</li>');
                }
            });
        }

        var controlboxview = vncchat.chatboxesview.views['online-users-container'];
        if (controlboxview) {
            controlboxview.roomspanel.trigger('update-rooms-list');
        }
        return true;
    },

    onMessage: function (message) {
        var body = $(message).children('body').text(),
            jid = $(message).attr('from'),
            bare_jid = Strophe.getBareJidFromJid(jid);
            composing = $(message).find('composing'),
            $chat_content = $(this.el).find('.chat-content'),
            sender = Strophe.getResourceFromJid(jid),
            subject = $(message).children('subject').text();
            user_id = Strophe.unescapeNode(sender);
            fullname = user_id;

        if (bare_jid !== this.model.get('jid')) {
            vncchat.chatboxesview.views[bare_jid].onMessage(message);
            return true;
        }

        var that = this;
        vncchat.get_user_info(user_id, function (data) {
            if (data && data.fullname) {
                fullname = data.fullname
            }
            if (subject) {
                that.$el.find('.chatroom-topic').text(subject);
            }
            if (!body) {
                if (composing.length > 0) {
                    that.insertStatusNotification(fullname, 'is typing');
                    return true;
                }
            } else {
                if (fullname=== that.model.get('nick')) {
                    that.appendMessage(body);
                } else {
                    $chat_content.find('div.chat-event').remove();

                    match = body.match(/^\/(.*?)(?: (.*))?$/);
                    if ((match) && (match[1] === 'me')) {
                        body = body.replace(/^\/me/, '*'+fullname);
                        $chat_content.append(
                                that.action_template({
                                    'sender': 'room', 
                                    'time': that.formatTimeStamp(new Date()),
                                    'message': body, 
                                    'username': fullname,
                                    'extra_classes': ($(message).find('delay').length > 0) && 'delayed' || ''
                                }));
                    } else {
                        $chat_content.append(
                                that.message_template({
                                    'sender': 'room', 
                                    'time': that.formatTimeStamp(new Date()),
                                    'message': body,
                                    'username': fullname,
                                    'extra_classes': ($(message).find('delay').length > 0) && 'delayed' || ''
                                }));
                    }
                    $chat_content.scrollTop($chat_content[0].scrollHeight);
                }
            }

        });
        if (!this.$el.is(':visible')) {
            if ($.makeArray(vncchat.chatboxesview.tabs).length == 0) {
                vncchat.chatboxesview.showChat(bare_jid);
            } else {
                this.tab.show();
                this.tab.$el.addClass('newMessage');
            }
        }
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
            seneder_username,
            $message = $(message),
            from = Strophe.unescapeNode($message.attr('name') || ''),
            time = new Date(Date.parse(start)),
            fullname = from;
        time.setSeconds(time.getSeconds() + parseInt($(message).attr('secs')));
        $chat_content = $(this.el).find('.chat-content')

        if (!from) {
            return false;
        }

        var that = this;
        vncchat.get_user_info(from, function (data) {
            if (data) {
                fullname = data.fullname;
            }
            body = $('body', message).text();
            node = Strophe.unescapeNode(from);
            match = body.match(/^\/(.*?)(?: (.*))?$/);
            if ((match) && (match[1] === 'me')) {
                body = body.replace(/^\/me/, '*'+ ((node == vncchat.username) ? vncchat.fullname:fullname));
                $chat_content.append(that.action_template({
                                     'sender': (node == vncchat.username) ? 'me':'them',
                                     'time': that.formatTimeStamp(time),
                                     'message': body, 
                                     'username': (node == vncchat.username) ? vncchat.fullname:fullname,
                                     'extra_classes': ''
                 }));
            } else {
                $chat_content.append(that.message_template({
                  'sender': (node == vncchat.username) ? 'me':'them',
                  'time': that.formatTimeStamp(time),
                  'message': body,
                  'username':(node == vncchat.username) ? vncchat.fullname:fullname,
                  'extra_classes': ''
                }));
            }
            $chat_content.scrollTop($chat_content[0].scrollHeight);
        });
    },


    addParticipants: function (event) {
        event.preventDefault();
        var participants,
            $participants =this.$el.find('.participant-list li')
                .clone().children().remove().end();
            recipients = [],
            participants = {};

        $participants.each(function() {
            name = $(this).text();
            if (name) { participants[name] = 1 };
        });

        roster = vncchat.roster.sort().models;
        for (var i=0;i<roster.length;i++) {
            jid = roster[i].id;
            node = Strophe.getNodeFromJid(jid);
            var fullname = roster[i].attributes.fullname;
            if  (fullname in participants) { continue; };
            recipients.push({'name':fullname, 'jid':jid});
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
            for (var i=0; i<recipients.length; i++) {
               $request_dialog
                .append('<input type="checkbox" name="' + 
                        recipients[i].name + '" ' +
                        'value="'+recipients[i].jid+'" />' +
                        recipients[i].name+'</br>');
            }
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

    save_joined_room: function(jid) {
        var cookie = jQuery.cookie('joined-rooms-'+vncchat.username),
            new_cookie,
            joined_rooms = [];

        if (cookie) {
            joined_rooms = cookie.split('|');
        };
        if ($.inArray(jid, joined_rooms) == -1) {
            joined_rooms.push(jid);
            new_cookie = joined_rooms.join('|');
            jQuery.cookie('joined-rooms-'+vncchat.username, new_cookie, {path: '/'});
            console.log('updated cookie = ' + new_cookie + '\n');
        }
    },

    remove_joined_room: function(jid) {
        var cookie = jQuery.cookie('joined-rooms-'+vncchat.username),
            joined_rooms= [],
            new_rooms = [];

        if (cookie) {
            joined_rooms= cookie.split('|');
        }
        for (var i=0; i < joined_rooms.length; i++) {
            if (joined_rooms[i] != jid) {
                new_rooms.push(joined_rooms[i]);
            }
        }
        if (new_rooms.length) {
            jQuery.cookie('joined-rooms-'+vncchat.username, new_rooms.join('|'), {path: '/'});
        }
        else {
            jQuery.cookie('joined-rooms-'+vncchat.username, null, {path: '/'});
        }
    },

});

vncchat.VncRoomsPanel = vncchat.RoomsPanel.extend({

    events: {
        'submit form.add-chatroom': 'createChatRoom',
        'click a.open-room': 'createChatRoom',
        'click a.leaveRoom': 'closeChatRoom'
    },

    room_template: _.template(
                        '<dd class="chatroom">' +
                        '<a class="open-room" room-jid="<%=jid%>" title="Click to open this chatroom" href="#">' +
                        '<%=name%></a>' +
                        '<a class="leaveRoom" href="#" room-jid="<%=jid%>"></a></dd>'),

    createChatRoom: function (ev) {
        ev.preventDefault();
        var name, jid;
        if (ev.type === 'click') {
            jid = $(ev.target).attr('room-jid');
        } else {
            // FIXME: Hardcoded
            name = $(ev.target).find('input.new-chatroom-name').val()
                               .replace(/^\s+|\s+$/g, '');
            if (name) {
                name = Strophe.escapeNode(name);
                jid = name + '@' + vncchat.connection.muc_domain;
            }
        }
        if (jid) {
            vncchat.chatboxesview.openChat(jid);
            this.updateRoomsList();
        }
    },

    closeChatRoom: function (ev) {
        ev.preventDefault();
        jid = $(ev.target).attr('room-jid');
        if (vncchat.chatboxesview.views[jid]) {
            vncchat.chatboxesview.views[jid].tab.closeTab();
            vncchat.chatboxesview.views[jid].closeChatRoom();
        }
        this.updateRoomsList();
    },

    invitationReceived: function (invitation) {
        var room = $(invitation).attr('from');
            from = Strophe.unescapeNode(
                   Strophe.getNodeFromJid(
                    $(invitation).find('invite').attr('from')));
            fullname = from;

        that = this;
        vncchat.get_user_info(from, function (data) {
            if (data && data.fullname) {
                fullname = data.fullname
            }
            $("<span></span>").dialog({
                title: fullname + ' invites you to join ' + 
                     Strophe.getNodeFromJid(room) + ' room.',
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
                        if (!$('#vnc-chat').is(':visible')) {
                            if ($('#vnc-stream').is(':visible')) {
                                $('#vnc-chat').show();
                            } else {
                                $('#vnc-chat').slideDown();
                            }
                        }
                    },
                    "Cancel": function() {
                        $(this).dialog( "close" );
                    }
                }
            });

        });
    },
});

vncchat.VncContactsPanel = vncchat.ContactsPanel.extend({

    events: {
        'click a.startChatWith': 'toggleContactForm',
        'submit form.search-xmpp-contact': 'searchContacts',
        'click a.subscribe-to-user': 'subscribeToContact'
    },

    toggleContactForm: function (ev) {
        ev.preventDefault();
        this.$el.find('form.search-xmpp-contact').fadeToggle('medium').find('input.username').focus();
        pmessage = $('div.startChatWith').find('#pending-contact-message');
        if (pmessage.length > 0) {
            pmessage.remove();
        }
    },

    searchContacts: function (ev) {
        ev.preventDefault();
        var value = $.trim($(ev.target).find('input.username').val());
        if (!value) {
          return false;
        }
        
        var contacts_models = $.grep(vncchat.roster.models, function(e, i) {
            return (e.get('subscription') == 'both')});
        $.getJSON(portal_url + "/search-contacts?q=" + value, function (data) {
            $('#found-users').remove();
            $('.startChatWith .search-msg').remove();
            var $results_el = $('<ul id="found-users"></ul>');
            $(data).each(function (idx, obj) {
                // user is already in contacts list
                if ($.inArray(Strophe.escapeNode(obj.id), $.map(contacts_models,
                    function (e, i) {return Strophe.getNodeFromJid(e.get('id'))}
                    )) != -1) {
                    $results_el.append($('<li></li>')
                        .attr('id', 'found-contacts-'+obj.id)
                        .append($('<a class="open-chat" href="#" title="' +
                            'Click to chat with contact"></a>')
                        .attr('data-recipient', Strophe.escapeNode(obj.id)+'@'+
                            vncchat.connection.domain)
                            .text(obj.fullname).on(
                                'click', function (ev) {
                                    ev.preventDefault();
                                    jid = Strophe.escapeNode(obj.id)+'@'+
                                        vncchat.connection.domain;
                                    vncchat.chatboxesview.openChat(jid);
                                    // remove search results
                                    $('#found-users').remove();
                                }
                            )
                        )
                    );
                } else {
                  // user is not in contact list
                    $results_el.append($('<li></li>')
                        .attr('id', 'found-users-'+obj.id)
                        .append($('<a class="subscribe-to-user" href="#" ' +
                            'title="Click to add as a chat contact"></a>')
                            .attr('data-recipient', Strophe.escapeNode(obj.id)+
                                '@'+vncchat.connection.domain)
                            .text(obj.fullname)
                        )
                    );
                }
            });
            if ($(data).length == 0) {
              $results_el = '<p class="search-msg">No users found.</p>';
            }
            // add list to page DOM
            $(ev.target).after($results_el);
        });
    },

    subscribeToContact: function (ev) {
        ev.preventDefault();
        var jid = $(ev.target).attr('data-recipient');
        xmppchat.connection.roster.add(jid, '', [], function (iq) {
            // XXX: We can set the name here!!!
            xmppchat.connection.roster.subscribe(jid);
        });
        $(ev.target).parents('ul#found-users').remove();
        $('div.startChatWith').append('<p class="search-msg">User has been ' +
            'successfully added to pending list. As soon as user accepts your' +
            ' request you will be able to start chat with him.</p>');
        setTimeout('jQuery("div.startChatWith p.search-msg").remove();', 10000);
    }

});

vncchat.VncControlBoxView = vncchat.ControlBoxView.extend({

    initialize: function () {
        var userspanel; 
        $('ul.tabs').tabs('div.panes > div');
        this.contactspanel = new vncchat.VncContactsPanel();
        this.roomspanel = new vncchat.VncRoomsPanel();
        this.settingspanel = new vncchat.SettingsPanel();
    }

});

vncchat.VncRoster = (function (_, $, console) {
    var ob = {},
        Collection = Backbone.Collection.extend({
            model: vncchat.VncRosterItem,
            stropheRoster: vncchat.connection.roster,

            initialize: function () {
                this._connection = vncchat.connection;
            },

            comparator : function (rosteritem) {
                var presence_type = rosteritem.get('presence_type'),
                    rank = 4;
                switch(presence_type) {
                    case 'offline': 
                        rank = 4;
                        break;
                    case 'unavailable':
                        rank = 3;
                        break;
                    case 'away':
                        rank = 2;
                        break;
                    case 'busy':
                        rank = 1;
                        break;
                    case 'dnd':
                        rank = 1;
                        break;
                    case 'online':
                        rank = 0;
                        break;
                }
                return rank;
            },

            isSelf: function (jid) {
                return (Strophe.getBareJidFromJid(jid) === Strophe.getBareJidFromJid(vncchat.connection.jid));
            },

            getRoster: function (callback) {
                return vncchat.connection.roster.get(callback);
            },

            getItem: function (id) {
                return Backbone.Collection.prototype.get.call(this, id);
            },

            addRosterItem: function (jid, subscription, ask) {
                var model = new vncchat.VncRosterItem(jid, subscription, ask);
                this.add(model);
            },

            addResource: function (bare_jid, resource) {
                var item = this.getItem(bare_jid),
                    resources;
                if (item) {
                    resources = item.get('resources');
                    if (resources) {
                        if (_.indexOf(resources, resource) == -1) {
                            resources.push(resource);
                            item.set({'resources': resources});
                        }
                    } else  {
                        item.set({'resources': [resource]});
                    }
                }
            },

            removeResource: function (bare_jid, resource) {
                var item = this.getItem(bare_jid),
                    resources,
                    idx;
                if (item) {
                    resources = item.get('resources');
                    idx = _.indexOf(resources, resource);
                    if (idx !== -1) {
                        resources.splice(idx, 1);
                        item.set({'resources': resources});
                        return resources.length;
                    }
                }
                return 0;
            },

            clearResources: function (bare_jid) {
                var item = this.getItem(bare_jid);
                if (item) {
                    item.set({'resources': []});
                }
            },

            getTotalResources: function (bare_jid) {
                var item = this.getItem(bare_jid);
                if (item) {
                    return _.size(item.get('resources'));
                }
            },

            getNumOnlineContacts: function () {
                var count = 0;
                for (var i=0; i<this.models.length; i++) {
                    if (_.indexOf(['offline', 'unavailable'], this.models[i].get('presence_type')) === -1) {
                        count++;
                    }
                }
                return count;
            }

        });

    var collection = new Collection();
    _.extend(ob, collection);
    _.extend(ob, Backbone.Events);

    ob.rosterHandler = function (items) {
        var model, item;
        for (var i=0; i<items.length; i++) {
            item = items[i];
            model = ob.getItem(item.jid);
            if (!model) {
                ob.addRosterItem(item.jid, item.subscription, item.ask);
            } else {
                model.set({'subscription': item.subscription, 'ask': item.ask});
            }
        }
    };

    ob.presenceHandler = function (presence) {
        var jid = $(presence).attr('from'),
            bare_jid = Strophe.getBareJidFromJid(jid),
            resource = Strophe.getResourceFromJid(jid),
            presence_type = $(presence).attr('type'),
            show = $(presence).find('show'),
            status_message = $(presence).find('status'),
            item;

        if ((($(presence).find('x').attr('xmlns') || '').indexOf(Strophe.NS.MUC) === 0) || (ob.isSelf(bare_jid))) {
            // Ignore MUC or self-addressed stanzas
            return true;
        }

        if (status_message.length > 0) {
            model = ob.getItem(bare_jid);
            if (model) {
                model.set({'status': status_message.text()});
            }
        }

        if ((presence_type === 'error') || 
                (presence_type === 'subscribed') || 
                (presence_type === 'unsubscribe')) {
            return true;
        } else if (presence_type === 'subscribe') {
            if (ob.getItem(bare_jid)) { 
                vncchat.connection.roster.authorize(bare_jid);
            } else {
                ob.addRosterItem(bare_jid, 'none', 'request');
            }
        } else if (presence_type === 'unsubscribed') {
            /* Upon receiving the presence stanza of type "unsubscribed", 
             * the user SHOULD acknowledge receipt of that subscription state 
             * notification by sending a presence stanza of type "unsubscribe" 
             * this step lets the user's server know that it MUST no longer 
             * send notification of the subscription state change to the user.
             */
            vncchat.xmppstatus.sendPresence('unsubscribe');
            if (vncchat.connection.roster.findItem(bare_jid)) {
                vncchat.roster.remove(bare_jid);
                vncchat.connection.roster.remove(bare_jid);
            }
        } else { 
            if ((presence_type === undefined) && (show)) {
                if (show.text() === 'chat') {
                    presence_type = 'online';
                } else if (show.text() === 'dnd') {
                    presence_type = 'busy';
                } else if (show.text() === 'xa') {
                    presence_type = 'offline';
                } else {
                    presence_type = show.text();
                }
            }

            if ((presence_type !== 'offline')&&(presence_type !== 'unavailable')) {
                ob.addResource(bare_jid, resource);
                model = ob.getItem(bare_jid);
                model.set({'presence_type': presence_type});
            } else {
                if (ob.removeResource(bare_jid, resource) === 0) {
                    model = ob.getItem(bare_jid);
                    model.set({'presence_type': presence_type});
                }
            }
        }
        return true;
    };
    return ob;
});
vncchat.VncRosterItemView = vncchat.RosterItemView.extend({

    template: _.template(
                '<img width="36" height="36" src="<%=portrait %>" />' +
                '<a class="open-chat" title="Click to chat with this contact" href="#"><%= fullname %></a>' +
                '<a class="remove-xmpp-contact" title="Click to remove this contact" href="#"></a>'),

    render: function () {
        var item = this.model,
            ask = item.get('ask'),
            that = this,
            subscription = item.get('subscription');

        $(this.el).addClass(item.get('presence_type')).attr('id', 'online-users-'+item.get('user_id'));

        if (ask === 'subscribe') {
            this.$el.addClass('pending-xmpp-contact');
            $(this.el).html(this.template(item.toJSON()));
        } else if (ask === 'request') {
            this.$el.addClass('requesting-xmpp-contact');
            $(this.el).html(this.request_template(item.toJSON()));
            this.$el.find('.accept-xmpp-request').on('click', function (ev) {
                ev.preventDefault();
                that.acceptRequest();
            });
            this.$el.find('.decline-xmpp-request').on('click', function (ev) {
                ev.preventDefault();
                that.declineRequest();
            });
        } else if (subscription === 'both') {
            this.$el.addClass('current-xmpp-contact');
            this.$el.html(this.template(item.toJSON()));
            this.$el.find('.open-chat').on('click', function (ev) {
                ev.preventDefault();
                that.openChat();
            });
        }

        // Event handlers
        this.$el.find('a.remove-xmpp-contact').on('click', function (ev) {
            ev.preventDefault();
            that.removeContact();
        });
        return this;
    }
});

vncchat.VncRosterView= (function (roster, _, $, console) {
    var View = Backbone.View.extend({
        el: $('#xmppchat-roster'),
        model: roster,
        rosteritemviews: {},

        initialize: function () {
            if (this.model.models.length > 0) {
                for (var i=0; i<this.model.models.length;i++) {
                    var elem = this.model.models[i];
                    var view = new vncchat.VncRosterItemView({model: elem});
                    this.rosteritemviews[elem.id] = view;
                    if (elem.get('ask') === 'request') {
                        view.on('decline-request', function (elem) {
                            this.model.remove(elem.id);
                        }, this);
                    }
                };
                this.render();
            };
            this.model.on("add", function (item) {
                var view = new vncchat.VncRosterItemView({model: item});
                this.rosteritemviews[item.id] = view;
                if (item.get('ask') === 'request') {
                    view.on('decline-request', function (item) {
                        this.model.remove(item.id);
                    }, this);
                }
                this.render();
            }, this);

            this.model.on('change', function (item) {
                this.render();
            }, this);

            this.model.on("remove", function (item) {
                delete this.rosteritemviews[item.id];
                this.render();
            }, this);

            this.model.on('show-contact', function (jid) {
                var $opened_chats = this.$el.find('#opened-xmpp-chats'),
                    view = this.rosteritemviews[jid];
                if (!$('#opened-xmpp-chats').nextUntil('dt')
                                           .is(view.render().$el)) {
                    $opened_chats.after(view.render().el);
                };
                if (!$opened_chats.is(':visible')) {
                    $opened_chats.show();
                };
            }, this);

            this.model.on('hide-contact', function (jid) {
                var $opened_chats = this.$el.find('#opened-xmpp-chats'),
                    view = this.rosteritemviews[jid];
                view.render().$el.remove();
                if ($opened_chats.is(':visible') && $opened_chats.nextUntil('dt').length == 0) {
                    $opened_chats.hide();
                }
            }, this);

        },

        template: _.template('<dt id="xmpp-contact-requests">Contact requests</dt>' +
                             '<dt id="opened-xmpp-chats">Opened chats</dt>' +
                             '<dt id="pending-xmpp-contacts">Pending contacts</dt>'),

        render: function () {
            this.$el.empty().html(this.template());
            var models = this.model.sort().models,
                children = $(this.el).children(),
                my_contacts = this.$el.find('#xmpp-contacts').hide(),
                contact_requests = this.$el.find('#xmpp-contact-requests').hide(),
                pending_contacts = this.$el.find('#pending-xmpp-contacts').hide();
                chats_cookie = jQuery.cookie('chats-open-'+vncchat.username),
                open_chats = [];

            if (chats_cookie) {
                open_chats = $.map(chats_cookie.split('|'), function (el, i) {
                    return el.split(':')[0];
                });
            };

            for (var i=0; i<models.length; i++) {
                var model = models[i],
                    user_id = Strophe.getNodeFromJid(model.id),
                    view = this.rosteritemviews[model.id],
                    ask = model.get('ask'),
                    subscription = model.get('subscription');

                if (ask === 'subscribe') {
                    pending_contacts.after(view.render().el);
                } else if (ask === 'request') {
                    contact_requests.after(view.render().el);
                } else if (subscription === 'both' &&
                           $.inArray(model.id, open_chats) !== -1) {
                    this.model.trigger('show-contact', model.id);
                }
            }
            // Hide the headings if there are no contacts under them
            _.each([my_contacts, contact_requests, pending_contacts], function (h) {
                if (h.nextUntil('dt').length > 0) {
                    h.show();
                }
            });
            $('#online-count').text(this.model.getNumOnlineContacts());
        }
    });
    var view = new View();
    return view;
});
