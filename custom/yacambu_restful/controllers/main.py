"""Part of odoo. See LICENSE file for full copyright and licensing details."""
import ast
import functools
import logging

from odoo import http
from odoo.http import request
from odoo.tests.common import Form

from odoo.addons.yacambu_restful.common import (
    extract_arguments,
    non_numeric_id_response,
    invalid_object_model
)

_logger = logging.getLogger(__name__)


def validate_token(func):
    """
    Decorator intended to validate the access token on each request.
    """

    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        """."""
        access_token = request.httprequest.headers.get("access_token")
        if not access_token:
            return {
                "error": "No se ha encontrado el token de acceso en los headers de la petición."
            }
        access_token_data = (
            request.env["api.access_token"].sudo().search([("token", "=", access_token)], order="id DESC", limit=1))

        if access_token_data.find_one_or_create_token(user_id=access_token_data.user_id.id) != access_token:
            return {
                "error": "El token es inválido o ha expirado."
            }

        request.session.uid = access_token_data.user_id.id
        request.uid = access_token_data.user_id.id
        return func(self, *args, **kwargs)

    return wrap


_routes = ["/api/<model>", "/api/<model>/<id>", "/api/<model>/<id>/<action>"]


class APIController(http.Controller):
    def __init__(self):
        self._model = "ir.model"

    @validate_token
    @http.route(_routes, type="json", auth="none", methods=["GET"], csrf=False)
    def get(self, model=None, id=None, **payload):
        try:
            ioc_name = model
            model = request.env[self._model].search([("model", "=", model)], limit=1)            
            if model:
                domain, fields, offset, limit, order = extract_arguments(payload)
                try:
                    _id = int(id) if id else None
                except:
                    return {
                        'error' : "El ID no es de tipo numero"
                    }
                if id:
                    domain = [("id", "=", _id)]                    
                    data = request.env[model.model].search_read(
                        domain=domain, fields=fields, offset=offset, limit=limit, order=order)                    
                else:
                    data = request.env[model.model].search_read(
                        domain=domain, fields=fields, offset=offset, limit=limit, order=order)                                    
            else:
                return invalid_object_model(ioc_name)
            if data:
                return {'msg': "OK", "data":data}
            else:
                return {
                    "error": "No se ha encontrado registro"
                }
        except Exception as e:
            return {"error": e}

    @validate_token
    @http.route("/api/reconcile/<invoice_id>", type="json", auth="none", methods=["POST"], csrf=False)
    def reconcile_invoice_with_client_payments(self, invoice_id=None, **payload):
        if not invoice_id:
            return {
                "error": "Debe pasar el id de la factura como parámetro."
            }
        try:
            id = int(invoice_id)
        except Exception:
            return non_numeric_id_response(invoice_id)
        invoice = request.env["account.move"].search([("id", '=', id)])
        if not invoice:
            return {
                "error": f"No hay facturas con el id {id}."
            }
        if invoice.amount_residual <= 0:
            return {
                "error": f"La factura con el id {id} no tiene saldo pendiente."
            }
        invoice_type = invoice.move_type
        if invoice_type not in ("out_invoice", "in_invoice"):
            return {
                "error": f"El asiento con el id {id} no es una factura."
            }
        partner_type = "supplier" if invoice_type == "in_invoice" else "customer"
        partner = invoice.partner_id
        domain = [("partner_id", '=', partner.id),
                  ("is_reconciled", '=', False),
                  ("partner_type", '=', partner_type)]
        payments = request.env["account.payment"].search(domain, order="date asc")
        if not any(payments):
            return {
                "error": f"{partner.name} no tiene pagos con saldo a favor."
            }
        try:
            for payment in payments:
                if invoice.amount_residual > 0:
                    payment.sudo().payment_invoices(partner.id, id, payment.move_id.id)
                else:
                    break
            msg = "La factura fue conciliada con los pagos satisfactoriamente."
            return { "msg": msg }
        except Exception as e:
            request.env.cr.rollback()
            _logger.warning("EXCEPTION %s",e)
            return { "error": e }

    @validate_token
    @http.route(_routes, type="json", auth="none", methods=["POST"], csrf=False)
    def post(self, model=None, id=None, **payload ):
        import ast
        _logger.info("PAYLOAD 1 %s", payload)
        #pendiente de manera producto por codigo y no id
        ioc_name = model
        model = request.env[self._model].sudo().search([("model", "=", model)], limit=1)
        values = {}
        if model:
            try:
                # changing IDs from string to int.
                for k, v in payload.items():
                    if "__api__" in k:
                        values[k[7:]] = ast.literal_eval(v)
                    else:
                        values[k] = v
                if model.model == 'account.payment':
                    try:
                        partner = request.env["res.partner"].sudo().search_read(
                            [("id", '=', int(values["partner_id"]))])
                        if not bool(partner):
                            return {
                                "msg": "Invalid res.partner id.",
                                "error": f"There is no res.partner record with the id {id}."
                            }
                    except Exception as e:
                        return {"msg": e}
                    if id != None:
                        try:
                            _id = int(id)
                            _logger.info("id 1 %s", _id)
                        except Exception:
                            return non_numeric_id_response(id)
                        _logger.info("PAGO DE FACTURA")
                        try:
                            values['payment_type'] = 'inbound'
                            values['partner_type'] = 'customer'
                            _logger.info(f"journal_id: {values['journal_id']}")

                            # Buscando la factura
                            record = request.env['account.move'].sudo().search_read(
                                [("id", "=", _id)])
                            if not bool(record):
                                return {
                                    "msg": "Invalid account.move id.",
                                    "error": f"There is no account.move record with the id {id}."
                                }
                            _logger.info("Factura %s", record[0])

                            # Si existe el expediente se utiliza su cuenta como la cuenta de destino
                            expediente = request.env['partner.files'].sudo().search([("name", "in", record[0].get('file_id'))], limit=1)
                            _logger.info("Values: %s", values)
                            _logger.info("Expediente")
                            if expediente:
                                _logger.info("Exp %s", expediente)
                                values['destination_account_id'] = expediente.property_account_receivable_id.id
                            _logger.info(model.model)
                            # Creando el pago
                            resource =  request.env[model.model].sudo().create(values)
                            _logger.info("Payment")
                            resource.sudo().action_post()
                            # Buscando el pago
                            payment = request.env[model.model].sudo().search_read([("id", '=', int(resource.id))])
                        
                            move_id = payment[0].get('move_id') #obtengo el move_id
                            invoice_id = record[0].get('id') #obtengo invoice_id
                            partner_id = record[0].get('partner_id') #obtengo partner_id

                            _logger.info(f"Move {move_id}")
                            _logger.info(f"Invoice {invoice_id}")
                            _logger.info(f"Partner {partner_id}")
                            
                            partial = request.env['account.payment'].sudo().payment_invoices(
                                partner_id[0],_id,move_id[0])
                            _logger.warning("partial")
                            _logger.warning(partial)
                            data = resource.sudo().read()
                            _logger.warning("data %s", data)
                            return {
                                "id": resource.id,
                                'msg': "OK",
                                "data": data
                            }
                        except Exception as e:
                            _logger.warning(e)
                            return {"msg": e}
                    else:
                        try:
                            values['payment_type'] = 'inbound'
                            values['partner_type'] = 'customer'
                            _logger.warning(f"journal_id: {values['journal_id']}")

                            _logger.warning("Model")
                            _logger.warning(model.model)
                            # Creando el pago
                            resource =  request.env[model.model].sudo().create(values)
                            _logger.warning("Payment")
                            resource.sudo().action_post()

                            data = resource.sudo().read()
                            _logger.warning("data %s", data)
                            return {
                                "id": resource.id,
                                'msg': "OK",
                                "data": data
                            }
                        except Exception as e:
                            _logger.info(e)
                            return {"msg": e}
                elif model.model == 'res.partner':
                    values['taxpayer'] = "formal"
                    values['type_person_ids'] = 1
                    values['is_company'] = True
                    values['company_type'] = "company"
                    values['lang'] = "es_VE"
                    values['exempt_islr'] = True
                    values['exempt_iva'] = True
                    values['customer_rank'] = 1

                    if "street" not in values or values['street'] is False:
                        return {
                            "error":"Campo dirección requerido.",
                        }
                    if "country_id" not in values or values['country_id'] is False:
                        return {
                            "error":"Campo pais requerido.",
                        }
                    if "state_id" not in values or values['state_id'] is False:
                        return {
                            "error":"Campo estado requerido.",
                        }
                    if "city_id" not in values or values['city_id'] is False:
                        return {
                            "error":"Campo ciudad requerido.",
                        }
                    if "phone" not in values or values['phone'] is False:
                        return {
                            "error":"Campo teléfono requerido.",
                        }
                    if "mobile" not in values or values['mobile'] is False:
                        return {
                            "error":"Campo celular requerido.",
                        }
                    if "email" not in values or values['email'] is False:
                        return {
                            "error":"Campo correo requerido.",
                        }
                    resource = request.env[model.model].sudo().create(values)
                else:
                    _logger.warning("PAYLOAD %s",payload)
                    _logger.warning("VALORES %s",values)
                    _logger.warning("NOMBRE %s", values['name'])
                    _logger.warning("model.model %s",model.model)
                    resource = request.env[model.model].sudo().create(values)
                    _logger.warning("RESOURCE %s",resource)
                
            except Exception as e:
                request.env.cr.rollback()
                _logger.warning("EXCEPTION %s",e)
                return { "msg": e }
            else:
                data = resource.sudo().read()
                if resource:
                    return {
                        "id": resource.id,
                        'msg': "OK",
                        "data": data
                    }
                else:
                    return { 'status': 200, 'msg': "OK" }
        return invalid_object_model(ioc_name)

    @validate_token
    @http.route(_routes, type="json", auth="none", methods=["PUT"], csrf=False)
    def put(self, model=None, id=None, **payload):
        try:
            _id = int(id)
        except Exception as e:
            return non_numeric_id_response(id)
        _model = request.env[self._model].sudo().search([("model", "=", model)], limit=1)
        values = {}
        if not _model:
            return invalid_object_model(model)
        try:
            record = request.env[_model.model].sudo().browse(_id)
            for k, v in payload.items():
                if "__api__" in k:
                    values[k[7:]] = ast.literal_eval(v)
                else:
                    values[k] = v
            record.write(values)
        except Exception as e:
            request.env.cr.rollback()
            return { "msg": e }
        else:
            data = record.sudo().read()
            return { 'msg': "OK", 'data': data }

    @validate_token
    @http.route(_routes, type="json", auth="none", methods=["DELETE"], csrf=False)
    def delete(self, model=None, id=None, **payload):
        try:
            _id = int(id)
        except Exception as e:
            return non_numeric_id_response(id)
        try:
            record = request.env[model].sudo().search([("id", "=", _id)])
            if record:
                record.unlink()
            else:
                return {
                    "msg": "Missing Record.",
                    "error": f"Record object with id {_id} could not be found."
                }
        except Exception as e:
            request.env.cr.rollback()
            return { "msg": e }
        else:
            return {
                "msg": f"{model} Model record with id {record.id} has been successfully deleted."
            }

    @validate_token
    @http.route(_routes, type="json", auth="none", methods=["PATCH"], csrf=False)
    def patch(self, model=None, id=None, action=None, **payload):
        if action:
            action = action 
        else:
             if payload.get("_method"):
                action = payload.get("_method")
        args = []
        _logger.info("action 1 %s", action)
        try:
            _id = int(id)
            _logger.info("id 1 %s", _id)
        except Exception as e:
            return non_numeric_id_response(id)
        try:
            record = request.env[model].sudo().search([("id", "=", _id)])
            _logger.info("record 1 %s", record)
            _callable = action in [method for method in dir(record) if callable(getattr(record, method))]
            _logger.info("callable 1 %s", _callable)
            if record and _callable:
                # action is a dynamic variable.
                getattr(record, action)(*args) if args else getattr(record, action)() 
            else:
                return {
                    "msg": "Missing Record.",
                    "error": "Record object with id {_id} could not be found or {model} object has no method {action}"
                }
        except Exception as e:
            return {
                "msg": e
            }
        else:
            return { 'msg': "OK", 'id': record.id }

    @validate_token
    @http.route("/api/<model>/expediente/<id>", type="json", auth="none", methods=["PUT"], csrf=False)
    def put_exp(self, model=None, id=None, **payload):
        try:
            _id = str(id)
        except Exception as e:
            return { "msg": e }
        _model = request.env[self._model].sudo().search([("model", "=", model)], limit=1)
        values = {}
        if not _model:
            return invalid_object_model(model)
        try:
            record = request.env[_model.model].sudo().search([("name", "=", _id)], limit=1)
            for k, v in payload.items():
                if "__api__" in k:
                    values[k[7:]] = ast.literal_eval(v)
                else:
                    values[k] = v
            record.write(values)
        except Exception as e:
            request.env.cr.rollback()
            return { "msg": e }
        else:
            data = record.sudo().read()
            return { 'msg': "OK", 'data': data }

    @validate_token
    @http.route("/api/<model>/expediente/<id>", type="json", auth="none", methods=["DELETE"], csrf=False)
    def delete_exp(self, model=None, id=None, **payload):
        try:
            _id = str(id)
        except Exception as e:
            return { "msg": e }
        try:
            record = request.env[model].sudo().search([("name", "=", _id)])
            if record:
                record.unlink()
            else:
                return {
                    "msg": "Missing Record.",
                    "error": f"Record object with partner.file id {_id} could not be found."
                }
        except Exception as e:
            request.env.cr.rollback()
            return { "msg": e }
        else:
            return {
                "msg": "Record has been successfully deleted."
            }
