# vim: expandtab
# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _, pgettext_lazy
from django.contrib.webdesign.lorem_ipsum import paragraphs as lorem

from poleno.utils.model import after_saved
from poleno.utils.form import AutoSuppressedSelect
from chcemvediet.apps.obligees.forms import ObligeeWithAddressInput, ObligeeAutocompleteField

from models import History, Action


class HistoryChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, history):
        return history.obligee_name;


class PrefixedForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(PrefixedForm, self).__init__(*args, **kwargs)
        self.prefix = u'%s%s%s' % (self.prefix or u'', u'-' if self.prefix else u'', self.__class__.__name__.lower())


class InforequestForm(PrefixedForm):
    obligee = ObligeeAutocompleteField(
            label=_(u'Obligee'),
            widget=ObligeeWithAddressInput(attrs={
                u'placeholder': _(u'Obligee'),
                }),
            )
    subject = forms.CharField(
            label=_(u'Subject'),
            initial=_(u'Information request'),
            max_length=255,
            widget=forms.TextInput(attrs={
                u'placeholder': _(u'Subject'),
                }),
            )
    content = forms.CharField(
            label=_(u'Request'),
            initial=lorem(1)[0],
            widget=forms.Textarea(attrs={
                u'placeholder': _(u'Request'),
                u'class': u'input-block-level',
                }),
            )

    def __init__(self, *args, **kwargs):
        self.draft = kwargs.pop(u'draft', False)
        super(InforequestForm, self).__init__(*args, **kwargs)

        if self.draft:
            self.fields[u'obligee'].required = False
            self.fields[u'subject'].required = False
            self.fields[u'content'].required = False

    def save(self, inforequest):
        if not self.is_valid():
            raise ValueError(u"The %s could not be saved because the data didn't validate." % type(self).__name__)

        @after_saved(inforequest)
        def deferred():
            history = History(
                    obligee=self.cleaned_data[u'obligee'],
                    inforequest=inforequest,
                    )
            history.save()

            action = Action(
                    history=history,
                    subject=self.cleaned_data[u'subject'],
                    content=self.cleaned_data[u'content'],
                    effective_date=inforequest.submission_date,
                    type=Action.TYPES.REQUEST,
                    )
            action.save()

    def save_to_draft(self, draft):
        if not self.is_valid():
            raise ValueError(u"The %s could not be saved because the data didn't validate." % type(self).__name__)

        draft.obligee = self.cleaned_data[u'obligee']
        draft.subject = self.cleaned_data[u'subject']
        draft.content = self.cleaned_data[u'content']

    def load_from_draft(self, draft):
        self.initial[u'obligee'] = draft.obligee
        self.initial[u'subject'] = draft.subject
        self.initial[u'content'] = draft.content


class ActionAbstractForm(PrefixedForm):
    history = HistoryChoiceField(
            queryset=History.objects.none(),
            label=_(u'Obligee'),
            empty_label=u'',
            widget=AutoSuppressedSelect(suppressed_attrs={
                u'class': u'suppressed-control',
                }),
            )

    def __init__(self, *args, **kwargs):
        self.draft = kwargs.pop(u'draft', False)
        history_set = kwargs.pop(u'history_set')
        super(ActionAbstractForm, self).__init__(*args, **kwargs)

        field = self.fields[u'history']
        field.queryset = history_set
        if history_set.count() == 1:
            field.empty_label = None

        if self.draft:
            self.fields[u'history'].required = False

    def save(self, action):
        if not self.is_valid():
            raise ValueError(u"The %s could not be saved because the data didn't validate." % type(self).__name__)

        action.history = self.cleaned_data[u'history']

    def save_to_draft(self, draft):
        if not self.is_valid():
            raise ValueError(u"The %s could not be saved because the data didn't validate." % type(self).__name__)

        draft.history = self.cleaned_data[u'history']

    def load_from_draft(self, draft):
        self.initial[u'history'] = draft.history

class EffectiveDateMixin(ActionAbstractForm):
    effective_date = forms.DateField(
            label=_(u'Effective Date'),
            localize=True,
            widget=forms.DateInput(attrs={
                u'placeholder': pgettext_lazy(u'Form Date Placeholder', u'mm/dd/yyyy'),
                u'class': u'datepicker',
                }),
            )

    def __init__(self, *args, **kwargs):
        super(EffectiveDateMixin, self).__init__(*args, **kwargs)
        if self.draft:
            self.fields[u'effective_date'].required = False

    def save(self, action):
        super(EffectiveDateMixin, self).save(action)
        action.effective_date = self.cleaned_data[u'effective_date']

    def save_to_draft(self, draft):
        super(EffectiveDateMixin, self).save_to_draft(draft)
        draft.effective_date = self.cleaned_data[u'effective_date']

    def load_from_draft(self, draft):
        super(EffectiveDateMixin, self).load_from_draft(draft)
        self.initial[u'effective_date'] = draft.effective_date

class SubjectContentMixin(ActionAbstractForm):
    subject = forms.CharField(
            label=_(u'Subject'),
            max_length=255,
            widget=forms.TextInput(attrs={
                u'placeholder': _(u'Subject'),
                }),
            )
    content = forms.CharField(
            label=_(u'Content'),
            widget=forms.Textarea(attrs={
                u'placeholder': _(u'Content'),
                u'class': u'input-block-level',
                }),
            )

    def __init__(self, *args, **kwargs):
        super(SubjectContentMixin, self).__init__(*args, **kwargs)
        if self.draft:
            self.fields[u'subject'].required = False
            self.fields[u'content'].required = False

    def save(self, action):
        super(SubjectContentMixin, self).save(action)
        action.subject = self.cleaned_data[u'subject']
        action.content = self.cleaned_data[u'content']

    def save_to_draft(self, draft):
        super(SubjectContentMixin, self).save_to_draft(draft)
        draft.subject = self.cleaned_data[u'subject']
        draft.content = self.cleaned_data[u'content']

    def load_from_draft(self, draft):
        super(SubjectContentMixin, self).load_from_draft(draft)
        self.initial[u'subject'] = draft.subject
        self.initial[u'content'] = draft.content

class DeadlineMixin(ActionAbstractForm):
    deadline = forms.IntegerField(
            label=_(u'New Deadline'),
            initial=Action.DEFAULT_DEADLINES.EXTENSION,
            min_value=2,
            max_value=100,
            widget=forms.NumberInput(attrs={
                u'placeholder': _(u'Deadline'),
                }),
            )

    def __init__(self, *args, **kwargs):
        super(DeadlineMixin, self).__init__(*args, **kwargs)
        if self.draft:
            self.fields[u'deadline'].required = False

    def save(self, action):
        super(DeadlineMixin, self).save(action)
        action.deadline = self.cleaned_data[u'deadline']

    def save_to_draft(self, draft):
        super(DeadlineMixin, self).save_to_draft(draft)
        draft.deadline = self.cleaned_data[u'deadline']

    def load_from_draft(self, draft):
        super(DeadlineMixin, self).load_from_draft(draft)
        self.initial[u'deadline'] = draft.deadline

class AdvancedToMixin(ActionAbstractForm):
    advanced_to_1 = ObligeeAutocompleteField(
            label=_(u'Advanced To'),
            widget=ObligeeWithAddressInput(attrs={
                u'placeholder': _(u'Obligee'),
                }),
            )
    advanced_to_2 = ObligeeAutocompleteField(
            label=u'',
            required=False,
            widget=ObligeeWithAddressInput(attrs={
                u'placeholder': _(u'Obligee'),
                }),
            )
    advanced_to_3 = ObligeeAutocompleteField(
            label=u'',
            required=False,
            widget=ObligeeWithAddressInput(attrs={
                u'placeholder': _(u'Obligee'),
                }),
            )
    ADVANCED_TO_FIELDS = [u'advanced_to_1', u'advanced_to_2', u'advanced_to_3']

    def __init__(self, *args, **kwargs):
        super(AdvancedToMixin, self).__init__(*args, **kwargs)
        if self.draft:
            for field in self.ADVANCED_TO_FIELDS:
                self.fields[field].required = False

    def save(self, action):
        super(AdvancedToMixin, self).save(action)

        @after_saved(action)
        def deferred():
            for field in self.ADVANCED_TO_FIELDS:
                obligee = self.cleaned_data[field]
                if obligee:
                    sub_history = History(
                            obligee=obligee,
                            inforequest=action.history.inforequest,
                            advanced_by=action,
                            )
                    sub_history.save()

                    sub_action = Action(
                            history=sub_history,
                            effective_date=action.effective_date,
                            type=Action.TYPES.ADVANCED_REQUEST,
                            )
                    sub_action.save()

    def save_to_draft(self, draft):
        super(AdvancedToMixin, self).save_to_draft(draft)

        @after_saved(draft)
        def deferred():
            draft.obligee_set.clear()
            for field in self.ADVANCED_TO_FIELDS:
                obligee = self.cleaned_data[field]
                if obligee:
                    draft.obligee_set.add(obligee)

    def load_from_draft(self, draft):
        super(AdvancedToMixin, self).load_from_draft(draft)
        for field, obligee in zip(self.ADVANCED_TO_FIELDS, draft.obligee_set.all()):
            self.initial[field] = obligee

class DisclosureLevelMixin(ActionAbstractForm):
    disclosure_level = forms.ChoiceField(
            label=_(u'Disclosure Level'),
            choices=[(u'', u'')] + Action.DISCLOSURE_LEVELS._choices,
            )

    def __init__(self, *args, **kwargs):
        super(DisclosureLevelMixin, self).__init__(*args, **kwargs)
        if self.draft:
            self.fields[u'disclosure_level'].required = False

    def save(self, action):
        super(DisclosureLevelMixin, self).save(action)
        action.disclosure_level = self.cleaned_data[u'disclosure_level']

    def save_to_draft(self, draft):
        super(DisclosureLevelMixin, self).save_to_draft(draft)
        draft.disclosure_level = self.cleaned_data[u'disclosure_level'] if self.cleaned_data[u'disclosure_level'] != u'' else None

    def load_from_draft(self, draft):
        super(DisclosureLevelMixin, self).load_from_draft(draft)
        self.initial[u'disclosure_level'] = draft.disclosure_level

class RefusalReasonMixin(ActionAbstractForm):
    refusal_reason = forms.ChoiceField(
            label=_(u'Refusal Reason'),
            choices=[(u'', u'')] + Action.REFUSAL_REASONS._choices,
            )

    def __init__(self, *args, **kwargs):
        super(RefusalReasonMixin, self).__init__(*args, **kwargs)
        if self.draft:
            self.fields[u'refusal_reason'].required = False

    def save(self, action):
        super(RefusalReasonMixin, self).save(action)
        action.refusal_reason = self.cleaned_data[u'refusal_reason']

    def save_to_draft(self, draft):
        super(RefusalReasonMixin, self).save_to_draft(draft)
        draft.refusal_reason = self.cleaned_data[u'refusal_reason'] if self.cleaned_data[u'refusal_reason'] != u'' else None

    def load_from_draft(self, draft):
        super(RefusalReasonMixin, self).load_from_draft(draft)
        self.initial[u'refusal_reason'] = draft.refusal_reason


class DecideEmailCommonForm(ActionAbstractForm):
    pass

class ConfirmationEmailForm(DecideEmailCommonForm):
    pass

class ExtensionEmailForm(DecideEmailCommonForm, DeadlineMixin):
    pass

class AdvancementEmailForm(DecideEmailCommonForm, DisclosureLevelMixin, AdvancedToMixin):
    pass

class ClarificationRequestEmailForm(DecideEmailCommonForm):
    pass

class DisclosureEmailForm(DecideEmailCommonForm, DisclosureLevelMixin):
    pass

class RefusalEmailForm(DecideEmailCommonForm, RefusalReasonMixin):
    pass


class AddSmailCommonForm(EffectiveDateMixin, SubjectContentMixin, ActionAbstractForm):
    pass

class ConfirmationSmailForm(AddSmailCommonForm):
    pass

class ExtensionSmailForm(AddSmailCommonForm, DeadlineMixin):
    pass

class AdvancementSmailForm(AddSmailCommonForm, DisclosureLevelMixin, AdvancedToMixin):
    pass

class ClarificationRequestSmailForm(AddSmailCommonForm):
    pass

class DisclosureSmailForm(AddSmailCommonForm, DisclosureLevelMixin):
    pass

class RefusalSmailForm(AddSmailCommonForm, RefusalReasonMixin):
    pass

class AffirmationSmailForm(AddSmailCommonForm, RefusalReasonMixin):
    pass

class ReversionSmailForm(AddSmailCommonForm, DisclosureLevelMixin):
    pass

class RemandmentSmailForm(AddSmailCommonForm, DisclosureLevelMixin):
    pass


class NewActionCommonForm(SubjectContentMixin, ActionAbstractForm):
    pass

class ClarificationResponseForm(NewActionCommonForm):
    pass

class AppealForm(NewActionCommonForm):
    pass


class ExtendDeadlineForm(PrefixedForm):
    extension = forms.IntegerField(
            label=_(u'Deadline Extension'),
            min_value=2,
            max_value=100,
            widget=forms.NumberInput(attrs={
                u'placeholder': _(u'Working Days'),
                }),
            )

    def save(self, action):
        if not self.is_valid():
            raise ValueError(u"The %s could not be saved because the data didn't validate." % type(self).__name__)

        action.extension = self.cleaned_data[u'extension']

    def load(self, action):
        self.initial[u'extension'] = action.extension or 5
