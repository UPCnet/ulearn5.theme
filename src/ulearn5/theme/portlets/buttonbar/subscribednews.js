$(document).ready(function () {

  var selector = '#subscribednews-search-box .maxui-text-input';
  
  // Focus in event handler
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
        if($('#searcher_selector option[value="' + normalized + '"]').length > 0){
          $('#searcher_selector').val(normalized);
        } else {
          $('#searcher_selector').val($('#searcher_selector option:first-child').text());
        }
        $.get(path + '/search_filtered_news', { q: normalized }, function(data) {
          $('.list-search-portlet').html(data);
        });
    }
  });

  // Remove filter handler
  $('#subscribednews-search-filters').on('click', '.maxui-close', function(event) {
      event.preventDefault();
      var filter = $(this).closest('.maxui-filter');
      var path = $('#subscribednews-search-text').attr('data-path');
      delFilter({
          type: filter.attr('type'),
          value: filter.attr('value')
      });

      var keywords_ls = [];
      var keywords = $('#subscribednews-search-filters .maxui-filter');

      keywords.each(function() {
          if ($(this).attr('value') !== filter.attr('value') || $(this).attr('type') !== filter.attr('type')) {
              keywords_ls.push($(this).attr('value'));
          }
      });

      var normalized = keywords_ls.join(' ');
      $.get(path + '/search_filtered_news', { q: normalized }, function(data) {
        $('.list-search-portlet').html(data);
      });
      if ($('#searcher_selector').val(normalized).val() == null) {
        $('#searcher_selector').val($('#searcher_selector option:first-child').text());
      }
      $('#subscribednews-search-text').val(normalized);
  });

  // Add search news handler
  $('#subscribednews-search-filters').on('click', '.add-search-news', function(event) {
    var keywords_ls = [];
    var keywords = $('#subscribednews-search-filters .maxui-filter');
    keywords.each(function() {
      keywords_ls.push($(this).attr('value'));
    });
    var items = keywords_ls.join(',');
    var path = $('#subscribednews-search-text').attr('data-path');
    $.post(path + '/add_user_search', { items: items }, function(data){
      getSearchers(data);
      $('#searcher_selector').val($('#searcher_selector option:last-child').text());
      $('#subscribednews-filters-toolbox').html('<a class="remove-search-news" href=""><i class="fa fa-trash fa-2" ></i></a>');
    });
  });

  // Remove search news handler
  $('#subscribednews-search-filters').on('click', '.remove-search-news', function(event) {
    var keywords_ls = [];
    var keywords = $('#subscribednews-search-filters .maxui-filter');
    keywords.each(function() {
      keywords_ls.push($(this).attr('value'));
    });
    var items = keywords_ls.join(',');
    var path = $('#subscribednews-search-text').attr('data-path');
    $.post(path + '/remove_user_search', { items: items }, function(data){
      delAllFilters();
      getSearchers(data);
    });

    $.get(path + '/search_filtered_news', { q:'' }, function(data) {
      $('.list-search-portlet').html(data);
    });
  });

  // Searcher selector change handler
  $('#searcher_selector').on('change',function(event){
    var text = $(this).val();
    var path = $('#subscribednews-search-text').attr('data-path');
    var normalized = normalizeWhiteSpace(text, false);
    delAllFilters();
    textSearch(normalized);

    $('#subscribednews-search').removeClass('folded');
    $('#subscribednews-search-text').val($("#searcher_selector").val());

    $.get(path + '/search_filtered_news', { q: normalized }, function(data) {
      $('.list-search-portlet').html(data);
    });
  });

  // Normalize white spaces
  var normalizeWhiteSpace = function(s, multi) {
      s = s.replace(/(^\s*)|(\s*$)/gi, "");
      s = s.replace(/\n /, "\n");
      var trimMulti = multi === undefined ? true : multi;
      if (trimMulti) {
          s = s.replace(/[ ]{2,}/gi, " ");
      }
      return s;
  }

  // Text search functionality
  var textSearch = function(text) {
      maxui.filters = []
      var keywords = text.split(' ');
      keywords.forEach(function(keyword) {
          if (keyword.length >= 3) {
              addFilter({
                  type: 'keyword',
                  value: keyword
              }, false);
          }
      });
      reloadFilters();
  }

  // Get searchers after POST request
  var getSearchers = function(data){
    var data_array = [];
    if (typeof data === 'string'){
        data_array = JSON.parse(data.replace(/'/g, '"'));
    }
    $('#searcher_selector option').remove();
    $('#searcher_selector').html('<option disabled="disabled" value="Cerca...">Cerca...</option>');
    $('#searcher_selector').val($('#searcher_selector option:first-child').text());
    data_array.forEach(function(item) {
        $('#searcher_selector').append($('<option>', { value : item }).text(item));
    });
  }

  // Reload current filters and UI
  var reloadFilters = function() {
      var filters = getFilters();
      $('#subscribednews-search').toggleClass('folded', !filters.visible);

      var template = '';
      maxui.filters.forEach(function(filter) {
        template += `<div class="maxui-filter maxui-keyword" type="keyword" value="${filter.value}">
                       <span>${filter.value}<a class="maxui-close" href=""><i class="maxui-icon-cancel-circled" alt="tanca"/></a></span>
                     </div>`;
      });
      var path = $('#subscribednews-search-text').attr('data-path');
      var keywords_ls = maxui.filters.map(function(filter) { return filter.value; }).join(',');

      $.get(path + '/search_in_searchers', { items: keywords_ls}, function(data) {
        if (data !== 'True') {
          template += '<div id="subscribednews-filters-toolbox"><a class="add-search-news" href=""><i class="fa fa-floppy-o fa-2" ></i></a></div>';
        } else {
          template += '<div id="subscribednews-filters-toolbox"><a class="remove-search-news" href=""><i class="fa fa-trash fa-2" ></i></a></div>';
        }
        $('#subscribednews-search-filters').html(template);
      });
  }

  // Get active filters
  var getFilters = function() {
      var filters = {};
      var enableSearchToggle = false;
      maxui.filters.forEach(function(filter) {
          if (filter.visible) {
              enableSearchToggle = true;
          }
          if (!filters[filter.type]) {
              filters[filter.type] = [];
          }
          filters[filter.type].push(filter.value);
      });
      return { filters: filters, visible: enableSearchToggle };
  }

  // Delete individual filter
  var delFilter = function(filter) {
      var deleted = false;
      for (var i = 0; i < maxui.filters.length; i++) {
          if (maxui.filters[i].value === filter.value && maxui.filters[i].type === filter.type) {
              maxui.filters.splice(i, 1);
              deleted = true;
              break;
          }
      }
      if (deleted) {
          reloadFilters();
      }
  }

  // Delete all filters
  var delAllFilters = function() {
      maxui.filters = [];
      $('#subscribednews-search-filters').html('');
      $('#subscribednews-search-text').val('');
  }

  // Add new filter
  var addFilter = function(filter) {
      var reload = true;
      if (maxui.filters.every(function(existingFilter) { return existingFilter.value !== filter.value || existingFilter.type !== filter.type; })) {
          maxui.filters.push(filter);
          if (reload) {
              reloadFilters();
          }
      }
  }
});
