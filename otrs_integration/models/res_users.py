# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import requests
import json
from odoo import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    otrs_login = fields.Char('Login OTRS')
    otrs_password = fields.Char('Senha OTRS')

    def otrs_post(self, route, data):
        headers = {'Content-Type': 'application/json'}
        domain = self.get_otrs_domain(self.company_id.otrs_webservice_domain,
                                      route)
        data = json.dumps(data)
        return requests.post(url=domain, headers=headers, data=data)

    def otrs_get(self, route):
        return requests.get(url=self.get_otrs_domain(
            self.company_id.otrs_webservice_domain, route))

    def otrs_patch(self, route, data):
        headers = {'Content-Type': 'application/json'}
        data = json.dumps(data)
        return requests.patch(url=self.get_otrs_domain(
            self.company_id.otrs_webservice_domain, route),
            headers=headers, data=data)

    def otrs_search(self, route, data):
        data = json.dumps(data)
        return requests.get(url=self.get_otrs_domain(
            self.company_id.otrs_webservice_domain, route),
            data=data)

    def get_otrs_domain(self, domain, route):
        return '{}/{}?UserLogin={}&Password={}'.format(
            domain, route, self.otrs_login, self.otrs_password)