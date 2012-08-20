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
    showMessage: function(type, body, time) {
        var sender,
            seneder_username;
        if (type == 'to' ){
            sender = 'me';
            sender_username = vncchat.username;
        } else if (type == 'from') {
            sender = 'them';
            sender_username = this.model.get('jid');
        } else {
            return;
        }
        $chat_content = $(this.el).find('.chat-content')
        $chat_content.append(this.message_template({
            'sender': sender,
            'time': time.toLocaleFormat('%d.%m.%Y %H:%M'),
            'message': body, 
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
                start = new Date(Date.parse($results.attr('start')));
                $.each($results.children(), function (index, value) {
                    type = value.tagName;
                    body = $('body', value).text();
                    start.setSeconds(start.getSeconds() +
                        parseInt($(value).attr('secs')));
                    that.showMessage(type, body, start);
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

vncchat.VncChatBoxesView = xmppchat.ChatBoxesView.extend({

    renderChat: function (jid) {
        var box, view;
        if (jid === 'online-users-container') {
            box = new xmppchat.ControlBox({'id': jid, 'jid': jid});
            view = new xmppchat.ControlBoxView({
                model: box 
            });
        } else {
            if (this.isChatRoom(jid)) {
                box = new xmppchat.ChatRoom(jid);
                view = new xmppchat.ChatRoomView({
                    'model': box
                });
            } else {
                box = new xmppchat.ChatBox({'id': jid, 'jid': jid});
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










