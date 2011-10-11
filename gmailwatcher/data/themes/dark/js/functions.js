var accounts = {}

var collapse_thread = function(thread) {
    messages = $(thread).children(':not(:last-child)').find('dt');
    $(messages).each(function(iter, elem) {
        $(elem).next().hide();
    })
}

var add_account = function(account) {
    var email = account.account;
    accounts[email] = {'folders': account.folders}

    folder_list = $('.folders[account='+email+']');
    if (folder_list.length == 0) {
        $('#foldersListTmpl').tmpl(account).appendTo('#sidebar');
        $('#emailsListTmpl').tmpl(account).appendTo('#content');
    }

    folders = []
    for (i in account.folders) {
        folders.push({
            'folder': account.folders[i],
            'account': email,
            'folder_id': i
          });
    };
    $('.folder[account='+email+']').remove();
    $('#folderTmpl').tmpl(folders).appendTo('.folders[account='+email+']');
    show_account(email);
};

var new_email = function(mail) {
    var account =  mail.account;
    var folder = mail.folder;
    var thread_id = mail.thread_id;
    mail.folder_id = accounts[account].folders.indexOf(folder);

    var email = $('#emailTmpl').tmpl(mail);
    thread = $('.email[thread_id='+thread_id+']');
    if (thread.length > 0) {
        email.find('.email-body').appendTo(thread);
    } else {
        mail_list = $('.emails[account='+account+']');
        email.prependTo(mail_list);
    };

    if (!$('.folder[account='+account+'][folder='+mail.folder_id+']').hasClass('selected')) {
        email.hide();
        $('.folder[account='+account+'][folder='+mail.folder_id+']').addClass('unseen');
        console.log($('.folder[account='+account+'][folder='+mail.folder_id+']'))
    }

    collapse_thread($('.email[thread_id='+thread_id+']'));
};

var show_account = function(account) {
    $('ul.folders').hide();
    $('ul.folders[account='+account+']').show();
    $('ul.folders[account='+account+']').children().first().click();
};

var test_data = function() {
    add_account({"folders": ["OdeskPS", "[GMAIL]/Important", "G+", "INBOX"], "account": "loneowais@gmail.com", "display_name": "Gmail"})


  new_email({"thread_id": "13762566744534478134",  "mail": [{"labels": [], "from": "\"GoDaddy.com\" <offers@godaddy.com>", "msg_id": "1376256674453447813", "thread_id": "1376256674453447813", "date": "4 Aug 2011 16:29:39 -0700", "starred": "", "system_labels": ["Important"], "subject": "Just Days left to SAVE 28%!"}], "account": "loneowais@gmail.com", "folder": "OdeskPS"});

    var i=0;

    while (i<1) {

new_email({"thread_id": "1376256674453447813",  "mail": [{"labels": [], "from": "\"GoDaddy.com\" <offers@godaddy.com>", "msg_id": "1376256674453447813", "thread_id": "1376256674453447813", "date": "4 Aug 2011 16:29:39 -0700", "starred": "", "system_labels": ["Important"], "subject": "Just Days left to SAVE 28%!"}], "account": "loneowais@gmail.com", "folder": "G+"});

new_email({"thread_id": "1376256674453447813",  "mail": [{"labels": [], "from": "\"GoDaddy.com\" <offers@godaddy.com>", "msg_id": "1376256674453447813", "thread_id": "1376256674453447813", "date": "4 Aug 2011 16:29:39 -0700", "starred": "", "system_labels": ["Important"], "subject": "Just Days left to SAVE 28%!"}], "account": "loneowais@gmail.com", "folder": "G+"});


new_email({"thread_id": "13762ds566744534478132",  "mail": [{"labels": [], "from": "\"GoDaddy.com\" <offers@godaddy.com>", "msg_id": "1376256674453447813", "thread_id": "1376256674453447813", "date": "4 Aug 2011 16:29:39 -0700", "starred": "", "system_labels": ["Important"], "subject": "Just Days left to SAVE 28%!"}], "account": "loneowais@gmail.com", "folder": "INBOX"});

    i = i+1;
    };
};

var theme = {};
theme.set_colors = function(color) {
  $('#sidebar, #sidebar *').css('background', color.bg)
  $('#sidebar, #sidebar *').css('border-color', color.border)
  $('#sidebar, #sidebar *').css('color', color.color)
};


$(document).ready(function() {

    $('.folder').live('click', function(event) {
        $('.folder').removeClass('selected');
        $('.email').hide();
        folder = $(this).attr('folder');
        account = $(this).attr('account');
        $('.email[account='+account+'][folder='+folder+']').show();
        $(this).addClass('selected');
        $(this).removeClass('unseen');
    });

    $('dt').live('click', function() {
        dd = $(this).next();
        if ($(dd).is(':hidden')) {
            $(dd).slideDown();
        }
        else {
            $(dd).slideUp();
        }
    });
   //test_data()
});


