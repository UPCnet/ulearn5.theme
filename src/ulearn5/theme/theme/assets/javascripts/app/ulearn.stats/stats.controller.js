(function() {
    'use strict';

    angular
        .module('ulearn.stats')
        .controller('StatsController', StatsController);

    /**
     * @desc
     */
    /* @nInject */
    function StatsController($state, $translate, $rootScope, moment, StatsInfo, UserService, ResultsService, $window, $httpParamSerializer, plonePortalURL) {
        var self = this;

        self.options = {
            format: 'DD/MM/YYYY',
            startDate: moment().subtract(29, 'days'),
            endDate: moment(),
            minDate: '01/01/2012',
            maxDate: moment(moment().year()+'-12-31'),
            // dateLimit: { days: 60 },
            showDropdowns: true,
            showWeekNumbers: true,
            timePicker: false,
            timePickerIncrement: 1,
            timePicker12Hour: true,
            ranges: {
            },
            drops: 'down',
            buttonClasses: ['btn', 'btn-sm'],
            applyClass: 'btn-primary',
            cancelClass: 'btn-default',
            separator: ' to ',
            locale: {
                applyLabel: 'Submit',
                cancelLabel: 'Cancel',
                fromLabel: 'From',
                toLabel: 'To',
                customRangeLabel: 'Custom',
                daysOfWeek: ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr','Sa'],
                monthNames: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
                firstDay: 1
            },
            activity: 'activity'
        };

        $translate(['STATS.ACTIVITY','STATS.TODAY', 'STATS.YESTERDAY', 'STATS.LAST7DAYS', 'STATS.LAST30DAYS', 'STATS.THISMONTH', 'STATS.LASTMONTH',
                    'COMMON.JANUARY', 'COMMON.FEBRUARY', 'COMMON.MARCH', 'COMMON.APRIL', 'COMMON.MAY', 'COMMON.JUNE', 'COMMON.JULY', 'COMMON.AUGUST', 'COMMON.SEPTEMBER', 'COMMON.OCTOBER', 'COMMON.NOVEMBER', 'COMMON.DECEMBER',
                    'STATS.APPLY', 'STATS.CANCEL', 'STATS.FROM', 'STATS.TO', 'STATS.CUSTOM',
                    'COMMON.SU', 'COMMON.MO', 'COMMON.TU', 'COMMON.WE', 'COMMON.TH', 'COMMON.FR', 'COMMON.SA'])
            .then(function (translations) {
                self.options.ranges[translations['STATS.TODAY']] = [moment(), moment()];
                self.options.ranges[translations['STATS.YESTERDAY']] = [moment().subtract(1, 'days'), moment().subtract(1, 'days')];
                self.options.ranges[translations['STATS.LAST7DAYS']] = [moment().subtract(6, 'days'), moment()];
                self.options.ranges[translations['STATS.LAST30DAYS']] = [moment().subtract(29, 'days'), moment()];
                self.options.ranges[translations['STATS.THISMONTH']] = [moment().startOf('month'), moment().endOf('month')];
                self.options.ranges[translations['STATS.LASTMONTH']] = [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')];

                self.options.locale.monthNames = [translations['COMMON.JANUARY'], translations['COMMON.FEBRUARY'], translations['COMMON.MARCH'], translations['COMMON.APRIL'], translations['COMMON.MAY'], translations['COMMON.JUNE'], translations['COMMON.JULY'], translations['COMMON.AUGUST'], translations['COMMON.SEPTEMBER'], translations['COMMON.OCTOBER'], translations['COMMON.NOVEMBER'], translations['COMMON.DECEMBER']];
                self.options.locale.applyLabel = translations['STATS.APPLY'];
                self.options.locale.cancelLabel = translations['STATS.CANCEL'];
                self.options.locale.fromLabel = translations['STATS.FROM'];
                self.options.locale.toLabel = translations['STATS.TO'];
                self.options.locale.customRangeLabel = translations['STATS.CUSTOM'];

                self.options.locale.daysOfWeek = [translations['COMMON.SU'], translations['COMMON.MO'], translations['COMMON.TU'], translations['COMMON.WE'], translations['COMMON.TH'], translations['COMMON.FR'], translations['COMMON.SA']];

                self.options.activity = translations['STATS.ACTIVITY'].toLowerCase();
            });

        self.principals = [];
        self.availableTags = [];
        self.communities = StatsInfo.communities;
        self.extended_report = StatsInfo.extended_report;
        self.selected_user = '';
        self.selected_tags = [];
        self.startMonth = moment.months(GetInitialMonth(moment().month()));
        self.endMonth = moment.months(moment().month());
        self.startYear = GetInitialYear(moment().month(), moment().year());
        self.endYear = moment().year();
        self.months = moment.months();
        self.years = GenerateYearList();
        self.date = {
            startDate: moment().subtract(29, 'days'),
            endDate: moment()
        };
        self.selected_community = self.communities[0].hash;

        self.refreshUsers = RefreshUsers;
        self.search = Search;
        self.export = Export;
        self.stats = Activities;
        self.chats = Chats;

        /////////////////////////////////////

        function RefreshUsers (query) {
            UserService.search(query).then(function (results) {
                self.principals = results;
            });
        }

        function Search () {
            var currentLocaleData = moment.localeData();
            self.date.startDate = moment({y:self.startYear, M:currentLocaleData.monthsParse(self.startMonth)});
            self.date.endDate = moment({y:self.endYear, M:currentLocaleData.monthsParse(self.endMonth)});
            ResultsService.search_type = $state.current.name.replace('stats.', '');
            ResultsService.search_options.start = self.date.startDate.format('YYYY-MM-DD');
            ResultsService.search_options.end = self.date.endDate.format('YYYY-MM-DD');
            ResultsService.search_options.community = self.selected_community;
            ResultsService.search_options.user = self.selected_user.id;
            ResultsService.search_options.keywords = self.selected_tags;
            ResultsService.show_results = true;
            $rootScope.$emit('results_requested');
        }

        function Export () {
            ResultsService.search_type = $state.current.name;
            ResultsService.search_options.start = self.date.startDate.format('YYYY-MM-DD');
            ResultsService.search_options.end = self.date.endDate.format('YYYY-MM-DD');
            ResultsService.search_options.community = self.selected_community;
            ResultsService.search_options.user = self.selected_user.id;
            ResultsService.search_options.keywords = self.selected_tags;
            ResultsService.search_options.format = 'csv';

            var query = $httpParamSerializer(ResultsService.search_options);
            $window.location = plonePortalURL + '/ulearn-stats-query?' + query;
        }

        function Activities () {
            $window.location = plonePortalURL + '/' + self.options.activity;
        }

        function Chats () {
            $window.location = plonePortalURL + '/chats';
        }

        function GenerateYearList () {
            var year_list = [];
            for (var year = 2012; year <= moment().year() + 1; year++) {
                year_list.push(year);
            };
            return year_list;
        }

        function GetInitialMonth (month) {
            if (month === 0) { return 11; }
            else { return month - 1; }
        }

        function GetInitialYear (month, year) {
            if (month === 0) { return year - 1; }
            else { return year; }
        }
    }
})();
