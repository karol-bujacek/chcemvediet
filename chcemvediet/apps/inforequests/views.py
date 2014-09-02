# vim: expandtab
# -*- coding: utf-8 -*-
from email.utils import formataddr

from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_http_methods
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from allauth.account.decorators import verified_email_required

from poleno.utils.http import JsonResponse
from poleno.utils.views import require_ajax
from poleno.utils.misc import Bunch, squeeze
from chcemvediet.apps.obligees.models import Obligee

from models import Inforequest, InforequestDraft, Action
import forms

@require_http_methods([u'HEAD', u'GET'])
@login_required
def index(request):
    inforequest_list = Inforequest.objects.all().owned_by(request.user)
    draft_list = InforequestDraft.objects.owned_by(request.user)

    ctx = {}
    ctx[u'inforequest_list'] = inforequest_list
    ctx[u'draft_list'] = draft_list
    return render(request, u'inforequests/index.html', ctx)

@require_http_methods([u'HEAD', u'GET', u'POST'])
@verified_email_required
def create(request, draft_id=None):
    draft = InforequestDraft.objects.owned_by(request.user).get_or_404(pk=draft_id) if draft_id else None

    if request.method == u'POST':
        if u'save' in request.POST:
            form = forms.InforequestDraftForm(request.POST)
            if form.is_valid():
                if not draft:
                    draft = InforequestDraft(applicant=request.user)
                form.save(draft)
                draft.save()
                return HttpResponseRedirect(reverse(u'inforequests:index'))

        elif u'submit' in request.POST:
            form = forms.InforequestForm(request.POST)
            if form.is_valid():
                inforequest = Inforequest(applicant=request.user)
                form.save(inforequest)
                inforequest.save()

                action = inforequest.history.action_set.requests().first()
                sender_full = formataddr((squeeze(inforequest.applicant_name), inforequest.unique_email))
                send_mail(action.subject, action.content, sender_full, [inforequest.history.obligee.email])

                if draft:
                    draft.delete()
                return HttpResponseRedirect(reverse(u'inforequests:detail', args=(inforequest.id,)))

        else:
            raise PermissionDenied

    else:
        form = forms.InforequestDraftForm()
        if draft:
            form.load(draft)

    return render(request, u'inforequests/create.html', {
            u'form': form,
            })

@require_http_methods([u'HEAD', u'GET'])
@login_required
def detail(request, inforequest_id):
    inforequest = Inforequest.objects.owned_by(request.user).get_or_404(pk=inforequest_id)
    return render(request, u'inforequests/detail.html', {
            u'inforequest': inforequest,
            })

@require_http_methods([u'POST'])
@login_required
def delete_draft(request, draft_id):
    draft = InforequestDraft.objects.owned_by(request.user).get_or_404(pk=draft_id)
    draft.delete()
    return HttpResponseRedirect(reverse(u'inforequests:index'))

@require_http_methods([u'HEAD', u'GET', u'POST'])
@require_ajax
@login_required
def decide_email(request, action, inforequest_id, receivedemail_id):
    inforequest = Inforequest.objects.owned_by(request.user).get_or_404(pk=inforequest_id)
    receivedemail = inforequest.receivedemail_set.undecided().get_or_404(pk=receivedemail_id)

    # We don't check whether ``receivedemail`` is the oldest ``inforequest`` undecided e-mail or
    # not. Although the frontend forces the user to decide the e-mails in the order they were
    # received, it is not necessarily a mistake to decide them in any other order. In the future we
    # may even add an advanced frontend to allow the user to decide the e-mails in any order, but
    # to keep the frontend simple, we don't do it now.

    available_actions = {
            u'unrelated': Bunch(
                template = u'inforequests/actions/unrelated-email.html',
                email_status = receivedemail.STATUSES.UNRELATED,
                action_type = None,
                form_class = None,
                ),
            u'unknown': Bunch(
                template = u'inforequests/actions/unknown-email.html',
                email_status = receivedemail.STATUSES.UNKNOWN,
                action_type = None,
                form_class = None,
                ),
            u'confirmation': Bunch(
                template = u'inforequests/actions/confirmation-email.html',
                email_status = receivedemail.STATUSES.OBLIGEE_ACTION,
                action_type = Action.TYPES.CONFIRMATION,
                form_class = forms.ConfirmationEmailForm,
                ),
            u'extension': Bunch(
                template = u'inforequests/actions/extension-email.html',
                email_status = receivedemail.STATUSES.OBLIGEE_ACTION,
                action_type = Action.TYPES.EXTENSION,
                form_class = forms.ExtensionEmailForm,
                ),
            u'advancement': Bunch(
                template = u'inforequests/actions/advancement-email.html',
                email_status = receivedemail.STATUSES.OBLIGEE_ACTION,
                action_type = Action.TYPES.ADVANCEMENT,
                form_class = forms.AdvancementEmailForm,
                ),
            u'clarification-request': Bunch(
                template = u'inforequests/actions/clarification_request-email.html',
                email_status = receivedemail.STATUSES.OBLIGEE_ACTION,
                action_type = Action.TYPES.CLARIFICATION_REQUEST,
                form_class = forms.ClarificationRequestEmailForm,
                ),
            u'disclosure': Bunch(
                template = u'inforequests/actions/disclosure-email.html',
                email_status = receivedemail.STATUSES.OBLIGEE_ACTION,
                action_type = Action.TYPES.DISCLOSURE,
                form_class = forms.DisclosureEmailForm,
                ),
            u'refusal': Bunch(
                template = u'inforequests/actions/refusal-email.html',
                email_status = receivedemail.STATUSES.OBLIGEE_ACTION,
                action_type = Action.TYPES.REFUSAL,
                form_class = forms.RefusalEmailForm,
                ),
            }

    try:
        template = available_actions[action].template
        email_status = available_actions[action].email_status
        action_type = available_actions[action].action_type
        form_class = available_actions[action].form_class
    except KeyError:
        raise Http404(u'Invalid action.')

    if request.method == u'POST':
        action = None
        if action_type is not None:
            form = form_class(request.POST, history_set=inforequest.history_set)
            if not form.is_valid():
                return JsonResponse({
                        u'result': u'invalid',
                        u'content': render_to_string(template, context_instance=RequestContext(request), dictionary={
                            u'inforequest': inforequest,
                            u'email': receivedemail,
                            u'form': form,
                            }),
                        })
            action = Action(
                    subject=receivedemail.raw_email.subject,
                    content=receivedemail.raw_email.text,
                    effective_date=receivedemail.raw_email.processed,
                    receivedemail=receivedemail,
                    type=action_type,
                    )
            form.save(action)
            action.save()

        # FIXME: comment this if you are lazy to send e-mails while testing
        #receivedemail.status = email_status
        #receivedemail.save()

        return JsonResponse({
                u'result': u'success',
                u'scroll_to': u'#action-%d' % action.id if action else u'',
                u'content': render_to_string(u'inforequests/detail-main.html', context_instance=RequestContext(request), dictionary={
                    u'inforequest': inforequest,
                    }),
                })

    else: # request.method != u'POST'
        form = form_class(history_set=inforequest.history_set) if form_class else None
        return render(request, template, {
                u'inforequest': inforequest,
                u'email': receivedemail,
                u'form': form,
                })

@require_http_methods([u'HEAD', u'GET', u'POST'])
@require_ajax
@login_required
def add_smail(request, action, inforequest_id):
    inforequest = Inforequest.objects.owned_by(request.user).get_or_404(pk=inforequest_id)

    # We don't check whether there are any undecided received e-mails waiting for this
    # ``inforequest``. Although the frontend forces the user to decide the e-mails before he can
    # add s-mails, it is not necessarily a mistake to add a s-mail before deciding waiting e-mails.

    available_actions = {
            u'confirmation': Bunch(
                template = u'inforequests/actions/confirmation-smail.html',
                action_type = Action.TYPES.CONFIRMATION,
                form_class = forms.ConfirmationSmailForm,
                ),
            u'extension': Bunch(
                template = u'inforequests/actions/extension-smail.html',
                action_type = Action.TYPES.EXTENSION,
                form_class = forms.ExtensionSmailForm,
                ),
            u'advancement': Bunch(
                template = u'inforequests/actions/advancement-smail.html',
                action_type = Action.TYPES.ADVANCEMENT,
                form_class = forms.AdvancementSmailForm,
                ),
            u'clarification-request': Bunch(
                template = u'inforequests/actions/clarification_request-smail.html',
                action_type = Action.TYPES.CLARIFICATION_REQUEST,
                form_class = forms.ClarificationRequestSmailForm,
                ),
            u'disclosure': Bunch(
                template = u'inforequests/actions/disclosure-smail.html',
                action_type = Action.TYPES.DISCLOSURE,
                form_class = forms.DisclosureSmailForm,
                ),
            u'refusal': Bunch(
                template = u'inforequests/actions/refusal-smail.html',
                action_type = Action.TYPES.REFUSAL,
                form_class = forms.RefusalSmailForm,
                ),
            u'affirmation': Bunch(
                template = u'inforequests/actions/affirmation-smail.html',
                action_type = Action.TYPES.AFFIRMATION,
                form_class = forms.AffirmationSmailForm,
                ),
            u'reversion': Bunch(
                template = u'inforequests/actions/reversion-smail.html',
                action_type = Action.TYPES.REVERSION,
                form_class = forms.ReversionSmailForm,
                ),
            u'remandment': Bunch(
                template = u'inforequests/actions/remandment-smail.html',
                action_type = Action.TYPES.REMANDMENT,
                form_class = forms.RemandmentSmailForm,
                ),
            }

    try:
        template = available_actions[action].template
        action_type = available_actions[action].action_type
        form_class = available_actions[action].form_class
    except KeyError:
        raise Http404(u'Invalid action.')

    if request.method == u'POST':
        form = form_class(request.POST, history_set=inforequest.history_set)
        if not form.is_valid():
            return JsonResponse({
                    u'result': u'invalid',
                    u'content': render_to_string(template, context_instance=RequestContext(request), dictionary={
                        u'inforequest': inforequest,
                        u'form': form,
                        }),
                    })
        action = Action(
                type=action_type,
                )
        form.save(action)
        action.save()

        return JsonResponse({
                u'result': u'success',
                u'scroll_to': u'#action-%d' % action.id,
                u'content': render_to_string(u'inforequests/detail-main.html', context_instance=RequestContext(request), dictionary={
                    u'inforequest': inforequest,
                    }),
                })

    else: # request.method != u'POST'
        form = form_class(history_set=inforequest.history_set)
        return render(request, template, {
                u'inforequest': inforequest,
                u'form': form,
                })
