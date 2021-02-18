$.urlParam = function(name) {
  var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
  return results ? results[1] : false;
}

$(document).ready(function(){

  setTimeout(function(){
    $('.userSearch').select2({
      allowClear: true,
      placeholder: " ",
      minimumInputLength: 3,
      ajax: {
        url: portal_url + '/ulearn.ajaxusersearch',
        data: function (term, page) {
          return {
            q: term,
            page: page, // page number
          };
        },
        results: function (data, page) {
          return data;
        },
      },
      initSelection: function(element, callback) {
        var id=$(element).val();
        $.ajax(portal_url + '/ulearn.fromusername2displayname', {
          data: {
            q: id,
          },
        }).done(function(data) { callback(data); });
      },
    });
  }, 100);

  if ($.urlParam('user')) {
    $('.typeSearch').val('user');
    $('.communityBlock').hide();
    $('.buttonAddFavorite').hide();
    $('.userBlock').show();
  } else if ($.urlParam('idcommunity')) {
    $('.typeSearch').val('community');
    $('.communityBlock').show();
    $('.buttonAddFavorite').show();
    $('.userBlock').hide();
    $('.communitySearch').val($.urlParam('idcommunity'));
  } else {
    $('.typeSearch').val('user');
    $('.communityBlock').hide();
    $('.buttonAddFavorite').hide();
    $('.userBlock').show();
  }

  $('.typeSearch').on('change', function(){
    var value = $(this).val();
    if (value == 'user') {
      $('.communityBlock').hide();
      $('.buttonAddFavorite').hide();
      $('.userBlock').show();
    } else if (value == 'community') {
      $('.communityBlock').show();
      $('.buttonAddFavorite').show();
      $('.userBlock').hide();
    } else {
      $('.communityBlock').hide();
      $('.buttonAddFavorite').hide();
      $('.userBlock').hide();
    }
  });

  $('.searchFilters input.search').on('click', function(){
    var value = $('.typeSearch').val();
    var url = window.location.href.replace('#/', '')
    index = url.indexOf('?');
    if (index != -1) {
        url = url.substring(0, index);
    }
    if (value == 'user') {
      var user = $('.userSearch').select2('val');
      if (user.length > 0) {
        window.location = url + '?user=' + user;
      }
    } else if (value == 'community') {
      window.location = url + '?idcommunity=' + $('.communitySearch').val();
    } else if (value == 'all') {
      url = url.split('/users_communities')[0]
      window.open(url + '/gestion/exports/export_users_communities.csv/@@download/file/export_users_communities.csv', '_blank');
    }
  });

  $('.searchFilters input.add_favorite').on('click', function(){
    var value = $('.typeSearch').val();
    var url = window.location.href.replace('#/', '')
    index = url.indexOf('?');
    if (index != -1) {
        url = url.substring(0, index);
    }
    if (value == 'community') {
      url = url.split('/users_communities')[0]
      var id=$('.communitySearch').val();
      $.ajax({
        type: "get",
        url: url + '/addcommunityasfavoritefromallusers',
        data:{community:id},
        success: function(res){
          alertify.success("Set favorite from all users.");
        },
        error:function(error)
        {
          alertify.error("Error to set favorite in community.");
        }
      });
    }
  });
});
