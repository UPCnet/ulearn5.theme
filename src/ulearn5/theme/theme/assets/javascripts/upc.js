// habilita tooltips i popover de bootstrap
$(function () { $('[data-toggle="tooltip"]').tooltip() })
$(function () {
    $('[data-toggle="popover"]').popover({
        html: true,
        trigger: "click",
    })
    $('[data-toggle="popover"]').on('click', function (e) {
        $('[data-toggle="popover"]').not(this).popover('hide');
    });
})

$(document).ready(function () {

    // javascript per al canvi de mes al portlet de calendari
    rebind_portlet_calendar();

    function load_portlet_calendar(event, elem) {
        // depends on plone_javascript_variables.js for portal_url
        event.preventDefault();
        var pw = elem.closest('.portletWrapper');
        var elem_data = elem.data();
        var portlethash = pw.attr('id');
        portlethash = portlethash.substring(15, portlethash.length);
        url = portal_url +
            '/@@render-portlet?portlethash=' + portlethash +
            '&year=' + elem_data.year +
            '&month=' + elem_data.month;
        $.ajax({
            url: url,
            success: function (data) {
                pw.html(data);
                rebind_portlet_calendar();
            }
        });
    }

    function rebind_portlet_calendar() {
        // ajaxify each portletCalendar
        $('.portletCalendar a.calendari-seguent').click(function (event) {
            load_portlet_calendar(event, $(this));
        });
        $('.portletCalendar a.calendari-anterior').click(function (event) {
            load_portlet_calendar(event, $(this));
        });
        $('.portletCalendar dd a[title]').tooltip({
            offset: [-10, 0],
            tipClass: 'pae_calendar_tooltip'
        });
        try {
            $('[rel="popover"]').popover();
        } catch (e) {
            console.log('This instance seems that doesn\'t have bootstrap.popover loaded')
        }
        // Prevent click on calendar events to allow popover
        $('.cal_has_events').click(function (event) {
            event.preventDefault();
            $('.popover-content').off('click').on('click', 'a', function () {
                window.location = this.href;
            });

        });
    }

    var isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry/i.test(navigator.userAgent) ? true : false;
    // mostra el focus només amb teclat perquè no li cal a qui usa mouse
    $("body").on("mousedown", "*", function (e) {
        remove_outline(this);
    });

    function remove_outline(element) {
        if ($(element).css("outline-style") == "none") {
            $(element).css("outline-style", "none").on("blur", function () {
                $(element).off("blur").css("outline-style", "");
            });
        }
    };

    // activar funcionament intro en els menus desplegables
    $(".dropdown-toggle").dropdown();

    // menú principal amb hover, modifica default de bootstrap
    $('li.dropdown').hover(function () {
        $(this).find('.dropdown-toggle').attr("aria-expanded", "true");
        $(this).find('.dropdown-menu').stop(true, true).delay(200).fadeIn(500);
    }, function () {
        $(this).find('.dropdown-toggle').attr("aria-expanded", "false");
        $(this).find('.dropdown-menu').stop(true, true).delay(200).fadeOut(500);
    });
    $('button.btn.btn-default.dropdown-toggle').click(function () {
        $(this).find('.dropdown-toggle').attr("aria-expanded", "true");
        $(this).find('.dropdown-menu').stop(true, true).delay(200).fadeIn(500);
    }, function () {
        $(this).find('.dropdown-toggle').attr("aria-expanded", "false");
        $(this).find('.dropdown-menu').stop(true, true).delay(200).fadeOut(500);
    });

    // vista mòbil. Dos botons es mostren i s'amagen amb el menú
    $('.button-menu-mobile a').on("click touchstart", function (e) {
        $(".global-navigation").addClass("open");
        $("body").css({
            "transform": "translateX(calc(-100vw + 105px))",
            "transition": ".25s all ease",
            "overflow": "hidden"
        });
        $(".button-menu-mobile").hide();
        $(".button-menu-mobile--close").show();
        e.preventDefault();
    });
    $('.button-menu-mobile--close a').on("click touchstart", function (e) {
        $(".global-navigation").removeClass("open");
        $("body").css({
            "transform": "translateX(0)",
            "transition": ".25s all ease",
            "overflow": "auto"
        });
        $(".button-menu-mobile--close").hide();
        $(".button-menu-mobile").show();
        e.preventDefault();
    });

    // fallback per a usar object-fit en bàners i capçalera i evitar backgrounds. Afegir la classe compat-object-fit on hi hagi el recurs de object-fit a les CSS
    // Execute this if IE is detected.
    function msieversion() {
        if (!Modernizr.objectfit) {
            $('.header-presentation, .content-highlighted, .hotnews-image, .event-img, .btn-banner').each(function () {
                // hero, 5 destacats...
                var $container = $(this),
                    imgUrl = $container.find('img').prop('src');
                if (imgUrl) {
                    $container.css('backgroundImage', 'url(' + imgUrl + ')').addClass('compat-object-fit');
                }
            });

            $('.section-recerca .list-top-stories a').each(function () {
                // dos destacats rodons a home
                var $container = $(this),
                    imgUrl = $container.find('img').prop('src');
                if (imgUrl) {
                    $container.find('img').hide();
                    $container.prepend('<span class="compat-object-fit" style="background-image:url(' + imgUrl + ');"></span>');
                }
            });

            $('.hotnews-regular ').each(function () {
                // noticies dins sala de premsa
                var $container = $(this),
                    imgUrl = $container.find('img').prop('src');
                if (imgUrl) {
                    $container.find('img').hide();
                    $container.prepend('<div class="compat-object-fit" style="background-image:url(' + imgUrl + ');"></div>');
                }
            });
        }
    } // End

    $(document).ready(msieversion);

    // manage visits cookies
    function getCookie(c_name) {
        var c_value = document.cookie;
        var c_start = c_value.indexOf(" " + c_name + "=");
        if (c_start == -1) c_start = c_value.indexOf(c_name + "=");
        if (c_start == -1) c_value = null;
        else {
            c_start = c_value.indexOf("=", c_start) + 1;
            var c_end = c_value.indexOf(";", c_start);
            if (c_end == -1) c_end = c_value.length;
            c_value = unescape(c_value.substring(c_start, c_end));
        }
        return c_value;
    }

    function setCookie(c_name, value, exdays) {
        var exdate = new Date();
        exdate.setDate(exdate.getDate() + exdays);
        var c_value = escape(value) + ((exdays == null) ? "" : "; expires=" + exdate.toUTCString());
        document.cookie = c_name + "=" + c_value;
    }

    if (getCookie('cookieAccepted') != "1") {
        $("#dialogTitle").css("display", "block");
    } else {
        $("#dialogTitle").css("display", "none");
    }

    $("#dialogClose").click(function () {
        setCookie('cookieAccepted', '1', 365);
        $("#dialogTitle").css("display", "none");
    });

    fields = $("[class$='field']");
    for (var i = 0; i < fields.length; i++) {
        if (fields[i].type == 'submit' || fields[i].type == 'button' || fields[i].type == 'reset') {
            $(fields[i]).addClass('btn btn-default pull-right');
        } else if (fields[i].className != 'schemaeditor-delete-field') {
            $(fields[i]).addClass('form-control');
        }
    }

    // canvia el titol del modal imatge pel peu de foto
    $('.pat-plone-modal').click(function () {
        var titol = $(this).parent().find('.hotnews-description').text().trim();
        if (titol !== '') {
            $('.plone-modal-title').text(titol);
        }
    });

    $(document).on("scroll", function () {
        if ($(document).scrollTop() > 100) {
            $("#portal-header").addClass("shrink");
        } else {
            $("#portal-header").removeClass("shrink");
        }
    });


    // Process per enviar convocatòria en els esdeveniments
    $('#NotAttendeesMsg').hide();

    if ($('#SendInvitation').length) {
        var attendants = $('.attendee').map(function () {
            return $.trim($(this).text());
        }).get()

        if (attendants.length <= 0) {
            $('#SendInvitation').remove();
            $('#NotAttendeesMsg').show();
        }
    }

    $('#SendInvitation').on('click', function () {
        dexterity_url = $(this).attr('data-dexterityUrl');
        $.ajax({
            type: 'POST',
            url: dexterity_url + '/event_to_attendees',
            success: function () {}
        });
    });
}); //ready
