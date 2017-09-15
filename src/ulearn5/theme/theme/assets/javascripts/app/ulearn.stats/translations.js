(function() {
    'use strict';

    angular
        .module('ulearn.stats')
        .config(config);

    /**
     * @desc
     */
    /* @nInject */
    function config($translateProvider) {
        $translateProvider.translations('en', {
            'COMMON': {
                'JANUARY': 'January',
                'FEBRUARY': 'February',
                'MARCH': 'March',
                'APRIL': 'April',
                'MAY': 'May',
                'JUNE': 'June',
                'JULY': 'July',
                'AUGUST': 'August',
                'SEPTEMBER': 'September',
                'OCTOBER': 'October',
                'NOVEMBER': 'November',
                'DECEMBER': 'December',
                'SU': 'Su',
                'MO': 'Mo',
                'TU': 'Tu',
                'WE': 'We',
                'TH': 'Th',
                'FR': 'Fr',
                'SA': 'Sa'
            },
            'STATS': {
                'TITLE': 'Stats',
                'RESULTSTITLE': 'Results',
                'SAVE': 'Save',
                'FIND': 'Find',
                'ACTIVITY': 'Activity',
                'CHATS': 'Chats',
                'ACCESSES': 'Accesses',
                'TODAY': 'Today',
                'YESTERDAY': 'Yesterday',
                'LAST7DAYS': 'Last 7 days',
                'LAST30DAYS': 'Last 30 days',
                'THISMONTH': 'This month',
                'LASTMONTH': 'Last month',
                'APPLY': 'Submit',
                'CANCEL': 'Cancel',
                'FROM': 'From ',
                'TO': 'To ',
                'CUSTOM': 'Custom',
                'SEARCHUSERS': 'Search user',
                'INTERVAL': 'Dates interval',
                'COMMUNITY': 'Community',
                'USER': 'User',
                'TAGS': 'Tags',
                'COMMENTS': 'Comments',
                'DOCUMENTS': 'Documents',
                'LINKS': 'Links',
                'MEDIA': 'Media',
                'RESULTDETAIL': 'Result detail',
                'ACTIVE': 'Active chats',
                'MESSAGES': 'Messages',
                'STARTDATE': 'Start date',
                'ENDDATE': 'End date',
                'EXPORT': 'Export',
                'CANCELA': 'Cancel',
                'INFO': 'Daily Information'
            }
        });

        $translateProvider.translations('es', {
            'COMMON': {
                'JANUARY': 'Enero',
                'FEBRUARY': 'Febrero',
                'MARCH': 'Marzo',
                'APRIL': 'Abril',
                'MAY': 'Mayo',
                'JUNE': 'Junio',
                'JULY': 'Julio',
                'AUGUST': 'Agosto',
                'SEPTEMBER': 'Septiembre',
                'OCTOBER': 'Octubre',
                'NOVEMBER': 'Noviembre',
                'DECEMBER': 'Diciembre',
                'SU': 'Do',
                'MO': 'Lu',
                'TU': 'Ma',
                'WE': 'Mi',
                'TH': 'Ju',
                'FR': 'Vi',
                'SA': 'Sa'
            },
            'STATS': {
                'TITLE': 'Estadísticas',
                'RESULTSTITLE': 'Resultados',
                'SAVE': 'Guardar',
                'FIND': 'Busca',
                'ACTIVITY': 'Actividad',
                'CHATS': 'Chats',
                'ACCESSES': 'Accesos',
                'TODAY': 'Hoy',
                'YESTERDAY': 'Ayer',
                'LAST7DAYS': 'Últimos 7 días',
                'LAST30DAYS': 'Últimos 30 días',
                'THISMONTH': 'Este mes',
                'LASTMONTH': 'El último mes',
                'APPLY': 'Aplicar',
                'CANCEL': 'Cancelar',
                'FROM': 'Desde ',
                'TO': 'A ',
                'CUSTOM': 'Personalizado',
                'SEARCHUSERS': 'Buscar usuario',
                'INTERVAL': 'Intervalo de fechas',
                'COMMUNITY': 'Comunidad',
                'USER': 'Usuario',
                'TAGS': 'Palabras clave',
                'COMMENTS': 'Comentarios',
                'DOCUMENTS': 'Documentos',
                'LINKS': 'Enlaces',
                'MEDIA': 'Media',
                'RESULTDETAIL': 'Detalle de resultados',
                'ACTIVE': 'Chats activos',
                'MESSAGES': 'Mensajes',
                'STARTDATE': 'Fecha de inicio',
                'ENDDATE': 'Fecha de fin',
                'EXPORT': 'Exporta',
                'CANCELA': 'Cancela',
                'INFO': 'Acceso a información diaria'
            }
        });

        $translateProvider.translations('ca', {
            'COMMON': {
                'JANUARY': 'Gener',
                'FEBRUARY': 'Febrer',
                'MARCH': 'Març',
                'APRIL': 'Abril',
                'MAY': 'Maig',
                'JUNE': 'Juny',
                'JULY': 'Juliol',
                'AUGUST': 'Agost',
                'SEPTEMBER': 'Setembre',
                'OCTOBER': 'Octubre',
                'NOVEMBER': 'Novembre',
                'DECEMBER': 'Desembre',
                'SU': 'Dg',
                'MO': 'Dl',
                'TU': 'Dm',
                'WE': 'Dc',
                'TH': 'Dj',
                'FR': 'Dv',
                'SA': 'Ds'
            },
            'STATS': {
                'TITLE': 'Estadístiques',
                'RESULTSTITLE': 'Resultats',
                'SAVE': 'Desa',
                'FIND': 'Busca',
                'ACTIVITY': 'Activitat',
                'CHATS': 'Xats',
                'ACCESSES': 'Accessos',
                'TODAY': 'Avui',
                'YESTERDAY': 'Ahir',
                'LAST7DAYS': 'Els últims 7 dies',
                'LAST30DAYS': 'Last 30 days',
                'THISMONTH': 'This month',
                'LASTMONTH': 'Last month',
                'APPLY': 'Aplica',
                'CANCEL': 'Cancel·la',
                'FROM': 'Des de ',
                'TO': 'Fins a ',
                'CUSTOM': 'Personalitzat',
                'SEARCHUSERS': 'Cerca usuari',
                'INTERVAL': 'Interval de dates',
                'COMMUNITY': 'Comunitat',
                'USER': 'Usuari',
                'TAGS': 'Paraula/es clau',
                'COMMENTS': 'Comentaris',
                'DOCUMENTS': 'Documents',
                'LINKS': 'Enllaços',
                'MEDIA': 'Media',
                'RESULTDETAIL': 'Detall de resultats',
                'ACTIVE': 'Xats actius',
                'MESSAGES': 'Missatges',
                'STARTDATE': 'Data d\'inici',
                'ENDDATE': 'Data de fi',
                'EXPORT': 'Exporta',
                'CANCELA': 'Cancel·la',
                'INFO': 'Accés a informació diària'
            }
        });
        // $translateProvider.preferredLanguage('en');
        $translateProvider.determinePreferredLanguage(function () {
            return angular.element('html').attr('lang');
        });
    }
})();
