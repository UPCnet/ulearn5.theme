'use strict';

/**
 * @ngdoc overview
 * @name editACL
 * @description
 * # editACL controller
 * Controls the community edit ACL widget
 */

GenwebApp.value('CommunityInfo', {
    community_url: '',
    community_hash: '',
    community_gwuuid: '',
    community_type: ''
});

GenwebApp.directive('communityinfo', [function() {
    return {
        restrict: 'E',
        controller: ['$scope', '$element', '$attrs', 'CommunityInfo', function($scope, $element, $attrs, CommunityInfo) {
            CommunityInfo.community_url = $attrs.communityUrl;
            CommunityInfo.community_hash = $attrs.communityHash;
            CommunityInfo.community_gwuuid = $attrs.communityGwuuid;
            CommunityInfo.community_type = $attrs.communityType;
        }]
    };
}]);
