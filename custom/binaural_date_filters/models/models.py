import collections
import datetime
import dateutil
import dateutil.relativedelta
import pytz

from odoo import api
from odoo.models import BaseModel


@api.model
def _read_group_process_groupby(self, gb, query):
    """
        Helper method to collect important information about groupbys: raw
        field name, type, time information, qualified name, ...
    """
    split = gb.split(':')
    field = self._fields.get(split[0])
    if not field:
        raise ValueError("Invalid field %r on model %r" % (split[0], self._name))
    field_type = field.type
    gb_function = split[1] if len(split) == 2 else None
    temporal = field_type in ('date', 'datetime')
    tz_convert = field_type == 'datetime' and self._context.get('tz') in pytz.all_timezones
    qualified_field = self._inherits_join_calc(self._table, split[0], query)
    if temporal:
        display_formats = {
            'hour': 'HH:mm dd MMM yyyy',
            'day': 'dd MMM yyyy',  # yyyy = normal year
            'week': "'W'w YYYY",  # w YYYY = ISO week-year
            'month': 'MMMM yyyy',
            'quarter': 'QQQ yyyy',
            'third': 'QQQ yyyy',
            'year': 'yyyy',
        }
        time_intervals = {
            'hour': dateutil.relativedelta.relativedelta(hours=1),
            'day': dateutil.relativedelta.relativedelta(days=1),
            'week': datetime.timedelta(days=7),
            'month': dateutil.relativedelta.relativedelta(months=1),
            'quarter': dateutil.relativedelta.relativedelta(months=3),
            'third': dateutil.relativedelta.relativedelta(months=4),
            'year': dateutil.relativedelta.relativedelta(years=1),
        }
        if tz_convert:
            qualified_field = "timezone('%s', timezone('UTC',%s))" % (self._context.get('tz', 'UTC'), qualified_field)
        if gb_function == "third":
            qualified_field_time_conditional = f"""
                (CASE 
                 WHEN EXTRACT(MONTH FROM {qualified_field}::timestamp) = 4 THEN {qualified_field}::timestamp - interval '1 month'
                 WHEN EXTRACT(MONTH FROM {qualified_field}::timestamp) = 7 THEN {qualified_field}::timestamp - interval '1 month'
                 WHEN EXTRACT(MONTH FROM {qualified_field}::timestamp) = 8 THEN {qualified_field}::timestamp - interval '2 months'
                 WHEN EXTRACT(MONTH FROM {qualified_field}::timestamp) = 10 THEN {qualified_field}::timestamp - interval '1 month'
                 WHEN EXTRACT(MONTH FROM {qualified_field}::timestamp) = 11 THEN {qualified_field}::timestamp - interval '2 months'
                 WHEN EXTRACT(MONTH FROM {qualified_field}::timestamp) = 12 THEN {qualified_field}::timestamp - interval '3 months'
                 ELSE {qualified_field}::timestamp
                 END)
            """
            qualified_field = "date_trunc('%s', %s::timestamp)" % ('quarter', qualified_field_time_conditional)
        else:
            qualified_field = "date_trunc('%s', %s::timestamp)" % (gb_function or 'month', qualified_field)
    if field_type == 'boolean':
        qualified_field = "coalesce(%s,false)" % qualified_field
    return {
        'field': split[0],
        'groupby': gb,
        'type': field_type,
        'display_format': display_formats[gb_function or 'month'] if temporal else None,
        'tz_convert': tz_convert,
        'interval': time_intervals[gb_function or 'month'] if temporal else None,
        'qualified_field': qualified_field
    }

BaseModel._read_group_process_groupby = _read_group_process_groupby
