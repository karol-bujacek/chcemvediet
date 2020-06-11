# vim: expandtab
# -*- coding: utf-8 -*-
import random
import unittest

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from . import ObligeesTestCaseMixin
from ..models import Obligee, HistoricalObligee

class ObligeeModelTest(ObligeesTestCaseMixin, TestCase):
    u"""
    Tests ``Obligee`` and ``HistoricalObligee`` models.
    """

    @unittest.skip(u'FIXME')
    def test_name_field(self):
        oblg = self._create_obligee(name=u'Agency')
        self.assertEqual(oblg.name, u'Agency')

    @unittest.skip(u'FIXME')
    def test_name_field_default_value_if_omitted(self):
        oblg = self._create_obligee(omit=[u'name'])
        self.assertEqual(oblg.name, u'')

    @unittest.skip(u'FIXME')
    def test_street_field(self):
        oblg = self._create_obligee(street=u'123 Westside')
        self.assertEqual(oblg.street, u'123 Westside')

    @unittest.skip(u'FIXME')
    def test_street_field_default_value_if_omitted(self):
        oblg = self._create_obligee(omit=[u'street'])
        self.assertEqual(oblg.street, u'')

    @unittest.skip(u'FIXME')
    def test_city_field(self):
        oblg = self._create_obligee(city=u'Winterfield')
        self.assertEqual(oblg.city, u'Winterfield')

    @unittest.skip(u'FIXME')
    def test_city_field_default_value_if_omitted(self):
        oblg = self._create_obligee(omit=[u'city'])
        self.assertEqual(oblg.city, u'')

    @unittest.skip(u'FIXME')
    def test_zip_field(self):
        oblg = self._create_obligee(zip=u'12345')
        self.assertEqual(oblg.zip, u'12345')

    @unittest.skip(u'FIXME')
    def test_zip_field_default_value_if_omitted(self):
        oblg = self._create_obligee(omit=[u'zip'])
        self.assertEqual(oblg.zip, u'')

    @unittest.skip(u'FIXME')
    def test_emails_field(self):
        oblg = self._create_obligee(emails=u'agency@example.com')
        self.assertEqual(oblg.emails, u'agency@example.com')

    @unittest.skip(u'FIXME')
    def test_emails_field_default_value_if_omitted(self):
        oblg = self._create_obligee(omit=[u'emails'])
        self.assertEqual(oblg.emails, u'')

    @unittest.skip(u'FIXME')
    def test_emails_field_validation_with_invalid_email(self):
        oblg = self._create_obligee(emails=u'invalid')
        with self.assertRaisesMessage(ValidationError, u'"invalid" is not a valid email address'):
            oblg.full_clean()

    @unittest.skip(u'FIXME')
    def test_emails_field_validation_with_normalized_email(self):
        oblg = self._create_obligee(emails=u'"John" Smith <smith@example.com>')
        with self.assertRaisesMessage(ValidationError, u'Parsed as: John Smith <smith@example.com>'):
            oblg.full_clean()

    @unittest.skip(u'FIXME')
    def test_emails_field_validation_with_valid_email(self):
        oblg = self._create_obligee(emails=u'John Smith <smith@example.com>')
        oblg.full_clean()

    @unittest.skip(u'FIXME')
    def test_slug_field_computed_value(self):
        oblg = self._create_obligee(name=u'Agency')
        self.assertEqual(oblg.slug, u'-agency-')

    @unittest.skip(u'FIXME')
    def test_slug_field_computed_value_from_multiword_name(self):
        oblg = self._create_obligee(name=u'Some Important Agency')
        self.assertEqual(oblg.slug, u'-some-important-agency-')

    @unittest.skip(u'FIXME')
    def test_slug_field_computed_value_from_name_with_accents(self):
        oblg = self._create_obligee(name=u'áäčďéěíľĺňóôŕřšťúýž')
        self.assertEqual(oblg.slug, u'-aacdeeillnoorrstuyz-')

    @unittest.skip(u'FIXME')
    def test_slug_field_computed_value_from_name_with_uppercase_accents(self):
        oblg = self._create_obligee(name=u'ÁÄČĎÉĚÍĽĹŇÓÔŔŘŠŤÚÝŽ')
        self.assertEqual(oblg.slug, u'-aacdeeillnoorrstuyz-')

    @unittest.skip(u'FIXME')
    def test_slug_field_computed_value_from_name_with_cyrillics(self):
        oblg = self._create_obligee(name=u'кюм иреуры рэпудёандаэ')
        self.assertEqual(oblg.slug, u'-kium-ireury-repudioandae-')

    @unittest.skip(u'FIXME')
    def test_slug_field_computed_value_from_empty_name(self):
        oblg = self._create_obligee(name=u'')
        self.assertEqual(oblg.slug, u'--')

    @unittest.skip(u'FIXME')
    def test_slug_field_may_not_be_set_by_user(self):
        oblg = self._create_obligee(name=u'Agency', slug=u'-slug-')
        self.assertEqual(oblg.slug, u'-agency-')

    @unittest.skip(u'FIXME')
    def test_slug_field_may_not_be_changed_by_user(self):
        oblg = self._create_obligee(name=u'Agency')
        oblg.slug = u'-slug-'
        oblg.save()
        self.assertEqual(oblg.slug, u'-agency-')
        oblg = Obligee.objects.get(pk=oblg.pk)
        self.assertEqual(oblg.slug, u'-agency-')

    @unittest.skip(u'FIXME')
    def test_slug_field_is_changed_when_name_field_changes(self):
        oblg = self._create_obligee(name=u'Agency')
        oblg.name = u'Another Agency'
        oblg.save()
        self.assertEqual(oblg.slug, u'-another-agency-')
        oblg = Obligee.objects.get(pk=oblg.pk)
        self.assertEqual(oblg.slug, u'-another-agency-')

    @unittest.skip(u'FIXME')
    def test_slug_field_is_not_changed_if_name_is_not_saved(self):
        oblg = self._create_obligee(name=u'Agency')
        oblg.name = u'Another Agency'
        oblg.save(update_fields=[u'street'])
        self.assertEqual(oblg.slug, u'-agency-')
        oblg = Obligee.objects.get(pk=oblg.pk)
        self.assertEqual(oblg.slug, u'-agency-')

    @unittest.skip(u'FIXME')
    def test_slug_field_is_changed_if_name_is_saved(self):
        oblg = self._create_obligee(name=u'Agency')
        oblg.name = u'Another Agency'
        oblg.save(update_fields=[u'name'])
        self.assertEqual(oblg.slug, u'-another-agency-')
        oblg = Obligee.objects.get(pk=oblg.pk)
        self.assertEqual(oblg.slug, u'-another-agency-')

    @unittest.skip(u'FIXME')
    def test_status_field(self):
        tests = (
                (Obligee.STATUSES.PENDING, u'Pending'),
                (Obligee.STATUSES.DISSOLVED, u'Dissolved'),
                )
        # Make sure we are testing all defined obligee statuses
        tested_statuses = [a for a, _ in tests]
        defined_statuses = Obligee.STATUSES._inverse.keys()
        self.assertItemsEqual(tested_statuses, defined_statuses)

        for status, expected_display in tests:
            oblg = self._create_obligee(status=status)
            self.assertEqual(oblg.status, status)
            self.assertEqual(oblg.get_status_display(), expected_display)

    @unittest.skip(u'FIXME')
    def test_status_field_may_not_be_omitted(self):
        with self.assertRaisesMessage(IntegrityError, u'obligees_obligee.status may not be NULL'):
            self._create_obligee(omit=[u'status'])

    def test_no_default_ordering(self):
        self.assertFalse(Obligee.objects.all().ordered)

    @unittest.skip(u'FIXME')
    def test_emails_parsed_property(self):
        oblg = self._create_obligee(emails=u'The Agency <agency@example.com>')
        self.assertEqual(list(oblg.emails_parsed), [(u'The Agency', u'agency@example.com')])

    @unittest.skip(u'FIXME')
    def test_emails_parsed_property_with_comma_in_name(self):
        oblg = self._create_obligee(emails=u'"Agency, The" <agency@example.com>')
        self.assertEqual(list(oblg.emails_parsed), [(u'Agency, The', u'agency@example.com')])

    @unittest.skip(u'FIXME')
    def test_emails_parsed_property_with_quotes_in_name(self):
        oblg = self._create_obligee(emails=u'"The \\"Secret\\" Agency" <agency@example.com>')
        self.assertEqual(list(oblg.emails_parsed), [(u'The "Secret" Agency', u'agency@example.com')])

    @unittest.skip(u'FIXME')
    def test_emails_parsed_property_with_empty_name(self):
        oblg = self._create_obligee(emails=u'     <agency@example.com>')
        self.assertEqual(list(oblg.emails_parsed), [(u'', u'agency@example.com')])

    @unittest.skip(u'FIXME')
    def test_emails_parsed_property_without_name(self):
        oblg = self._create_obligee(emails=u'agency@example.com')
        self.assertEqual(list(oblg.emails_parsed), [(u'', u'agency@example.com')])

    @unittest.skip(u'FIXME')
    def test_emails_parsed_property_with_multiple_mails(self):
        oblg = self._create_obligee(emails=u'The Agency <agency@example.com>, Another Mail <another@example.com>')
        self.assertEqual(list(oblg.emails_parsed), [(u'The Agency', u'agency@example.com'), (u'Another Mail', u'another@example.com')])

    @unittest.skip(u'FIXME')
    def test_emails_parsed_property_with_empty_mails(self):
        oblg = self._create_obligee(emails=u'  , The Agency <agency@example.com>,  ,   ')
        self.assertEqual(list(oblg.emails_parsed), [(u'The Agency', u'agency@example.com')])

    @unittest.skip(u'FIXME')
    def test_emails_parsed_property_with_no_emails(self):
        oblg = self._create_obligee(emails=u'')
        self.assertEqual(list(oblg.emails_parsed), [])

    @unittest.skip(u'FIXME')
    def test_emails_formatted_property(self):
        oblg = self._create_obligee(emails=u'The Agency <agency@example.com>')
        self.assertEqual(list(oblg.emails_formatted), [u'The Agency <agency@example.com>'])

    @unittest.skip(u'FIXME')
    def test_emails_formatted_property_with_comma_in_name(self):
        oblg = self._create_obligee(emails=u'"Agency, The" <agency@example.com>')
        self.assertEqual(list(oblg.emails_formatted), [u'"Agency, The" <agency@example.com>'])

    @unittest.skip(u'FIXME')
    def test_emails_formatted_property_with_quotes_in_name(self):
        oblg = self._create_obligee(emails=u'"The \\"Secret\\" Agency" <agency@example.com>')
        self.assertEqual(list(oblg.emails_formatted), [u'"The \\"Secret\\" Agency" <agency@example.com>'])

    @unittest.skip(u'FIXME')
    def test_emails_formatted_property_with_empty_name(self):
        oblg = self._create_obligee(emails=u'     <agency@example.com>')
        self.assertEqual(list(oblg.emails_formatted), [u'agency@example.com'])

    @unittest.skip(u'FIXME')
    def test_emails_formatted_property_without_name(self):
        oblg = self._create_obligee(emails=u'agency@example.com')
        self.assertEqual(list(oblg.emails_formatted), [u'agency@example.com'])

    @unittest.skip(u'FIXME')
    def test_emails_formatted_property_with_multiple_mails(self):
        oblg = self._create_obligee(emails=u'The Agency <agency@example.com>, Another Mail <another@example.com>')
        self.assertEqual(list(oblg.emails_formatted), [u'The Agency <agency@example.com>', u'Another Mail <another@example.com>'])

    @unittest.skip(u'FIXME')
    def test_emails_formatted_property_with_empty_mails(self):
        oblg = self._create_obligee(emails=u'  , The Agency <agency@example.com>,  ,   ')
        self.assertEqual(list(oblg.emails_formatted), [u'The Agency <agency@example.com>'])

    @unittest.skip(u'FIXME')
    def test_emails_formatted_property_with_no_emails(self):
        oblg = self._create_obligee(emails=u'')
        self.assertEqual(list(oblg.emails_formatted), [])

    @unittest.skip(u'FIXME')
    def test_repr(self):
        oblg = self._create_obligee()
        self.assertEqual(repr(oblg), u'<Obligee: %s>' % oblg.pk)

    @unittest.skip(u'FIXME')
    def test_pending_query_method(self):
        oblg1 = self._create_obligee(status=Obligee.STATUSES.DISSOLVED)
        oblg2 = self._create_obligee(status=Obligee.STATUSES.DISSOLVED)
        oblg3 = self._create_obligee(status=Obligee.STATUSES.PENDING)
        oblg4 = self._create_obligee(status=Obligee.STATUSES.PENDING)
        result = Obligee.objects.pending()
        self.assertItemsEqual(result, [oblg3, oblg4])

    @unittest.skip(u'FIXME')
    def test_order_by_pk_query_method(self):
        oblgs = [self._create_obligee() for i in range(20)]
        sample = random.sample(oblgs, 10)
        result = Obligee.objects.filter(pk__in=(d.pk for d in sample)).order_by_pk().reverse()
        self.assertEqual(list(result), sorted(sample, key=lambda d: -d.pk))

    @unittest.skip(u'FIXME')
    def test_order_by_name_query_method(self):
        names = [u'aaa', u'bbb', u'ccc', u'ddd', u'eee', u'ggg', u'hhh', u'iii', u'jjj']
        names += [u'fff', u'fff', u'fff', u'fff', u'fff'] # Many same names to check secondary sorting by ``pk``
        random.shuffle(names)
        oblgs = [self._create_obligee(name=n) for n in names]
        result = Obligee.objects.order_by_name()
        self.assertEqual(list(result), sorted(oblgs, key=lambda o: (o.name, o.pk)))

    @unittest.skip(u'FIXME')
    def test_historical_obligee_model_exists(self):
        oblg = self._create_obligee(name=u'Agency', street=u'Westside')
        count = HistoricalObligee.objects.filter(id=oblg.pk).count()
        self.assertEqual(count, 1)

    @unittest.skip(u'FIXME')
    def test_history_records_changes_to_name_field(self):
        oblg = self._create_obligee(name=u'Agency')
        oblg.name = u'Secret Agency'
        oblg.save()
        history = oblg.history.all()
        self.assertEqual([h.name for h in history], [u'Secret Agency', u'Agency'])

    @unittest.skip(u'FIXME')
    def test_history_records_changes_to_street_field(self):
        oblg = self._create_obligee(street=u'123 Westside')
        oblg.street = u'123 Eastside'
        oblg.save()
        history = oblg.history.all()
        self.assertEqual([h.street for h in history], [u'123 Eastside', u'123 Westside'])

    @unittest.skip(u'FIXME')
    def test_history_records_changes_to_city_field(self):
        oblg = self._create_obligee(city=u'Winterfield')
        oblg.city = u'Springfield'
        oblg.save()
        history = oblg.history.all()
        self.assertEqual([h.city for h in history], [u'Springfield', u'Winterfield'])

    @unittest.skip(u'FIXME')
    def test_history_records_changes_to_zip_field(self):
        oblg = self._create_obligee(zip=u'12345')
        oblg.zip = u'99999'
        oblg.save()
        history = oblg.history.all()
        self.assertEqual([h.zip for h in history], [u'99999', u'12345'])

    @unittest.skip(u'FIXME')
    def test_history_records_changes_to_emails_field(self):
        oblg = self._create_obligee(emails=u'agency@example.com')
        oblg.emails = u'agency@example.com, another@example.com'
        oblg.save()
        history = oblg.history.all()
        self.assertEqual([h.emails for h in history], [u'agency@example.com, another@example.com', u'agency@example.com'])

    @unittest.skip(u'FIXME')
    def test_history_records_changes_to_slug_field_when_name_field_changes(self):
        oblg = self._create_obligee(name=u'Agency')
        oblg.name = u'Another Agency'
        oblg.save()
        history = oblg.history.all()
        self.assertEqual([h.slug for h in history], [u'-another-agency-', u'-agency-'])

    @unittest.skip(u'FIXME')
    def test_history_records_changes_to_status_field(self):
        oblg = self._create_obligee(status=Obligee.STATUSES.PENDING)
        oblg.status = Obligee.STATUSES.DISSOLVED
        oblg.save()
        history = oblg.history.all()
        self.assertEqual([h.status for h in history], [Obligee.STATUSES.DISSOLVED, Obligee.STATUSES.PENDING])

    @unittest.skip(u'FIXME')
    def test_history_records_miltiple_changes(self):
        oblg = self._create_obligee(name=u'Agency', street=u'Westside', status=Obligee.STATUSES.PENDING)
        oblg.name = u'Secret Agency'
        oblg.save()
        oblg.street = u'Eastside'
        oblg.save()
        oblg.status = Obligee.STATUSES.DISSOLVED
        oblg.save()

        history = oblg.history.all()
        expected_history = [
                (u'Secret Agency', u'Eastside', u'-secret-agency-', Obligee.STATUSES.DISSOLVED),
                (u'Secret Agency', u'Eastside', u'-secret-agency-', Obligee.STATUSES.PENDING),
                (u'Secret Agency', u'Westside', u'-secret-agency-', Obligee.STATUSES.PENDING),
                (u'Agency', u'Westside', u'-agency-', Obligee.STATUSES.PENDING),
                ]
        self.assertEqual([(h.name, h.street, h.slug, h.status) for h in history], expected_history)
