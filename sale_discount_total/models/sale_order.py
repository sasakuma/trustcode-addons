# -*- coding: utf-8 -*-
# © 2017 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api
from odoo.addons import decimal_precision as dp


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    discount_type = fields.Selection(
        [('percent', 'Percentual'),
         ('amount', 'Quantia')],
        string='Tipo de Desconto',
        readonly=True,
        states={'draft': [('readonly', False)],
                'sent': [('readonly', False)]},
        default='percent')

    discount_value = fields.Float(
        string='Desconto',
        readonly=True,
        states={'draft': [('readonly', False)],
                'sent': [('readonly', False)]})

    @api.multi
    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        self.update_discount_lines()
        return res

    @api.multi
    def update_discount_lines(self):
        precision_discount = dp.get_precision('Discount')(self._cr)[1]
        precision_money = dp.get_precision('Product Price')(self._cr)[1]
        for item in self:
            if item.discount_value == 0:
                continue
            discount_percent = round(item.discount_value,
                                     precision_discount)
            if item.discount_type == 'amount':
                discount_percent = round(
                    item.discount_value / item.total_bruto * 100,
                    precision_discount)
            if discount_percent > 100:
                discount_percent = 100
            elif discount_percent < 0:
                discount_percent = 0
            amount = 0
            for line in item.order_line[:-1]:
                line.discount = discount_percent
                amount += round(discount_percent / 100 * line.valor_bruto,
                                precision_money)
            if item.discount_type == 'amount':
                last = item.order_line[-1]
                last.discount = (
                    item.discount_value - amount) / last.valor_bruto * 100
            else:
                item.order_line[-1].discount = discount_percent
