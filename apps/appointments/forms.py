from django import forms
from .models import Appointment
from apps.accounts.models import User
from django.utils import timezone
from .speciality_keywords import check_reason_matches_speciality
import json


class AppointmentBookingForm(forms.ModelForm):
    confirm_mismatch = forms.BooleanField(
        required=False,
        label="I understand this doctor may not specialize in my condition and wish to proceed.",
    )

    class Meta:
        model = Appointment
        fields = ['doctor', 'scheduled_time', 'reason_for_visit']
        widgets = {
            'scheduled_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'reason_for_visit': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Describe your symptoms or reason for the visit...'
            }),
        }
        labels = {
            'reason_for_visit': 'Purpose / Reason for Visit',
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.patient = user
        doctors_qs = User.objects.filter(role='doctor', is_active=True)
        self.fields['doctor'].queryset = doctors_qs

        # Show "Dr. First Last — Speciality" instead of email
        self.fields['doctor'].label_from_instance = lambda obj: (
            "Dr. {} {}".format(obj.first_name, obj.last_name)
            + (" \u2014 {}".format(obj.speciality) if obj.speciality else "")
        )

        # JSON data for the JS speciality filter
        self.doctors_json = json.dumps([
            {
                'id': d.pk,
                'name': "Dr. {} {}".format(d.first_name, d.last_name),
                'speciality': d.speciality or '',
                'label': "Dr. {} {}".format(d.first_name, d.last_name)
                         + (" \u2014 {}".format(d.speciality) if d.speciality else ""),
            }
            for d in doctors_qs
        ])

    def clean_scheduled_time(self):
        scheduled_time = self.cleaned_data.get('scheduled_time')
        if scheduled_time:
            if scheduled_time < timezone.now():
                raise forms.ValidationError("Cannot book appointments in the past.")
            doctor = self.cleaned_data.get('doctor')
            if doctor:
                exists = Appointment.objects.filter(
                    doctor=doctor,
                    scheduled_time=scheduled_time,
                    status__in=[Appointment.STATUS_PENDING, Appointment.STATUS_CONFIRMED]
                ).exists()
                if exists:
                    raise forms.ValidationError("This time slot is already booked.")
        return scheduled_time

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doctor')
        reason = cleaned_data.get('reason_for_visit', '')
        confirm_mismatch = cleaned_data.get('confirm_mismatch', False)

        if doctor and doctor.speciality and reason:
            matches = check_reason_matches_speciality(reason, doctor.speciality)
            if not matches and not confirm_mismatch:
                self.speciality_mismatch = True
                self.add_error(
                    'confirm_mismatch',
                    forms.ValidationError(
                        "Your reason doesn't appear related to Dr. {}'s speciality ({}). "
                        "Please tick the box to confirm you still wish to proceed.".format(
                            doctor.last_name, doctor.speciality
                        )
                    )
                )
            else:
                self.speciality_mismatch = False
        else:
            self.speciality_mismatch = False

        return cleaned_data
