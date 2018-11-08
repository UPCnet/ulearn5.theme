$(document).ready(function (event) {

  var selector = '#subscribednews-search-box .maxui-text-input';
  $('#subscribednews-search').on('focusin', selector, function(event) {
      event.preventDefault();
      var text = $(this).val();
      var literal = $(this).attr('data-literal');
      var normalized = normalizeWhiteSpace(text, false);
      if (normalized === literal) {
          $(this).val('');
      }
  }).on('keydown', selector, function(event) {
    if (event.which === 13 && $(this).val() !== '') {
        event.preventDefault();
        var literal = $(this).attr('data-literal');
        var text = $(this).val();
        var path = $(this).data().path;
        var normalized = normalizeWhiteSpace(text, false);
        textSearch(normalized);
        $.get(path + '/search_filtered_news', { q: normalized }, function(data) {
          $('.list-search-portlet').html(data);
        });
      }
  });

  $('#subscribednews-search-filters').on('click', '.maxui-close', function(event) {
      event.preventDefault();
      var filter = $(this.parentNode.parentNode);
      var path = $('#subscribednews-search-text').attr('data-path');
      delFilter({
          type: filter.attr('type'),
          value: filter.attr('value')
      });

      var keywords_ls = [];
      var keywords = $('#subscribednews-search-filters .maxui-filter');

      for (var i = 0; i < keywords.length; i++) {
          if (keywords[i].getAttribute('value') === filter.attr('value') & keywords[i].getAttribute('type') === filter.attr('type')) {
              deleted = true;
              keywords.splice(i, 1);
          }
      };

      for (var kw = 0; kw < keywords.length; kw++) {
        keywords_ls.push(keywords[kw].getAttribute('value'));
      };
      var normalized = keywords_ls.join(' ');
      $.get(path + '/search_filtered_news', { q: normalized }, function(data) {
        $('.list-search-portlet').html(data);
      });

  });

  $('#subscribednews-search-filters').on('click', '.add-search-news', function(event) {
    var keywords_ls = [];
    var keywords = $('#subscribednews-search-filters .maxui-filter');
    for (var kw = 0; kw < keywords.length; kw++) {
      keywords_ls.push(keywords[kw].getAttribute('value'));
    };
    var items = keywords_ls.join(',');
    var path = $('#subscribednews-search-text').attr('data-path');
    $.post(path + '/add_user_search', { items: items });
    getSearchers();
    $('#subscribednews-filters-toolbox').html('<a class="remove-search-news" href=""><i class="fa fa-times fa-2" ></i></a>');
  });

  $('#subscribednews-search-filters').on('click', '.remove-search-news', function(event) {
    var keywords_ls = [];
    var keywords = $('#subscribednews-search-filters .maxui-filter');
    for (var kw = 0; kw < keywords.length; kw++) {
      keywords_ls.push(keywords[kw].getAttribute('value'));
    };
    var items = keywords_ls.join(',');
    var path = $('#subscribednews-search-text').attr('data-path');
    $.post(path + '/remove_user_search', { items: items });
    getSearchers();
    $('#subscribednews-search-filters').html('');
    delAllFilters();

    $.get(path + '/search_filtered_news', { q:'' }, function(data) {
      $('.list-search-portlet').html(data);
    });


  });

  $('#searcher_selector').on('change',function(event){

    var text = $(this).val();
    var path = $('#subscribednews-search-text').attr('data-path');
    var normalized = normalizeWhiteSpace(text, false);
    delAllFilters();
    textSearch(normalized);

    $('#subscribednews-search').toggleClass('folded', false);
    $('#subscribednews-search-text').val('');

    $.get(path + '/search_filtered_news', { q: normalized }, function(data) {
      $('.list-search-portlet').html(data);
    });

  });

  var finalActions = function(text) {
    maxui.textSearch(text);
    $('#subscribednews-search').toggleClass('folded', false);
    $('#subscribednews-search-text').val('');
  }

  var normalizeWhiteSpace = function(s, multi) {
      s = s.replace(/(^\s*)|(\s*$)/gi, "");
      s = s.replace(/\n /, "\n");
      var trimMulti = true;
      if (arguments.length > 1) {
          trimMulti = multi;
      }
      if (trimMulti === true) {
          s = s.replace(/[ ]{2,}/gi, " ");
      }
      return s;
  };

  var textSearch = function(text) {
      // Refresh filters
      var maxui = this;
      maxui.filters = []

      var keywords = text.split(' ');
      for (var kw = 0; kw < keywords.length; kw++) {
          var kwtype = 'keyword';
          var keyword = keywords[kw];

          if (keyword.length >= 3) {
              addFilter({
                  type: kwtype,
                  value: keyword
              }, false);
          }
      }
      reloadFilters();
  };

  var getSearchers = function(){
    var path = $('#subscribednews-search-text').attr('data-path');
    var data_array = [];
    $.get(path + '/get_user_searchers', function(data) {
      if (typeof data === 'string' || data instanceof String){
        data_parser = data.replace(/'/g, '"');
        data_array = JSON.parse(data_parser);
      };
      $('#searcher_selector option').remove();
      for (var i = 0; i < data_array.length; i++){
          $('#searcher_selector').append($('<option>', { value : data_array[i] }).text(data_array[i]));
      }

    });
  };


  /**
   *    Prepares a object with the current active filters
   *
   *    @param {String} (optional)    A string containing the id of the last activity loaded
   **/
  var getFilters = function() {
      var maxui = this;
      var params = {
          filters: maxui.filters
      };
      if (params.filters === undefined) {
          params.filters = [];
      }
      var filters = {};
      // group filters
      var enableSearchToggle = false;
      for (var f = 0; f < params.filters.length; f++) {
          var filter = params.filters[f];
          // Enable toggle button only if there's at least one visible filter
          if (filter.visible) {
              enableSearchToggle = true;
          }
          if (!filters[filter.type]) {
              filters[filter.type] = [];
          }
          filters[filter.type].push(filter.value);
      }
      // Accept a optional parameter indicating search start point
      if (arguments.length > 0) {
          filters.before = arguments[0];
      }
      return {
          filters: filters,
          visible: enableSearchToggle
      };
  };


  /**
 *    Reloads the current filters UI and executes the search, optionally starting
 *    at a given point of the timeline
 *
 *    @param {String} (optional)    A string containing the id of the last activity loaded
 **/
var reloadFilters = function() {
    var maxui = this;
    var filters;

    var values = [];
    keywords_ls=[];
    var template = '';
    for (var i = 0; i < maxui.filters.length; i++) {
      template = template + '<div class="maxui-filter maxui-keyword" type="keyword" value="'+maxui.filters[i].value+'"><span>'+maxui.filters[i].value+'<a class="maxui-close" href=""><i class="maxui-icon-cancel-circled" alt="tanca"/></a></span></div>';
      keywords_ls.push(maxui.filters[i].value);
    };
    items = keywords_ls.join(',');
    var path = $('#subscribednews-search-text').attr('data-path');

    $.get(path + '/search_in_searchers', { items: items}, function(data) {
      if(data != 'True'){
        template += '<div id="subscribednews-filters-toolbox"><a class="add-search-news" href=""><i class="fa fa-floppy-o fa-2" ></i></a></div>';
      }
      else{
        template += '<div id="subscribednews-filters-toolbox"><a class="remove-search-news" href=""><i class="fa fa-times fa-2" ></i></a></div>';
      };
      $('#subscribednews-search-filters').html(template);
    });
    // Accept a optional parameter indicating search start point
    if (arguments.length > 0) {
        filters = getFilters(arguments[0]);
    } else {
        filters = getFilters();
    }
    //Enable or disable filter toogle if there are visible filters defined (or not)
    $('#subscribednews-search').toggleClass('folded', !filters.visible);
};
/**
 *    Adds a new filter to the search if its not present
 *    @param {Object} filter    An object repesenting a filter, with the keys "type" and "value"
 **/
var delFilter = function(filter) {
    var maxui = this;
    var deleted = false;
    for (var i = 0; i < maxui.filters.length; i++) {
        if (maxui.filters[i].value === filter.value & maxui.filters[i].type === filter.type) {
            deleted = true;
            maxui.filters.splice(i, 1);
        }
    }
    if (deleted) {
        reloadFilters();
    }
};

var delAllFilters = function() {
    var maxui = this;
    maxui.filters = [];
};

/**
 *    Adds a new filter to the search if its not present
 *    @param {Object} filter    An object repesenting a filter, with the keys "type" and "value"
 **/
var addFilter = function(filter) {
    var maxui = this
    var reload = true;
    //Reload or not by func argument
    if (arguments.length > 1) {
        reload = arguments[1];
    }
    if (!maxui.filters) {
        maxui.filters = [];
    }
    // show filters bu default unless explicitly specified on filter argument
    if (!filter.hasOwnProperty('visible')) {
        filter.visible = true;
    }
    var already_filtered = false;
    for (var i = 0; i < maxui.filters.length; i++) {
        if (maxui.filters[i].value === filter.value & maxui.filters[i].type === filter.type) {
            already_filtered = true;
        }
    }
    if (!already_filtered) {
        maxui.filters.push(filter);
        if (reload === true) {
            reloadFilters();
        }
    }
}

});
