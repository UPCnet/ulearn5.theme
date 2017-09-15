(function() {
    'use strict';

    angular
        .module('ulearn.stats')
        .directive('statsinfo', StatsInfoDirective);

    /**
     * @desc This a factory template that returns a function to be instantiated
     *       As an OOP comparison, when using MyFactory as a DI, MyFactory is a
     *       class, that has to be instantiated like MyFactory(param).
     *
     *       MyFactory (the class) is a singlenton, so unique across the app, but
     *       each instance created calling MyFactory will be a new instance.
     */
    /* @nInject */
    function StatsInfoDirective() {
        return {
            restrict: 'E',
            controller: ['$scope', '$element', '$attrs', 'StatsInfo', function($scope, $element, $attrs, StatsInfo) {
                StatsInfo.communities = angular.fromJson($attrs.communities);
                StatsInfo.extended_report = JSON.parse($attrs.extendedReport.toLowerCase());
            }]
        };
    }
})();
