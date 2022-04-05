from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from odoo.tools import float_compare, date_utils, email_split, email_re
from odoo.tools.misc import formatLang, format_date, get_lang

import logging
_logger = logging.getLogger(__name__)


class PartnerFiles(models.Model):
    _name = "partner.files"
    _description = "Expediente"

    name = fields.Char(string='ID de Expediente',)
    modality_id = fields.Many2one("partner.files.modality", string="Modalidad", required=True)
    state = fields.Selection([
        ('activo', 'Activo'),
        ('cancelado', 'Cancelado'),
        ('concluido', 'Concluido'),
        ('jubiliado', 'Jubiliado'),
        ('graduando', 'Graduando')
    ], string='Estado')
    partner_id = fields.Many2one(
        'res.partner', string="Estudiante", tracking=True)
    property_account_receivable_id = fields.Many2one(
        'account.account', related="modality_id.property_account_receivable_id", store=True)
    property_account_payable_id = fields.Many2one(
        'account.account', related="modality_id.property_account_payable_id", store=True)

    def write(self, vals):
        res = super().write(vals)
        if self.partner_id.file_ids[-1].id == self.id:
            self.partner_id.write({
                "property_account_receivable_id": self.modality_id.property_account_receivable_id.id,
                "property_account_payable_id": self.modality_id.property_account_payable_id.id})
            return res


class Modality(models.Model):
    _name = "partner.files.modality"
    _description = "Modalidad"

    name = fields.Char(string="Modalidad")
    partner_files_ids = fields.One2many("partner.files", "modality_id")
    property_account_receivable_id = fields.Many2one(
        'account.account',
        string='Cuenta por cobrar',
        domain=[("user_type_id", '=', 1)],
        required=True)
    property_account_payable_id = fields.Many2one(
        'account.account',
        string='Cuenta por pagar',
        domain=[("user_type_id", '=', 2)],
        required=True)

    @api.model
    def create(self, vals):
        res = super().create(vals)
        self._check_accounts(this=res)
        return res

    def write(self, vals):
        res = super().write(vals)
        self._check_accounts(this=self)
        for file in self.partner_files_ids:
            file.write({
                "property_account_receivable_id": self.property_account_receivable_id.id,
                "property_account_payable_id": self.property_account_payable_id.id})
        return res

    def _check_accounts(self, this):
        """Verificar que las cuentas tienen el tipo correspondiente."""
        if (bool(this.property_account_receivable_id)
                and this.property_account_receivable_id.user_type_id.id != 1) \
            or (bool(this.property_account_payable_id)
                and this.property_account_payable_id.user_type_id.id) != 2:
            raise ValidationError(
                "Una de las cuentas no tiene el tipo correspondiente.")

    @api.onchange("property_account_receivable_id")
    def _onchange_property_account_receivable_id(self):
        if bool(self.property_account_receivable_id) and \
                self.property_account_receivable_id.user_type_id.id != 1:
            raise ValidationError(
                "La cuenta de este campo debe ser de tipo Por Cobrar.")

    @api.onchange("property_account_payable_id")
    def _onchange_property_account_payable_id(self):
        if bool(self.property_account_payable_id) and \
                self.property_account_payable_id.user_type_id.id != 2:
            raise ValidationError(
                "La cuenta de este campo debe ser de tipo Por Pagar.")


class PartnerPartnerFiles(models.Model):
    _inherit = "res.partner"

    file_ids = fields.One2many(
        'partner.files', 'partner_id', string="Expedientes")

    @api.onchange("file_ids")
    def _onchange_file_ids(self):
        self.property_account_receivable_id = self.file_ids[-1].property_account_receivable_id if any(self.file_ids) else None
        self.property_account_payable_id = self.file_ids[-1].property_account_payable_id if any(self.file_ids) else None


class InvoicePartnerFiles(models.Model):
    _inherit = "account.move"

    file_id = fields.Many2one('partner.files', string="Expedientes", domain="[('partner_id', '=', partner_id)]")
