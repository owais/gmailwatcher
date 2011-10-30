var accounts = {}
var accounts_list = []

var get_account_id = function(email) {
    account_id = accounts_list.indexOf(email)
    if (account_id == -1) {
      accounts_list.push(email)
      account_id = accounts_list.indexOf(email)
    }
    account_id = account_id
    return account_id
}

var collapse_thread = function(thread) {
    messages = $(thread).children(':not(:last-child)').find('dt');
    $(messages).each(function(iter, elem) {
        $(elem).next().hide();
    })
}

var add_account = function(account) {
    var email = account.account;
    accounts[email] = {'folders': account.folders}
    account_id = get_account_id(email)
    //account.account_id = account_id
    folder_list = $('.folders[account='+account_id+']');
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
    $('.folder[account='+account_id+']').remove();
    $('#folderTmpl').tmpl(folders).appendTo('.folders[account='+account_id+']');
    show_account(email);
};

var new_email = function(mail) {
    var account =  mail.account;
    var folder = mail.folder;
    var thread_id = mail.thread_id;
    mail.folder_id = accounts[account].folders.indexOf(folder);

    account_id = get_account_id(account)
    var email = $('#emailTmpl').tmpl(mail);
    thread = $('.email[thread_id='+thread_id+']');
    if (thread.length > 0) {
        email.find('.email-body').appendTo(thread);
    } else {
        mail_list = $('.emails[account='+account_id+']');
        email.prependTo(mail_list);
    };

    if (!$('.folder[account='+account_id+'][folder='+mail.folder_id+']').hasClass('selected')) {
        email.hide();
        $('.folder[account='+account_id+'][folder='+mail.folder_id+']').addClass('unseen');
    }

    collapse_thread($('.email[thread_id='+thread_id+']'));
};

var show_account = function(account) {
    account_id = get_account_id(account)
    $('ul.folders').hide();
    $('ul.folders[account='+account_id+']').show();
    $('ul.folders[account='+account_id+']').children().first().click();
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
});


