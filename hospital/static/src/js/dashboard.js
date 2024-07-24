odoo.define('hospital.dashboard', function (require){
"use strict";

var AbstractAction = require('web.AbstractAction');
var core = require('web.core');
var rpc = require('web.rpc');

var hospital_dashboard = AbstractAction.extend({
    template: 'hospital_dashboard_view',

    patient_count : function(){
            var patient_count = rpc.query({
                model: 'hospital.appointment',
                method: 'total_patient'
            }).then(function (result) {
                $('.patient').innerHTML = result;
            });
        }
    });

core.action_registry.add('hospital_dashboard', hospital_dashboard);
return hospital_dashboard;
});