

from datetime import datetime
import random
import re
import string

from odoo import api, fields, models
from odoo.exceptions import ValidationError


DATETIME_FORMAT = '%d/%m/%Y %H:%M:%S'
COMPUTE_PATTERN = (
    r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2} \+ \d+\.\d{2}$'
)


class ExtensionSaleOrder(models.Model):
    _inherit = 'sale.order'

    responsible_for_issuing = fields.Many2one(
        'hr.employee',
        string='Ответственный за выдачу товара',
        required=True
    )
    new_field = fields.Char(
        string='New Field',
        compute='_compute_date_and_total',
        store=True
    )
    temp_field = fields.Boolean(
        string='Temporary',
        store=False,
        default=True
    )

    def _generate_random_string(self, lengtn=10):
        letters = string.ascii_letters
        result = ''
        for _ in range(lengtn):
            result += random.choice(letters)
        return result

    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        defaults['new_field'] = self._generate_random_string()
        return defaults

    @api.depends('date_order', 'amount_total')
    def _compute_date_and_total(self):
        for record in self:
            if record.date_order and record.order_line:
                if record.new_field:
                    if (
                        re.match(
                            COMPUTE_PATTERN,
                            record.new_field
                        )
                        or record.temp_field
                    ):
                        record.temp_field = False
                        date = datetime.strftime(
                            record.date_order,
                            DATETIME_FORMAT
                        )
                        record.new_field = (
                            f'{date} + {record.amount_total:.2f}'
                        )

    @api.constrains('new_field')
    def _check_string_length(self):
        for record in self:
            if record.new_field:
                if len(record.new_field) > 30:
                    raise ValidationError(
                        'Длина текста должна быть меньше 30 символов!'
                    )
