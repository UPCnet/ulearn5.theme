(function() {
    'use strict';

    angular
        .module('ulearn.stats')
        .service('ResultsService', ResultsService);

    /**
     * @desc My service returns an object that can hold properties and/or methods.
     *       As an OOP comparision, when using Myservice as a DI, MyService is an
     *       instance of a class (not the class itself).
     *
     *       MyService is a singleton, so any reference to MyService is using
     *       the same class instance across an app.
     */
    /* @nInject */
    function ResultsService($http, $translate, plonePortalURL) {
        var self = this;
        self.show_results = false;
        self.is_drilldown = false;
        self.drilldown_params = {};
        self.search_type = 'activity';
        self.search_options = {
            start: '',
            end: '',
            community: '',
            user: '',
            keywords: []
        };

        self.columns = {
            activity: ['activity', 'comments', 'documents', 'links', 'media'],
            chats: ['active', 'messages'],
            accesses: ['accesses']
        };

        self.search = Search;
        self.buildColumns = buildColumns;
        self.drilldown = DrillDown;

        ////////////////////
        function Search() {
            self.search_options.stats_requested = self.columns[self.search_type];
            return $http.get(
                        plonePortalURL + '/ulearn-stats-query',
                        {params: self.search_options})
                    .then(function(response) {
                        return response.data;})
                    .catch(function () {
                        console.log('Error during the user search');});
        }

        function buildColumns () {
            var columns = [];
            $translate(['STATS.ACTIVITY', 'STATS.COMMENTS', 'STATS.DOCUMENTS', 'STATS.LINKS', 'STATS.MEDIA', 'STATS.ACTIVE', 'STATS.MESSAGES'])
                .then(function (translations) {
                    // var columns = [];
                    angular.forEach(self.columns[self.search_type], function(value){
                        this.push(translations['STATS.'+value.toUpperCase()]);
                    }, columns);
                });
            return columns;
        }

        function DrillDown () {
            return $http.get(
                        plonePortalURL + '/ulearn-stats-query-drilldown',
                        {params: angular.extend({}, self.search_options, self.drilldown_params)})
                    .then(function(response) {
                        return response.data;})
                    .catch(function () {
                        console.log('Error during the user search');});
        }
    }
})();
