import logging
from psycopg2 import IntegrityError
from odoo.tests.common import Form, SavepointCase
from odoo.tests import tagged
_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
class HrHeadquarterTestCase(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(HrHeadquarterTestCase, cls).setUpClass()

        cls.state = cls.env["res.country.state"].create({
            "name": "Estado Prueba",
            "country_id": 3, 
            "code": "EP1",
        })
        cls.city = cls.env["res.country.city"].create({
            "name": "Ciudad Prueba",
            "state_id": cls.state.id,
            "country_id": cls.state.country_id.id,
        })

    def test_headquarter_name_unique_constraint(self):
        """
        Probar que No se puede repetir el nombre de una sede administrativa.
        """
        record = self.env["hr.headquarter"]
        with Form(record) as h:
            h.name = "Sede Prueba 1"
            h.state_id = self.state
            h.city_id = self.city
        with self.assertRaises(IntegrityError):
            with Form(record) as h:
                h.name = "Sede Prueba 1"
                h.state_id = self.state
                h.city_id = self.city
