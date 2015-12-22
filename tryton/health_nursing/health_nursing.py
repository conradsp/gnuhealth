# -*- coding: utf-8 -*-
##############################################################################
#
#    GNU Health: The Free Health and Hospital Information System
#    Copyright (C) 2008-2015 Luis Falcon <lfalcon@gnusolidario.org>
#    Copyright (C) 2011-2015 GNU Solidario <health@gnusolidario.org>
#
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import pytz
from trytond.model import ModelView, ModelSQL, ModelSingleton, fields
from datetime import datetime
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.pyson import Eval


__all__ = ['GnuHealthSequences', 'PatientRounding', 'RoundingProcedure',
    'PatientAmbulatoryCare', 'AmbulatoryCareProcedure']


class GnuHealthSequences(ModelSingleton, ModelSQL, ModelView):
    "Standard Sequences for GNU Health"
    __name__ = "gnuhealth.sequences"

    ambulatory_care_sequence = fields.Property(fields.Many2One('ir.sequence',
        'Health Ambulatory Care', domain=[
            ('code', '=', 'gnuhealth.ambulatory_care')
        ]))


# Class : PatientRounding
# Assess the patient and evironment periodically
# Usually done by nurses

class PatientRounding(ModelSQL, ModelView):
    'Patient Rounding'
    __name__ = 'gnuhealth.patient.rounding'

    name = fields.Many2One('gnuhealth.inpatient.registration',
        'Registration Code', required=True)
    health_professional = fields.Many2One('gnuhealth.healthprofessional',
        'Health Professional', readonly=True)
    evaluation_start = fields.DateTime('Start', required=True)
    evaluation_end = fields.DateTime('End', required=True)
    environmental_assessment = fields.Char('Environment', help="Environment"
        " assessment . State any disorder in the room.")

    weight = fields.Integer('Weight', help="Measured weight, in kg")

    # The 6 P's of rounding
    pain = fields.Boolean('Pain', help="Check if the patient is in pain")
    pain_level = fields.Integer('Pain', help="Enter the pain level, from 1 to "
            "10", states={'invisible': ~Eval('pain')})

    potty = fields.Boolean('Potty', help="Check if the patient needs to "
        "urinate / defecate")
    position = fields.Boolean('Position', help="Check if the patient needs to "
        "be repositioned or is unconfortable")
    proximity = fields.Boolean('Proximity', help="Check if personal items, "
        "water, alarm, ... are not in easy reach")
    pump = fields.Boolean('Pumps', help="Check if there is any issues with "
        "the pumps - IVs ... ")
    personal_needs = fields.Boolean('Personal needs', help="Check if the "
        "patient requests anything")

    # Vital Signs
    systolic = fields.Integer('Systolic Pressure')
    diastolic = fields.Integer('Diastolic Pressure')
    bpm = fields.Integer('Heart Rate',
        help='Heart rate expressed in beats per minute')
    respiratory_rate = fields.Integer('Respiratory Rate',
        help='Respiratory rate expressed in breaths per minute')
    osat = fields.Integer('Oxygen Saturation',
        help='Oxygen Saturation(arterial).')
    temperature = fields.Float('Temperature',
        help='Temperature in celsius')

    # Diuresis

    diuresis = fields.Integer('Diuresis',help="volume in ml")
    urinary_catheter = fields.Boolean('Urinary Catheter')

    #Glycemia
    glycemia = fields.Integer('Glycemia', help='Blood Glucose level')

    depression = fields.Boolean('Depression signs', help="Check this if the "
        "patient shows signs of depression")
    evolution = fields.Selection([
        ('n', 'Status Quo'),
        ('i', 'Improving'),
        ('w', 'Worsening'),
        ], 'Evolution', help="Check your judgement of current "
        "patient condition", sort=False)
    round_summary = fields.Text('Round Summary')
    warning = fields.Boolean('Warning', help="Check this box to alert the "
        "supervisor about this patient rounding. A warning icon will be shown "
        "in the rounding list")
    warning_icon = fields.Function(fields.Char('Warning Icon'), 'get_warn_icon')
    procedures = fields.One2Many('gnuhealth.rounding_procedure', 'name',
        'Procedures', help="List of the procedures in this rounding. Please "
        "enter the first one as the main procedure")

    report_start_date = fields.Function(fields.Date('Start Date'), 
        'get_report_start_date')
    report_start_time = fields.Function(fields.Time('Start Time'), 
        'get_report_start_time')
    report_end_date = fields.Function(fields.Date('End Date'), 
        'get_report_end_date')
    report_end_time = fields.Function(fields.Time('End Time'), 
        'get_report_end_time')

    @classmethod
    def __setup__(cls):
        super(PatientRounding, cls).__setup__()
        cls._error_messages.update({
            'health_professional_warning':
                    'No health professional associated to this user',
        })

    @classmethod
    def validate(cls, roundings):
        super(PatientRounding, cls).validate(roundings)
        for rounding in roundings:
            rounding.check_health_professional()

    def check_health_professional(self):
        if not self.health_professional:
            self.raise_user_error('health_professional_warning')

    @staticmethod
    def default_health_professional():
        pool = Pool()
        HealthProf= pool.get('gnuhealth.healthprofessional')
        healthprof = HealthProf.get_health_professional()
        return healthprof

    @staticmethod
    def default_evaluation_start():
        return datetime.now()

    def get_report_start_date(self, name):
        Company = Pool().get('company.company')

        timezone = None
        company_id = Transaction().context.get('company')
        if company_id:
            company = Company(company_id)
            if company.timezone:
                timezone = pytz.timezone(company.timezone)

        dt = self.evaluation_start
        return datetime.astimezone(dt.replace(tzinfo=pytz.utc), timezone).date()

    def get_report_start_time(self, name):
        Company = Pool().get('company.company')

        timezone = None
        company_id = Transaction().context.get('company')
        if company_id:
            company = Company(company_id)
            if company.timezone:
                timezone = pytz.timezone(company.timezone)

        dt = self.evaluation_start
        return datetime.astimezone(dt.replace(tzinfo=pytz.utc), timezone).time()

    def get_report_end_date(self, name):
        Company = Pool().get('company.company')

        timezone = None
        company_id = Transaction().context.get('company')
        if company_id:
            company = Company(company_id)
            if company.timezone:
                timezone = pytz.timezone(company.timezone)

        dt = self.evaluation_end
        return datetime.astimezone(dt.replace(tzinfo=pytz.utc), timezone).date()

    def get_report_end_time(self, name):
        Company = Pool().get('company.company')

        timezone = None
        company_id = Transaction().context.get('company')
        if company_id:
            company = Company(company_id)
            if company.timezone:
                timezone = pytz.timezone(company.timezone)

        dt = self.evaluation_end
        return datetime.astimezone(dt.replace(tzinfo=pytz.utc), timezone).time()

    def get_warn_icon(self, name):
        if self.warning:
            return 'gnuhealth-warning'


class RoundingProcedure(ModelSQL, ModelView):
    'Rounding - Procedure'
    __name__ = 'gnuhealth.rounding_procedure'

    name = fields.Many2One('gnuhealth.patient.rounding', 'Rounding')
    procedure = fields.Many2One('gnuhealth.procedure', 'Code', required=True,
        select=True,
        help="Procedure Code, for example ICD-10-PCS Code 7-character string")
    notes = fields.Text('Notes')


class PatientAmbulatoryCare(ModelSQL, ModelView):
    'Patient Ambulatory Care'
    __name__ = 'gnuhealth.patient.ambulatory_care'

    name = fields.Char('ID', readonly=True)
    patient = fields.Many2One('gnuhealth.patient', 'Patient', required=True)
    base_condition = fields.Many2One('gnuhealth.pathology', 'Base Condition')
    evaluation = fields.Many2One('gnuhealth.patient.evaluation',
        'Related Evaluation', domain=[('patient', '=', Eval('patient'))],
        depends=['patient'])
    ordering_professional = fields.Many2One('gnuhealth.healthprofessional',
        'Ordering Physician')
    health_professional = fields.Many2One('gnuhealth.healthprofessional',
        'Health Professional', readonly=True)
    procedures = fields.One2Many('gnuhealth.ambulatory_care_procedure', 'name',
        'Procedures',
        help="List of the procedures in this session. Please enter the first "
        "one as the main procedure")
    session_number = fields.Integer('Session #')
    session_start = fields.DateTime('Start', required=True)

    # Vital Signs
    systolic = fields.Integer('Systolic Pressure')
    diastolic = fields.Integer('Diastolic Pressure')
    bpm = fields.Integer('Heart Rate',
        help='Heart rate expressed in beats per minute')
    respiratory_rate = fields.Integer('Respiratory Rate',
        help='Respiratory rate expressed in breaths per minute')
    osat = fields.Integer('Oxygen Saturation',
        help='Oxygen Saturation(arterial).')
    temperature = fields.Float('Temperature',
        help='Temperature in celsius')

    warning = fields.Boolean('Warning', help="Check this box to alert the "
        "supervisor about this session. A warning icon will be shown in the "
        "session list")
    warning_icon = fields.Function(fields.Char('Warning Icon'), 'get_warn_icon')

    #Glycemia
    glycemia = fields.Integer('Glycemia', help='Blood Glucose level')

    evolution = fields.Selection([
        ('initial', 'Initial'),
        ('n', 'Status Quo'),
        ('i', 'Improving'),
        ('w', 'Worsening'),
        ], 'Evolution', help="Check your judgement of current "
        "patient condition", sort=False)
    session_end = fields.DateTime('End', required=True)
    next_session = fields.DateTime('Next Session')
    session_notes = fields.Text('Notes')

    @classmethod
    def __setup__(cls):
        super(PatientAmbulatoryCare, cls).__setup__()
        cls._error_messages.update({
            'health_professional_warning':
                    'No health professional associated to this user',
        })
        cls._order.insert(0, ('session_start', 'DESC'))

    @classmethod
    def validate(cls, records):
        super(PatientAmbulatoryCare, cls).validate(records)
        for record in records:
            record.check_health_professional()

    def check_health_professional(self):
        if not self.health_professional:
            self.raise_user_error('health_professional_warning')

    @classmethod
    def create(cls, vlist):
        Sequence = Pool().get('ir.sequence')
        Config = Pool().get('gnuhealth.sequences')

        vlist = [x.copy() for x in vlist]
        for values in vlist:
            if not values.get('name'):
                config = Config(1)
                values['name'] = Sequence.get_id(
                    config.ambulatory_care_sequence.id)
        return super(PatientAmbulatoryCare, cls).create(vlist)

    @staticmethod
    def default_health_professional():
        pool = Pool()
        HealthProf= pool.get('gnuhealth.healthprofessional')
        healthprof = HealthProf.get_health_professional()
        return healthprof

    @staticmethod
    def default_session_start():
        return datetime.now()

    @classmethod
    def copy(cls, ambulatorycares, default=None):
        if default is None:
            default = {}
        default = default.copy()
        default['name'] = None
        default['session_start'] = cls.default_session_start()
        default['session_end'] = cls.default_session_start()
        return super(PatientAmbulatoryCare, cls).copy(ambulatorycares,
            default=default)

    def get_warn_icon(self, name):
        if self.warning:
            return 'gnuhealth-warning'


class AmbulatoryCareProcedure(ModelSQL, ModelView):
    'Ambulatory Care Procedure'
    __name__ = 'gnuhealth.ambulatory_care_procedure'

    name = fields.Many2One('gnuhealth.patient.ambulatory_care', 'Session')
    procedure = fields.Many2One('gnuhealth.procedure', 'Code', required=True,
        select=True,
        help="Procedure Code, for example ICD-10-PCS Code 7-character string")
    comments = fields.Char('Comments')
