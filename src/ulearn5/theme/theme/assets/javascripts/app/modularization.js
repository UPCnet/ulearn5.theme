// External modularization
(function() {
    'use strict';

    angular
        .module('underscore', [])
        .value('_', window._);

})();

(function() {
    'use strict';

    angular
        .module('ploneVariables', [])
        .value('plonePortalURL', window.portal_url);

})();

(function() {
    'use strict';

    angular
        .module('momentjs', [])
        .value('moment', window.moment);

})();
