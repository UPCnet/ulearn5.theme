(function() {
    'use strict';

    angular
        .module('ulearn.stats')
        .controller('StatsModalController', StatsModalController);

    /**
     * @desc
     */
    /* @nInject */
    function StatsModalController(StatsModalFactory, ResultsService) {
        var self = this;
        self.close = StatsModalFactory.deactivate;

        ResultsService.drilldown().then(function (response) {
            self.drilldown = response.results;
        });
    }
})();
