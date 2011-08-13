var collapse_thread = function(thread) {
    messages = $(thread).children(':not(:last-child)').find('dt');
    $(messages).each(function(iter, elem) {
        $(elem).next().hide();
    })
}

var add_account = function(account) {
    var folders = account.folders;
    var email = account.account;
    var account_tab = $('.account-tab[id='+email+']');
    if (account_tab.length == 0) {
        var account_tab = $('#accountTabTmpl').tmpl(account);
        account_tab.appendTo('#accounts');
        $('#foldersListTmpl').tmpl(account).appendTo('#sidebar');
        $('#emailsListTmpl').tmpl(account).appendTo('#content');
    }

    var old_folders = []
    $('li.folder[id^='+email+'_]').each(function(iter, folder) {
        old_folders.push($(folder).attr('id'));
    });

    var folders_list = []
    for (i in folders) {    
        folder_id = email+'_'+folders[i]
        if (old_folders.indexOf(folder_id) == -1) {
            folders_list.push({
                'folder':folders[i],
                'account':email
            });
        }
    };
    $('#folderTmpl').tmpl(folders_list).appendTo('.folders[id='+email+']');
    $('option[id='+email+']').change();
};

var new_email = function(mail) {
    var account =  mail.account;
    var folder = mail.folder;
    var thread_id = mail.thread_id;
    var email = $('#emailTmpl').tmpl(mail);
    thread = $('.email[thread_id='+thread_id+']');
    if (thread.length > 0) {
        email.find('.email-body').appendTo(thread);
    } else {
        thread = $('.emails[id='+account+']');
        email.prependTo(thread);

    };

    if ($('.folder.selected').attr('id') != account+'_'+folder) {
        email.hide();
        $('.folder[id='+account+'_'+folder+']').addClass('unseen');
    }

    collapse_thread($('.email[thread_id='+thread_id+']'));
};

var show_account = function(account) {
    $('ul.folders').hide();
    $('ul.folders[id='+account+']').show();
    $('ul.folders[id='+account+']').children().first().click();
    $('.account-tab').removeClass('selected');
    account = $('option[id='+account+']');
    account.addClass('selected');
    display_name = account.text();
    $('#accounts').val(display_name);
};

var test_data = function() {
    add_account({'account':'loneowais@gmail.com','display_name':'Personal','folders':['G+','inbox','LP-Bugs','facebook','Ubuntu/Ayatana', 'Ubuntu/AyatanaUbuntu/AyatanaUbuntu/AyatanaAyatana']});
    add_account({'account':'owaislone@odeskps.com','display_name':'Work','folders':['facebook','Ubuntu/Ayatana', 'Ubuntu/AyatanaUbuntu/AyatanaUbuntu/AyatanaAyatana']});

    var i=0;

    while (i<1) {

new_email({"thread_id": "1376256674453447813",  "mail": [{"labels": [], "from": "\"GoDaddy.com\" <offers@godaddy.com>", "msg_id": "1376256674453447813", "thread_id": "1376256674453447813", "date": "4 Aug 2011 16:29:39 -0700", "starred": "", "system_labels": ["Important"], "subject": "Just Days left to SAVE 28%!"}], "account": "loneowais@gmail.com", "folder": "G+"});

new_email({"thread_id": "1376256674453447813",  "mail": [{"labels": [], "from": "\"GoDaddy.com\" <offers@godaddy.com>", "msg_id": "1376256674453447813", "thread_id": "1376256674453447813", "date": "4 Aug 2011 16:29:39 -0700", "starred": "", "system_labels": ["Important"], "subject": "Just Days left to SAVE 28%!"}], "account": "loneowais@gmail.com", "folder": "G+"});


new_email({"thread_id": "13762ds56674453447813",  "mail": [{"labels": [], "from": "\"GoDaddy.com\" <offers@godaddy.com>", "msg_id": "1376256674453447813", "thread_id": "1376256674453447813", "date": "4 Aug 2011 16:29:39 -0700", "starred": "", "system_labels": ["Important"], "subject": "Just Days left to SAVE 28%!"}], "account": "loneowais@gmail.com", "folder": "inbox"});

    i = i+1;
    };
};


$(document).ready(function() {

    $('.folder').live('click', function(event) {
        $('.folder').removeClass('selected');
        $('.email').hide();
        id = $(this).attr('id');
        $('.email[id='+id+']').show();
        $(this).addClass('selected');
        $(this).removeClass('unseen');
    });

    $('#accounts').live('change', function(event) {
        var account = $(this).find('option:selected').attr('id');
        show_account(account);
    });

    $('dt').live('click', function(){
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


