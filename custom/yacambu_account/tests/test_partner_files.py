import logging
from odoo.tests.common import Form, SavepointCase
from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged
from odoo.tools import float_compare
_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
class HagusClisseTestCase(SavepointCase):

    @classmethod
    def setUpClass(self):
        super(HagusClisseTestCase, self).setUpClass()

        self.accounts = [
            self.env["account.account.template"].create({
                "code": "Acc1",
                "name": "Test Account number 1",
                "user_type_id": 1,
            }),
            self.env["account.account.template"].create({
                "code": "Acc2",
                "name": "Test Account number 2",
                "user_type_id": 2,
            }),
        ]
        self.modalities = [
            self.env["partner.files.modality"].create({
                "name": "Mod Prueba",
                "property_account_receivable_id": self.accounts[0].id,
                "property_account_payable_id": self.accounts[1].id,
            })
        ]

    def test_modality_creation_with_invalid_accounts(self):
        """
        Probar que no se pueda crear una modalidad cuyas cuentas que sean por
        cobrar o por pagar tengan un tipo distinto al que les corresponde.
        """
        with self.assertRaises(ValidationError):
            self.env["partner.files.modality"].create({
                "name": "Mod Prueba",
                "property_account_payable_id": self.env["account.account.template"].create({
                    "code": "Acc Prueba 2",
                    "name": "Test Account with invalid data",
                    "user_type_id": 1,
                }).id,
                "property_account_receivable_id": self.env["account.account.template"].create({
                    "code": "Acc Prueba 2",
                    "name": "Test Account with valid data",
                    "user_type_id": 1,
                }).id,
            })
        with self.assertRaises(ValidationError):
            self.env["partner.files.modality"].create({
                "name": "Mod Prueba",
                "property_account_payable_id": self.env["account.account.template"].create({
                    "code": "Acc Prueba 2",
                    "name": "Test Account with valid data",
                    "user_type_id": 2,
                }).id,
                "property_account_receivable_id": self.env["account.account.template"].create({
                    "code": "Acc Prueba 2",
                    "name": "Test Account with invalid data",
                    "user_type_id": 2,
                }).id,
            })

    def test_modality_write_with_invalid_data(self):
        """
        Probar que una modalidad se guarda cuando se crea 
        """
        modality = self.modalities[0]
        with self.assertRaises(ValidationError):
            modality.write({
                "property_account_receivable_id": self.env["account.account.template"].create({
                    "code": "Acc Prueba 2",
                    "name": "Test Account with invalid data",
                    "user_type_id": 2,
                }).id,
            })
        with self.assertRaises(ValidationError):
            modality.write({
                "property_account_payable_id": self.env["account.account.template"].create({
                    "code": "Acc Prueba 2",
                    "name": "Test Account with invalid data",
                    "user_type_id": 1,
                }).id,
            })
