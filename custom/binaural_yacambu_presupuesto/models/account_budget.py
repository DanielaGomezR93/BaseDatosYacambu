from odoo import api, fields, models


class CrossoveredBudget(models.Model):
    _inherit = "crossovered.budget"

    currency_id = fields.Many2one("res.currency", related="company_id.currency_id")
    available_amount = fields.Monetary(
        compute="_compute_available_amount", string="Disponible", store=True)
    has_been_transfered = fields.Boolean(string="¿Se ha realizado una transferencia de este presupuesto?", default=False)

    @api.depends("crossovered_budget_line")
    def _compute_available_amount(self):
        for budget in self:
            budget.available_amount = 0
            budget.available_amount += sum(budget.crossovered_budget_line.mapped("available_amount"))
    
    def action_transfer_wizard(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Transferencia de presupuesto",
            "res_model": "crossovered.budget.transfer.wizard",
            "target": "new",
            "view_id": self.env.ref("binaural_yacambu_presupuesto.view_crossovered_budget_transfer_wizard").id,
            "view_mode": "form",
            "context": {
                "default_origin_budget_id": self.id,
                "default_user_id": self.env.uid,
            }
        }

class CrossoveredBudgetLines(models.Model):
    _inherit = "crossovered.budget.lines"

    variation = fields.Monetary(
        compute="_compute_variation", string="Variación", store=True)
    variation_percentage = fields.Float(
        compute="_compute_variation_percentage", string="% de variación", store=True)
    available_amount = fields.Monetary(
        compute="_compute_available_amount", string="Disponible", store=True)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        # overrides the default read_group in order to compute the computed fields manually for the group

        fields_list = {'practical_amount', 'theoritical_amount', 'percentage'}

        # Not any of the fields_list support aggregate function like :sum
        def truncate_aggr(field):
            field_no_aggr = field.split(':', 1)[0]
            if field_no_aggr in fields_list:
                return field_no_aggr
            return field
        fields = {truncate_aggr(field) for field in fields}

        # Read non fields_list fields
        result = super(CrossoveredBudgetLines, self).read_group(
            domain, list(fields - fields_list), groupby, offset=offset,
            limit=limit, orderby=orderby, lazy=lazy)

        # Populate result with fields_list values
        if fields & fields_list:
            for group_line in result:

                # initialise fields to compute to 0 if they are requested
                if 'practical_amount' in fields:
                    group_line['practical_amount'] = 0
                if 'theoritical_amount' in fields:
                    group_line['theoritical_amount'] = 0
                if 'variation' in fields:
                    group_line['variation'] = 0
                if 'available_amount' in fields:
                    group_line['available_amount'] = 0
                if 'variation_percentage' in fields:
                    group_line['variation_percentage'] = 0
                if 'percentage' in fields:
                    group_line['percentage'] = 0
                    group_line['practical_amount'] = 0
                    group_line['theoritical_amount'] = 0

                domain = group_line.get('__domain') or domain
                all_budget_lines_that_compose_group = self.search(domain)

                for budget_line_of_group in all_budget_lines_that_compose_group:
                    if 'practical_amount' in fields or 'percentage' in fields:
                        group_line['practical_amount'] += budget_line_of_group.practical_amount

                    if 'theoritical_amount' in fields or 'percentage' in fields:
                        group_line['theoritical_amount'] += budget_line_of_group.theoritical_amount

                    if 'variation' in fields:
                        group_line['variation'] += budget_line_of_group.variation
                        
                    if 'available_amount' in fields:
                        group_line['available_amount'] += budget_line_of_group.available_amount

                    if 'variation_percentage' in fields:
                        if group_line['planned_amount']:
                            group_line['variation_percentage'] = float(
                                (group_line['variation'] or 0.0) / (group_line['planned_amount'] * 100))

                    if 'percentage' in fields:
                        if group_line['theoritical_amount']:
                            # use a weighted average
                            group_line['percentage'] = float(
                                (group_line['practical_amount'] or 0.0) / group_line['theoritical_amount'])

        return result
  
    @api.depends("planned_amount", "practical_amount")
    def _compute_variation(self):
        for budget_line in self:
            if budget_line.practical_amount == 0:
                budget_line.variation = 0
            else:
                budget_line.variation = abs(budget_line.planned_amount - budget_line.practical_amount)

    @api.depends("variation", "planned_amount")
    def _compute_variation_percentage(self):
        for budget_line in self:
            budget_line.variation_percentage = 0
            if budget_line.planned_amount and budget_line.planned_amount > 0:
                budget_line.variation_percentage = budget_line.variation / (budget_line.planned_amount * 100)

    @api.depends("variation")
    def _compute_available_amount(self):
        for budget_line in self:
            available_amount = budget_line.planned_amount - budget_line.practical_amount
            budget_line.available_amount = available_amount if available_amount > 0 else 0
