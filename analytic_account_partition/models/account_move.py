# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.multi
    def post(self):
        for line in self.line_ids:
            line._create_partition_move_lines(
                line.analytic_account_id.partition_id)
        return super(AccountMove, self).post()


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def update_partition_move_line(self, credit, debit,
                                   app_line):
        if app_line.type == 'percent':
            self.update({
                'credit': (credit * app_line.partition_percent
                        / 100),
                'debit': (debit * app_line.partition_percent /
                        100),
                'analytic_account_id': app_line.analytic_account_id,
                })
        else:
            self.update({
                'credit': credit,
                'debit': debit,
                'analytic_account_id': app_line.analytic_account_id,
                })
        return self.credit, self.debit

    def _create_partition_move_lines(self, partition_group):
        if not partition_group:
            return
        initial_credit = credit = self.credit
        initial_debit = debit = self.debit
        balance_line = False
        move_lines = []
        for app_line in partition_group.partition_line_ids:
            if app_line.type == 'balance':
                balance_line = app_line
                continue
            if app_line.analytic_account_id == self.analytic_account_id:
                move_line = self
            else:
                move_line = self.copy()
            new_credit, new_debit = move_line.update_partition_move_line(
                    initial_credit, initial_debit, app_line)
            credit -= new_credit
            debit -= new_debit
            move_lines.append(move_line)
        if not balance_line:
            raise UserError('O grupo de rateio %s não contém linha de Saldo'
                            % partition_group.name)
        if balance_line.analytic_account_id == self.analytic_account_id:
            move_line = self
        else:
            move_line = self.copy()
        move_line.update_partition_move_line(credit, debit, balance_line)
        move_lines.append(move_line)
        return move_lines
