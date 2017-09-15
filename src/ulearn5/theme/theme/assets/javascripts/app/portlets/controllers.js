'use strict';

/**
 * @ngdoc overview
 * @name editACL
 * @description
 * # editACL controller
 * Controls the community edit ACL widget
 */


GenwebApp.controller('profilePortlet', [function () {
  var self = this;

}]);

GenwebApp.controller('profilePortletModal', ['$scope', '$http', '$timeout', '$window', 'plonePortalURL', 'MAXInfo', 'SweetAlert', '$translate', function ($scope, $http, $timeout, $window, plonePortalURL, MAXInfo, SweetAlert, $translate) {
  $scope.selected = $scope.ngDialogData.community_type;
  $scope.changeCommunityType = function (selected) {
    var data = {community_type: selected};
    $http.put(
      plonePortalURL + '/api/communities/' + $scope.ngDialogData.community_hash,
      data,
      {headers:MAXInfo.headers})
    .success(function() {
      $scope.closeThisDialog();
      $timeout(function () { $window.location.reload(); }, 700);
    })
    .error(function () {
      $translate(['CHANGECOMMUNITYTYPE_VIEW.ERROR'])
        .then(function (translations) {
          SweetAlert.swal({
            title:'Error',
            description: translations['CHANGECOMMUNITYTYPE_VIEW.ERROR'],
            type:'error',
            timer: 2000});
        });
    });
  };

}]);

GenwebApp.controller('homeTopPageMenuButtons', ['ngDialog', function (ngDialog) {
  var self = this;
  self.active_tab = 'stream';

}]);

GenwebApp.controller('homeTopPageMenuButtonsCA', ['ngDialog', '$scope', function (ngDialog, $scope) {
  var self = this;
  self.active_tab = 'stream';
  $scope.filtered_contents_search_ca_view = 'https://farm4.staticflickr.com/3261/2801924702_ffbdeda927_d.jpg';


}]);
