import fhir as supermod
from flask import url_for
from operator import attrgetter
import sys

class DiagnosticReport_Map:
    model_mapping={
            'gnuhealth.lab': {
                'subject': 'patient',
                'performer': 'pathologist',
                'conclusion': 'results', #or diagnosis?
                'codedDiagnosis': 'diagnosis',
                'result': 'critearea',
                'date': 'date_analysis',
                'code': 'test.code',
                'name': 'test.name'}
                }
    url_prefixes={'gnuhealth.lab': 'labreport'}
    search_mapping={}

class health_DiagnosticReport(supermod.DiagnosticReport, DiagnosticReport_Map):
    def __init__(self, *args, **kwargs):
        rec = kwargs.pop('gnu_record', None)
        field = kwargs.pop('field', None)
        super(health_DiagnosticReport, self).__init__(*args, **kwargs)
        if rec:
            self.set_gnu_diagnostic_report(rec, field)

    def set_gnu_diagnostic_report(self, diagnostic_report, field):
        self.diagnostic_report = diagnostic_report
        self.field = field
        self.model_type = self.diagnostic_report.__name__

        # Only certain models
        if self.model_type not in self.model_mapping:
            raise ValueError('Not a valid model')

        self.map = self.model_mapping[self.model_type]
        self.search_prefix=self.url_prefixes[self.model_type]

        self.__import_from_gnu_diagnostic_report()

    def __import_from_gnu_diagnostic_report(self):
        if self.diagnostic_report:
            self.__set_gnu_identifier()
            self.__set_gnu_result()
            self.__set_gnu_performer()
            self.__set_gnu_subject()
            self.__set_gnu_name()
            self.__set_gnu_issued()
            self.__set_gnu_conclusion()
            self.__set_feed_info()

    def __set_gnu_identifier(self):
        if self.diagnostic_report:
            obj, patient, time = attrgetter(self.map['name'], self.map['subject'], self.map['date'])(self.diagnostic_report)

            if obj and patient and time:
                label = '{0} for {1} on {2}'.format(obj, patient.name.rec_name, time.strftime('%Y/%m/%d'))
                value = url_for('diagnostic_report_endpoint.record', log_id=(self.search_prefix, self.diagnostic_report.id, self.field))
                ident = supermod.Identifier(
                            label=supermod.string(value=label),
                            value=supermod.string(value=value))
                self.set_identifier(ident)

    def __set_feed_info(self):
        ''' Sets the feed-relevant info
        '''
        if self.diagnostic_report:
            self.feed={'id': self.diagnostic_report.id,
                    'published': self.diagnostic_report.create_date,
                    'updated': self.diagnostic_report.write_date or self.diagnostic_report.create_date,
                    'title': self.diagnostic_report.rec_name
                        }

    def __set_gnu_name(self):
        if self.diagnostic_report:
            conc = supermod.CodeableConcept()
            conc.coding=[supermod.Coding()]
            conc.coding[0].display=supermod.string(value=attrgetter(self.map['name'])(self.diagnostic_report))
            conc.coding[0].code = supermod.code(value=attrgetter(self.map['code'])(self.diagnostic_report))
            self.set_name(conc)

    def __set_gnu_issued(self):
        if self.diagnostic_report:
            try:
                time=attrgetter(self.map['date'])(self.diagnostic_report)
                instant = supermod.instant(value=time.strftime("%Y-%m-%dT%H:%M:%S"))
                self.set_issued(instant)
            except:
                # If there is no date attached, this report is either not done
                #  or useless
                raise ValueError('No date')

    def __set_gnu_result(self):
        if self.diagnostic_report:
            for test in attrgetter(self.map['result'])(self.diagnostic_report):
                uri = url_for('observation_endpoint.record', log_id=('lab', test.id))
                display = test.rec_name
                ref=supermod.ResourceReference()
                ref.display = supermod.string(value=display)
                ref.reference = supermod.string(value=uri)
                self.add_result(ref)

    def __set_gnu_performer(self):
        if self.diagnostic_report:
            try:
                p = attrgetter(self.map['performer'])(self.diagnostic_report)
                uri = url_for('practitioner_endpoint.record', log_id=p.id)
                display = p.name.rec_name
                ref=supermod.ResourceReference()
                ref.display = supermod.string(value=display)
                ref.reference = supermod.string(value=uri)
            except:
                # Not absolutely needed, so continue execution
                pass
            else:
                self.set_performer(ref)

    def __set_gnu_subject(self):
        if self.diagnostic_report:
            try:
                patient = attrgetter(self.map['subject'])(self.diagnostic_report)
                uri = url_for('patient_endpoint.record', log_id=patient.id)
                display = patient.rec_name
                ref=supermod.ResourceReference()
                ref.display = supermod.string(value=display)
                ref.reference = supermod.string(value=uri)
                self.set_subject(ref)
            except:
                # Without subject, useless information
                raise ValueError('No subject')

    def __set_gnu_conclusion(self):
        if self.diagnostic_report:
            text = attrgetter(self.map['conclusion'])(self.diagnostic_report)
            if text:
                conclusion = supermod.string(value=text)
                self.set_conclusion(conclusion)

class health_DiagnosticReport_Image(supermod.DiagnosticReport_Image):
    pass

class health_DiagnosticReportStatus(supermod.DiagnosticReportStatus):
    pass
