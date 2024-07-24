
from odoo import http
from odoo.http import request


class ControllerName(http.Controller):

    @http.route('<url path>', type='http', website=True, auth='public')
    def function_name(self):
        return request.render('module_name.template_name')
