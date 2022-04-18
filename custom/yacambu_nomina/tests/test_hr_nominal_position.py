import logging
from psycopg2 import IntegrityError
from odoo.tests.common import Form, SavepointCase
from odoo.tests import tagged
_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
class HrNominalPositionTestCase(SavepointCase):

    def test_headquarter_name_unique_constraint(self):
        """
        Probar que No se pueden repetir los datos de un cargo nominal.
        """
        record = self.env["hr.nominal.position"]
        with Form(record) as h:
            h.name = "Cargo Prueba 1"
        with self.assertRaises(IntegrityError):
            with Form(record) as h:
                h.name = "Cargo Prueba 1"
