odoo.define('gymwale.dashboard', function (require) {
    "use strict";

    const AbstractAction = require('web.AbstractAction');
    const core = require('web.core');
    const QWeb = core.qweb;

    const GymwaleDashboard = AbstractAction.extend({
        template: 'gymwale_dashboard_template',

        // Fetch data from the server
        init: function (parent, context) {
            this._super(parent, context);
            this.dashboardData = {}; // Initialize data storage
        },

        // Start method to load the dashboard
        start: function () {
            var self = this;
            this._fetchDashboardData().then(function () {
                self._renderDashboard();
            });
            return this._super();
        },

        // Fetch dashboard data from the server
        _fetchDashboardData: function () {
            var self = this;
            return this._rpc({
                model: 'gymwale.dashboard',
                method: 'compute_total_paid_members',
                args: [],
            }).then(function (result) {
                self.dashboardData = result; // Store result in data storage
            });
        },

        // Render the dashboard with the fetched data
        _renderDashboard: function () {
            const $totalMembers = this.$('#total_members_count');
//            const $totalRevenue = this.$('#total_revenue_count');
//            const $newSignups = this.$('#new_signups_count');

            $totalMembers.text(this.dashboardData.total_members || 0);
//            $totalRevenue.text(this.dashboardData.total_revenue || 0);
//            $newSignups.text(this.dashboardData.new_signups || 0);
        },
    });

    core.action_registry.add('gymwale_dashboard', GymwaleDashboard);

    return GymwaleDashboard;
});
