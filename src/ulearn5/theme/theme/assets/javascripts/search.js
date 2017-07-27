require([
  'expect',
  'jquery'
], function(expect, $) {
  $(document).ready(function() {
    var lang = $('html').attr('lang');
    $("select.custom-select2").select2({
      width: 'resolve',
      placeholder: function () {
        if (lang == 'ca') {
          $('#news_link').text('Més notícies a la sala de premsa...');
          return 'Cerca a la sala de premsa...';
        }
        else if (lang == 'es') {
          $('#news_link').text('Más noticias a la sala de prensa...');
          return 'Busca en la sala de prensa...';
        }
        else if (lang == 'en') {
          $('#news_link').text('More news at press room...');
          return 'Search at press room...';
        }
        else {
          $('#news_link').text('Més notícies a la sala de premsa...');
          return 'Cerca a la sala de premsa...';
        }
      }
    });
    $("select.custom-select2").on('change', function() {
      window.location = this.value;
      $(this).empty();
    });
    $(".custom-select2").on("click", function() {
      $('.select2-results li:last-child').attr('style', 'font-weight: 500');
    });
  });
});
