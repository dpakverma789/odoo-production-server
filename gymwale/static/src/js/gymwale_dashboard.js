odoo.define('gymwale.dashboard', function (require) {
    "use strict";

    const AbstractAction = require('web.AbstractAction');
    const core = require('web.core');
    const QWeb = core.qweb;
    const session = require('web.session');
    const _t = core._t;


    const GymwaleDashboard = AbstractAction.extend({
        template: 'gymwale_dashboard_template',
        jsLibs: ['/web/static/lib/Chart/Chart.js'],

        init: function (parent, context) {
            this._super(parent, context);
            this.dashboardData = {};
            this.dateFilter = '';  // Default filter
            this.startDate = null;
            this.endDate = null;
            console.log("Dashboard initialized");
        },

        start: function () {
            var self = this;
            console.log("Fetching dashboard data...");
            this._bindEvents();
            this._fetchDashboardData().then(function () {
                console.log("Data fetched:", self.dashboardData);
                self._renderDashboard();
                self._renderChart();
            });
            return this._super();
        },

        _bindEvents: function () {
            var self = this;

            this.$('#date_filter').on('change', function () {
                self.dateFilter = $(this).val();
                self._updateDateControls();
            });

            this.$('#apply_filter').on('click', function () {
                self.startDate = self.$('#start_date').val();
                self.endDate = self.$('#end_date').val();
                self._fetchDashboardData().then(function () {
                    self._renderDashboard();
                    self._renderChart();
                });
            });

            this.$('#start_date, #end_date').on('change', function () {
                if (self.dateFilter === 'custom_range') {
                    self.startDate = self.$('#start_date').val();
                    self.endDate = self.$('#end_date').val();
                }
            });
        },

        _updateDateControls: function () {
            if (this.dateFilter === 'custom_range') {
                this.$('#custom_range_controls').show();
            } else {
                this.$('#custom_range_controls').hide();
                this.startDate = null;
                this.endDate = null;
            }
        },

        _fetchDashboardData: function () {
            var self = this;
            return this._rpc({
                model: 'gymwale.members',
                method: 'get_dashboard_info',
                args: [self.dateFilter, self.startDate, self.endDate],
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

        _renderChart: function () {
            const ctx = this.$('#paid_members_chart')[0].getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: this.dashboardData.months || [],
                    datasets: [{
                        label: _t('Paid Members'),
                        data: this.dashboardData.values || [],
                        borderColor: '#000',
                        backgroundColor: '#ffa500',
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: _t('Months')
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: _t('Number of Members')
                            }
                        }
                    }
                }
            });
        },
    });

    core.action_registry.add('gymwale_dashboard', GymwaleDashboard);

    return GymwaleDashboard;
});
