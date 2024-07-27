odoo.define('gymwale.dashboard', function (require) {
    "use strict";

    const AbstractAction = require('web.AbstractAction');
    const core = require('web.core');
    const QWeb = core.qweb;

    const GymwaleDashboard = AbstractAction.extend({
        template: 'gymwale_dashboard_template',

        init: function (parent, context) {
            this._super(parent, context);
            this.dashboardData = {};
            console.log("Dashboard initialized");
        },

        start: function () {
            var self = this;
            console.log("Fetching dashboard data...");
            this._fetchDashboardData().then(function () {
                console.log("Data fetched:", self.dashboardData);
                self._renderDashboard();
            });
            return this._super();
        },

        _fetchDashboardData: function () {
            var self = this;
            return this._rpc({
                model: 'gymwale.members',
                method: 'get_dashboard_info',
                args: [],
            }).then(function (result) {
                self.dashboardData = result;
                console.log("Dashboard data received:", result);
            }).catch(function (error) {
                console.error("Error fetching dashboard data:", error);
            });
        },

        _renderDashboard: function () {
            const $total_collection = this.$('#total_collection');
            const $total_paid_members_count = this.$('#total_paid_members_count');
            const $monthly_collection = this.$('#monthly_collection');
            const $total_gym_expense = this.$('#total_gym_expense');
            const $net_collection = this.$('#net_collection');

            $total_collection.text(this.dashboardData.total_collection || 0);
            $total_paid_members_count.text(this.dashboardData.total_paid_members_count || 0);
            $monthly_collection.text(this.dashboardData.monthly_collection || 0);
            $total_gym_expense.text(this.dashboardData.total_gym_expense || 0);
            $net_collection.text(this.dashboardData.net_collection || 0);
            console.log("Dashboard rendered");
        },
    });

    core.action_registry.add('gymwale_dashboard', GymwaleDashboard);

    return GymwaleDashboard;
});
