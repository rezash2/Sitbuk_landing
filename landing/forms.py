from django import forms

from .models import BlogPost, ContactMessage, DemoRequest, LeadRequest, NewsletterSubscription


class LeadRequestForm(forms.ModelForm):
    class Meta:
        model = LeadRequest
        fields = ['full_name', 'phone', 'company', 'email', 'note']
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'نام و نام خانوادگی'}),
            'phone': forms.TextInput(attrs={'placeholder': 'شماره تماس'}),
            'company': forms.TextInput(attrs={'placeholder': 'نام شرکت / سازمان'}),
            'email': forms.EmailInput(attrs={'placeholder': 'ایمیل سازمانی'}),
            'note': forms.Textarea(attrs={'placeholder': 'نیاز یا توضیح کوتاه شما', 'rows': 3}),
        }

    def clean_phone(self):
        phone = ''.join(ch for ch in self.cleaned_data['phone'] if ch.isdigit())
        if len(phone) < 8:
            raise forms.ValidationError('شماره تماس معتبر وارد کنید.')
        return phone


class DemoRequestForm(forms.ModelForm):
    class Meta:
        model = DemoRequest
        fields = ['full_name', 'phone', 'email', 'company', 'demo_type', 'note']
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'نام و نام خانوادگی'}),
            'phone': forms.TextInput(attrs={'placeholder': 'شماره موبایل'}),
            'email': forms.EmailInput(attrs={'placeholder': 'ایمیل کاری'}),
            'company': forms.TextInput(attrs={'placeholder': 'نام شرکت / سازمان'}),
            'demo_type': forms.Select(),
            'note': forms.Textarea(attrs={'placeholder': 'در صورت نیاز، حوزه فعالیت یا انتظارتان از دمو را بنویسید', 'rows': 3}),
        }

    def clean_phone(self):
        phone = ''.join(ch for ch in self.cleaned_data.get('phone', '') if ch.isdigit())
        if len(phone) < 8:
            raise forms.ValidationError('شماره موبایل معتبر وارد کنید.')
        return phone

    def clean_email(self):
        return self.cleaned_data.get('email', '').strip().lower()

    def clean_company(self):
        company = self.cleaned_data.get('company', '').strip()
        if len(company) < 2:
            raise forms.ValidationError('نام شرکت را وارد کنید.')
        return company


class NewsletterSubscriptionForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscription
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'ایمیل خود را وارد کنید'}),
        }

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if NewsletterSubscription.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('این ایمیل قبلاً در خبرنامه ثبت شده است.')
        return email


class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['full_name', 'phone', 'email', 'company', 'subject', 'message']
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'نام و نام خانوادگی'}),
            'phone': forms.TextInput(attrs={'placeholder': 'شماره تماس'}),
            'email': forms.EmailInput(attrs={'placeholder': 'ایمیل کاری'}),
            'company': forms.TextInput(attrs={'placeholder': 'نام شرکت / سازمان'}),
            'subject': forms.TextInput(attrs={'placeholder': 'موضوع پیام'}),
            'message': forms.Textarea(attrs={'placeholder': 'نیاز، سوال یا توضیح خود را بنویسید', 'rows': 5}),
        }

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('phone') and not cleaned.get('email'):
            raise forms.ValidationError('حداقل یکی از فیلدهای شماره تماس یا ایمیل را وارد کنید.')
        return cleaned

    def clean_phone(self):
        phone = ''.join(ch for ch in self.cleaned_data.get('phone', '') if ch.isdigit())
        if phone and len(phone) < 8:
            raise forms.ValidationError('شماره تماس معتبر نیست.')
        return phone


class BlogAdminForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = '__all__'
