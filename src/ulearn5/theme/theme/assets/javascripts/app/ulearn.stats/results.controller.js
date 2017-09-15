(function() {
    'use strict';

    angular
        .module('ulearn.stats')
        .controller('ResultsController', ResultsController);

    /**
     * @desc
     */
    /* @nInject */
    function ResultsController($rootScope, ResultsService, StatsModalFactory) {
        var self = this;
        self.show = false;
        self.results = {};

        self.show_modal = ShowModal;

        $rootScope.$on('results_requested', ShowResults);
        $rootScope.$on('$stateChangeStart', ChangeTab);

        function ShowResults () {
            self.show = ResultsService.show_results;
            self.column_headers = ResultsService.buildColumns();
            ResultsService.search().then(function (response) {
                self.results = response.rows;
            });
        }

        function ShowModal (params) {
            ResultsService.is_drilldown = true;
            ResultsService.drilldown_params = params;
            StatsModalFactory.activate();
        }

        function ChangeTab () {
            ResultsService.show_results = false;
            self.show = false;
        }
    }
})();
