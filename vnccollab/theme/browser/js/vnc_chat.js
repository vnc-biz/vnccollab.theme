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

vncchat.VncChatBoxView = vncchat.ChatBoxView.extend({

    tagName: 'div',
    className: 'vncChatbox',

    template: _.template(
                '<div class="chat-head chat-head-chatbox">' +
                    '<div class="chat-title"> <%= user_id %> </div>' +
                    '<a href="javascript:void(0)" class="chatbox-button close-chatbox-button">X</a>' +
                    '<p class="user-custom-message"><p/>' +
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
        'click .close-chatbox-button': 'closeChat',
        'keypress textarea.chat-textarea': 'keyPressed',
        'click .historyControl':'getHistory'
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

});

vncchat.VncChatBoxesView = vncchat.ChatBoxesView.extend({

    renderChat: function (jid) {
        var box, view;
        if (jid === 'online-users-container') {
            box = new xmppchat.ControlBox({'id': jid, 'jid': jid});
            view = new xmppchat.ControlBoxView({
                model: box 
            });
        } else {
            if (this.isChatRoom(jid)) {
                box = new vncchat.ChatRoom(jid);
                view = new vncchat.VncChatRoomView({
                    'model': box
                });
            } else {
                box = new vncchat.ChatBox({'id': jid, 'jid': jid});
                view = new vncchat.VncChatBoxView({
                    model: box
                });
            }
        }
        this.views[jid] = view.render();
        view.$el.appendTo(this.$el);
        this.options.model.add(box);
        return view;
    },
});

vncchat.VncChatRoomView = vncchat.VncChatBoxView.extend({
    length: 300,
    tagName: 'div',
    className: 'chatroom',

    template: _.template(
            '<div class="chat-head chat-head-chatroom">' +
                '<div class="chat-title"> <%= name %> </div>' +
                '<a href="javascript:void(0)" class="chatbox-button close-chatbox-button">X</a>' +
                '<p class="chatroom-topic"><p/>' +
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
            '<div class="participants">' +
                '<ul class="participant-list"></ul>' +
            '</div>' +
            '</div>'),

    events: {
        'click .close-chatbox-button': 'closeChatRoom',
        'keypress textarea.chat-textarea': 'keyPressed',
        'click .historyControl':'getHistory'
    },

    initialize: function () {
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
        this.$el.find('.participant-list').empty();
        for (var i=0; i<_.size(roster); i++) {
            this.$el.find('.participant-list').append('<li>' + _.keys(roster)[i] + '</li>');
        }
        return true;
    },

    show: function () {
        this.$el.css({'opacity': 0});
        this.$el.css({'display': 'inline'});
        this.$el.animate({
            opacity: '1'
        }, 200);
        return this;
    },

    render: function () {
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
    }
});
