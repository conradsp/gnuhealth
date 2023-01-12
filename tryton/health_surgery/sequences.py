# SPDX-FileCopyrightText: 2008-2023 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2023 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# GNU Health HMIS sequences for this package

from trytond.model import (ModelSQL, ValueMixin, fields)
from trytond import backend
from trytond.pyson import Id
from trytond.pool import Pool, PoolMeta
from trytond.tools.multivalue import migrate_property

# Sequences
surgery_code_sequence = fields.Many2One(
    'ir.sequence', 'Surgery code sequence', required=True,
    domain=[('sequence_type', '=', Id(
        'health', 'seq_type_gnuhealth_surgery_code'))])


# GNU HEALTH SEQUENCES
class GnuHealthSequences(metaclass=PoolMeta):
    'Standard Sequences for GNU Health'
    __name__ = 'gnuhealth.sequences'

    surgery_code_sequence = fields.MultiValue(
        surgery_code_sequence)

    @classmethod
    def default_surgery_code_sequence(cls, **pattern):
        pool = Pool()
        ModelData = pool.get('ir.model.data')
        try:
            return ModelData.get_id('health_surgery',
                                    'seq_gnuhealth_surgery_code')
        except KeyError:
            return None


class _ConfigurationValue(ModelSQL):

    _configuration_value_field = None

    @classmethod
    def __register__(cls, module_name):
        exist = backend.TableHandler.table_exist(cls._table)

        super(_ConfigurationValue, cls).__register__(module_name)

        if not exist:
            cls._migrate_property([], [], [])

    @classmethod
    def _migrate_property(cls, field_names, value_names, fields):
        field_names.append(cls._configuration_value_field)
        value_names.append(cls._configuration_value_field)
        migrate_property(
            'gnuhealth.sequences', field_names, cls, value_names,
            fields=fields)


class SurgeryCodeSequence(_ConfigurationValue, ModelSQL, ValueMixin):
    'Health Service Request Sequence setup'
    __name__ = 'gnuhealth.sequences.surgery_code_sequence'
    surgery_code_sequence = surgery_code_sequence
    _configuration_value_field = 'surgery_code_sequence'

    @classmethod
    def check_xml_record(cls, records, values):
        return True
