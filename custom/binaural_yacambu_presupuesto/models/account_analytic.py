from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    account_budget_post_ids = fields.Many2many(
        "account.budget.post", string="Situaciones presupuestarias", store=True,
        compute="_compute_budget_post_ids", search="_search_account_budget_post_ids")

    file_id = fields.Many2one(
        "partner.files", string="Expediente", readonly=False)
        # related="move_id.move_id.file_id", store=True)
    modality_id = fields.Many2one(
        "partner.files.modality", string="Modalidad", readonly=False)
        # related="move_id.move_id.file_id.modality_id", store=True)

    @api.depends("move_id", "general_account_id")
    def _compute_budget_post_ids(self):
        for line in self:
            line.account_budget_post_ids = []
            if line.general_account_id:
                for budget in line.general_account_id.account_budget_post_ids:
                    line.account_budget_post_ids += budget

    def _search_account_budget_post_ids(self, operator, value):
        for line in self:
            recs = line.search([]).filtered(
                lambda x: x.account_budget_post_ids.mapped("name") == value)
            return [('id', operator, [x.id for x in recs] if recs else False)]

    # @api.depends("move_id")
    # def _compute_modality_id(self):
    #     for line in self:
    #         if line.move_id:
    #             line.modality_id = line.move_id.move_id.file_id.modality_id
    #         else:
    #             line.modality_id = None

    # @api.depends("move_id")
    # def _compute_file_id(self):
    #     for line in self:
    #         if line.move_id:
    #             line.file_id = line.move_id.move_id.file_id
    #         else:
    #             line.file_id = None


class AccountAccount(models.Model):
    _inherit = "account.account"

    account_budget_post_ids = fields.Many2many("account.budget.post", "account_budget_rel", "account_id", "budget_id",
                                               string="Situaciones presupuestarias", store=True)
