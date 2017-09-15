(function() {
    'use strict';

    angular
        .module('ulearn.stats')
        .factory('StatsModalFactory', StatsModalFactory);

    /**
     * @desc This a factory template that returns a function to be instantiated
     *       As an OOP comparison, when using MyFactory as a DI, MyFactory is a
     *       class, that has to be instantiated like MyFactory(param).
     *
     *       MyFactory (the class) is a singlenton, so unique across the app, but
     *       each instance created calling MyFactory will be a new instance.
     */
    /* @nInject */
    function StatsModalFactory (vModal) {
        return vModal({
            controller: 'StatsModalController',
            controllerAs: 'statsmodal',
            templateUrl: '++ulearn++app/ulearn.stats/templates/stats.modal.html'
        });
    }
})();
