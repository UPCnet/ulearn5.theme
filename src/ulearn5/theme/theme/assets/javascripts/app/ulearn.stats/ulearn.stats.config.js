(function() {
    'use strict';

    angular
        .module('ulearn.stats')
        .config(config);

    /**
     * @desc
     */
    /* @nInject */
    function config($stateProvider, $urlRouterProvider) {
        $stateProvider
            .state('stats', {
              url: '/stats',
              templateUrl: '++ulearn++app/ulearn.stats/templates/stats.html',
              controller: 'StatsController as statsctrl',
              resolve: {
                hiderightportlets: function(){
                      angular.element('#angular-route-view').siblings().hide()
                      angular.element('#home-angular-route-view').parent().parent().find('> * > *').hide()
                      angular.element('.homepage-hpm4').hide()
                      angular.element('.homepage-hpm3').addClass('span12')
                      angular.element('.homepage-hpm3').removeClass('span8')
                      return;
                  }
              },
            })
            .state('stats.activity', {
              url: '/activity',
              templateUrl: '++ulearn++app/ulearn.stats/templates/activity.html',
              controller: 'StatsController as statsctrl'
            })
            .state('stats.chats', {
              url: '/chats',
              templateUrl: '++ulearn++app/ulearn.stats/templates/chats.html',
              controller: 'StatsController as statsctrl'
            });
    }
})();
