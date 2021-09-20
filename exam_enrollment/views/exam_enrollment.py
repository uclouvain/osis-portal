##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
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
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import logging

from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone

from base import models as mdl_base
from base.business import student as student_bsn
from base.models.education_group_year import EducationGroupYear
from exam_enrollment.models import exam_enrollment_request

logger = logging.getLogger(settings.DEFAULT_LOGGER)
queue_exception_logger = logging.getLogger(settings.QUEUE_EXCEPTION_LOGGER)


# @login_required
# @permission_required('base.is_student', raise_exception=True)
# def choose_offer(request):
#     return navigation(request, False)
#
#
# @login_required
# @permission_required('base.is_student', raise_exception=True)
# def choose_offer_direct(request):
#     return navigation(request, False)


# def navigation(request, navigate_direct_to_form):
#     try:
#         stud = student_bsn.find_by_user_and_discriminate(request.user)
#     except MultipleObjectsReturned:
#         return dash_main_view.show_multiple_registration_id_error(request)
#     current_academic_year = mdl_base.academic_year.starting_academic_year()
#     student_programs = _get_student_programs(stud, current_academic_year)
#     if student_programs:
#         if navigate_direct_to_form and len(student_programs) == 1:
#             return _get_exam_enrollment_form(student_programs[0], request, stud)
#         else:
#             return layout.render(request, 'offer_choice.html', {
#                 'programs': student_programs,
#                 'student': stud
#             })
#     else:
#         messages.add_message(request, messages.WARNING, _('no_offer_enrollment_found').format(current_academic_year))
#         return response.HttpResponseRedirect(reverse('dashboard_home'))


# @login_required
# @permission_required('base.is_student', raise_exception=True)
# def exam_enrollment_form(request, acronym: str, academic_year: int):
#     try:
#         stud = student_bsn.find_by_user_and_discriminate(request.user)
#     except MultipleObjectsReturned:
#         return dash_main_view.show_multiple_registration_id_error(request)
#     educ_group_year = EducationGroupYear.objects.get(
#         acronym=acronym,
#         academic_year__year=academic_year
#     )
#     if request.method == 'POST':
#         return _process_exam_enrollment_form_submission(educ_group_year, request, stud)
#     else:
#         return _get_exam_enrollment_form(educ_group_year, request, stud)


# def _get_student_programs(stud, acad_year):
#     if stud:
#         offer_enrollments = list(
#             mdl_base.offer_enrollment.find_by_student_academic_year(
#                 stud,
#                 acad_year
#             ).select_related('education_group_year')
#         )
#         return [
#             enrol.education_group_year for enrol in offer_enrollments
#         ]
#     return None

#
# def _get_exam_enrollment_form(educ_group_year, request, stud):
#     learn_unit_enrols = LearningUnitEnrollment.objects.filter(
#         offer_enrollment__student=stud,
#         offer_enrollment__education_group_year=educ_group_year
#     )
#     if not learn_unit_enrols:
#         messages.add_message(
#             request,
#             messages.WARNING,
#             _('no_learning_unit_enrollment_found').format(educ_group_year.acronym)
#         )
#         return response.HttpResponseRedirect(reverse('dashboard_home'))
#     request_timeout = get_request_timeout()
#     exam_enroll_request = get_exam_enroll_request(educ_group_year.acronym, request_timeout, stud)
#
#     program = EducationGroupYear.objects.get(pk=educ_group_year.id)
#
#     if exam_enroll_request:
#         try:
#             data = json.loads(exam_enroll_request.document)
#         except json.JSONDecodeError:
#             logger.exception("Json data is not valid")
#             data = {}
#         return layout.render(request, 'exam_enrollment_form.html',
#                              {
#                                  'error_message': _get_error_message(data, educ_group_year),
#                                  'exam_enrollments': data.get('exam_enrollments'),
#                                  'student': stud,
#                                  'current_number_session': data.get('current_number_session'),
#                                  'academic_year': mdl_base.academic_year.current_academic_year(),
#                                  'program': program,
#                                  'request_timeout': request_timeout,
#                                  'testwe_exam': data.get('testwe_exam'),
#                                  'teams_exam': data.get('teams_exam'),
#                                  'moodle_exam': data.get('moodle_exam'),
#                                  'covid_period': data.get('covid_period'),
#                                  'is_11ba': program.acronym.endswith('11BA'),
#                              })
#     else:
#         ask_exam_enrollment_form(stud, educ_group_year)
#         return layout.render(request, 'exam_enrollment_form.html',
#                              {
#                                  'exam_enrollments': "",
#                                  'student': stud,
#                                  'current_number_session': "",
#                                  'academic_year': mdl_base.academic_year.current_academic_year(),
#                                  'program': program,
#                                  'request_timeout': request_timeout,
#                                  'is_11ba': program.acronym.endswith('11BA'),
#                              })

#
# def _get_error_message(data, educ_group_year):
#     if data.get('error_message') == 'outside_exam_enrollment_period':
#         error_message = _("You are outside the exams enrollment period")
#     elif data.get('error_message') == 'student_can_not_enrol_to_exam':
#         error_message = _("You can not enrol to exam")
#     elif data.get('error_message') == 'no_exam_enrollment_found':
#         error_message = _("No exam enrollment found")
#     elif data.get('error_message') == 'no_exam_enrollment_avalaible':
#         error_message = _("Exam enrollment is not available")
#     elif data.get('error_message'):
#         error_message = _(data.get('error_message')).format(educ_group_year.acronym)
#     else:
#         error_message = data.get('error_message')
#     return error_message

#
# def ask_exam_enrollment_form(stud, educ_group_year):
#     if 'exam_enrollment' in settings.INSTALLED_APPS and hasattr(settings, 'QUEUES') and settings.QUEUES:
#         try:
#             message_published = ask_queue_for_exam_enrollment_form(stud, educ_group_year)
#         except (RuntimeError, pika.exceptions.ConnectionClosed, pika.exceptions.ChannelClosed,
#                 pika.exceptions.AMQPError):
#             return HttpResponse(status=400)
#         if message_published:
#             return HttpResponse(status=200)
#     return HttpResponse(status=405)


# def ask_queue_for_exam_enrollment_form(stud, educ_group_year):
#     connect = pika.BlockingConnection(_get_rabbit_settings())
#     queue_name = settings.QUEUES.get('QUEUES_NAME').get('EXAM_ENROLLMENT_FORM_REQUEST')
#     channel = _create_channel(connect, queue_name)
#     message = _exam_enrollment_form_message(
#         stud.registration_id,
#         educ_group_year.acronym,
#         educ_group_year.academic_year.year
#     )
#     message_published = channel.basic_publish(exchange='',
#                                               routing_key=queue_name,
#                                               body=json.dumps(message))
#     connect.close()
#     return message_published


# def _exam_enrollment_form_message(registration_id, offer_year_acronym, year):
#     return {
#         'registration_id': registration_id,
#         'offer_year_acronym': offer_year_acronym,
#         'year': year,
#     }
#

# def check_exam_enrollment_form(request, acronym, academic_year):
#     a_student = student_bsn.find_by_user_and_discriminate(request.user)
#     educ_group_year = EducationGroupYear.objects.filter(
#         acronym=acronym,
#         academic_year__year=academic_year
#     ).first()
#     if 'exam_enrollment' in settings.INSTALLED_APPS:
#         if _exam_enrollment_up_to_date_in_db_with_document(a_student, educ_group_year):
#             return HttpResponse(status=200)
#         else:
#             return HttpResponse(status=404)
#     return HttpResponse(status=405)


# def _exam_enrollment_up_to_date_in_db_with_document(a_student, educ_group_year):
#     an_offer_enrollment = mdl_base.offer_enrollment.get_by_student_offer(a_student, educ_group_year)
#     if an_offer_enrollment:
#         if hasattr(settings, 'QUEUES') and settings.QUEUES:
#             request_timeout = settings.QUEUES.get("QUEUES_TIMEOUT").get("EXAM_ENROLLMENT_FORM_RESPONSE")
#         else:
#             request_timeout = settings.DEFAULT_QUEUE_TIMEOUT
#         fetch_date_limit = timezone.now() - timezone.timedelta(seconds=request_timeout)
#         exam_enroll_request = exam_enrollment_request. \
#             get_by_student_and_offer_year_acronym_and_fetch_date(a_student, educ_group_year.acronym, fetch_date_limit)
#         return exam_enroll_request and exam_enroll_request.document
#     else:
#         logger.warning("This student is not enrolled in this offer_year")
#         return False

#
# def _process_exam_enrollment_form_submission(educ_group_year, request, stud):
#     # Lines before data_to_submit = ... are temporary (covid-19)
#     covid_choices = ['testwe_exam', 'moodle_exam', 'teams_exam']
#     all_covid_choices_made = all(request.POST.get(choice) for choice in covid_choices)
#     covid_period = request.POST.get('covid_period')
#     if covid_period and not all_covid_choices_made:
#         messages.add_message(request, messages.ERROR, _('Form not submitted !'))
#         messages.add_message(request, messages.ERROR, _('Please complete IMPERATIVELY the questionnaire below'))
#         return _get_exam_enrollment_form(educ_group_year, request, stud)
#
#     data_to_submit = _exam_enrollment_form_submission_message(educ_group_year, request, stud)
#     json_data = json.dumps(data_to_submit)
#     offer_enrol = offer_enrollment.get_by_student_offer(stud, educ_group_year)
#     if json_data and offer_enrol:
#         exam_enrollment_submitted.insert_or_update_document(offer_enrol, json_data)
#     queue_sender.send_message(settings.QUEUES.get('QUEUES_NAME').get('EXAM_ENROLLMENT_FORM_SUBMISSION'), 
# data_to_submit)
#     if covid_period:
#         messages.add_message(request, messages.SUCCESS, _('exam_enrollment_form_submitted_covid_period'))
#     else:
#         messages.add_message(request, messages.SUCCESS, _('exam_enrollment_form_submitted'))
#     return response.HttpResponseRedirect(reverse('dashboard_home'))


# def _exam_enrollment_form_submission_message(educ_group_year, request, stud):
#     return {
#         'registration_id': stud.registration_id,
#         'offer_year_acronym': educ_group_year.acronym,
#         'year': educ_group_year.academic_year.year,
#         'exam_enrollments': _build_enrollments_by_learning_unit(request),
#         'testwe_exam': request.POST.get('testwe_exam'),
#         'teams_exam': request.POST.get('teams_exam'),
#         'moodle_exam': request.POST.get('moodle_exam')
#     }


# def _build_enrollments_by_learning_unit(request):
#     warnings.warn(
#         "The field named 'etat_to_inscr' is only used to call EPC services. It should be deleted when the exam "
#         "enrollment business will be implemented in Osis (not in EPC anymore). "
#         "The flag 'is_enrolled' should be sufficient for Osis."
#         "Do not forget to delete the hidden input field in the html template.",
#         DeprecationWarning
#     )
#     current_number_session = request.POST['current_number_session']
#     enrollments_by_learn_unit = []
#     is_enrolled_by_acronym = _build_dicts_is_enrolled_by_acronym(current_number_session, request)
#     etat_to_inscr_by_acronym = _build_dicts_etat_to_inscr_by_acronym(request)
#     for acronym, etat_to_inscr in etat_to_inscr_by_acronym.items():
#         etat_to_inscr = None if not etat_to_inscr or etat_to_inscr == 'None' else etat_to_inscr
#         if etat_to_inscr:
#             enrollments_by_learn_unit.append({
#                 'acronym': acronym,
#                 'is_enrolled': is_enrolled_by_acronym.get(acronym, False),
#                 'etat_to_inscr': etat_to_inscr
#             })
#     return enrollments_by_learn_unit


# def _build_dicts_etat_to_inscr_by_acronym(request):
#     return {_extract_acronym(html_tag_id): etat_to_inscr for html_tag_id, etat_to_inscr in request.POST.items()
#             if "etat_to_inscr_current_session_" in html_tag_id}
#
#
# def _build_dicts_is_enrolled_by_acronym(current_number_session, request):
#     return {_extract_acronym(html_tag_id): True if value == "on" else False
#             for html_tag_id, value in request.POST.items()
#             if "chckbox_exam_enrol_sess{}_".format(current_number_session) in html_tag_id}
#
#
# def _extract_acronym(html_tag_id):
#     return html_tag_id.split("_")[-1]
