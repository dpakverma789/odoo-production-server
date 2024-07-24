odoo.define('GymWale_CRM.gymwale_dashboard', function (require) {
    "use strict";

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');

    var gymwale_dashboard = AbstractAction.extend({
        template: 'GymWale_CRM.gymwale_dashboard_template',

        init: function (parent, context) {
            this._super(parent, context);
            this.context = context || {};
        },

        start: function () {
            var self = this;
            return this._super().then(function () {
                self.render_dashboard();
            });
        },

        render_dashboard: function () {
            // Your custom dashboard rendering logic
            console.log("Dashboard is rendered!");
        },
    });

    core.action_registry.add('gymwale_dashboard_tag', gymwale_dashboard);

    return gymwale_dashboard;
});
