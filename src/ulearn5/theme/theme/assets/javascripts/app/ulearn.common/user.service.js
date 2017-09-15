(function() {
    'use strict';

    angular
        .module('ulearn.stats')
        .service('UserService', UserService);

    /**
     * @desc My service returns an object that can hold properties and/or methods.
     *       As an OOP comparision, when using Myservice as a DI, MyService is an
     *       instance of a class (not the class itself).
     *
     *       MyService is a singleton, so any reference to MyService is using
     *       the same class instance across an app.
     */
    /* @nInject */
    function UserService($http, plonePortalURL) {
        this.search = Search;

        ////////////////////
        function Search(query) {
          return $http.get(
                        plonePortalURL + '/max.ajaxusersearch',
                        {params: {q: query}})
                    .then(function(response) {
                        return response.data.results;})
                    .catch(function () {
                        console.log('Error during the user search');});
        }
    }
})();
