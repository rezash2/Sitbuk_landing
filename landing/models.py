import uuid
from pathlib import Path

from django.conf import settings
from django.db import models
from django.urls import reverse


class LeadRequest(models.Model):
    STATUS_NEW = 'new'
    STATUS_CONTACTED = 'contacted'
    STATUS_QUALIFIED = 'qualified'
    STATUS_WON = 'won'
    STATUS_LOST = 'lost'

    STATUS_CHOICES = (
        (STATUS_NEW, 'جدید'),
        (STATUS_CONTACTED, 'پیگیری شده'),
        (STATUS_QUALIFIED, 'واجد شرایط'),
        (STATUS_WON, 'تبدیل شده'),
        (STATUS_LOST, 'رد شده'),
    )

    PRIORITY_LOW = 'low'
    PRIORITY_NORMAL = 'normal'
    PRIORITY_HIGH = 'high'
    PRIORITY_URGENT = 'urgent'

    PRIORITY_CHOICES = (
        (PRIORITY_LOW, 'کم'),
        (PRIORITY_NORMAL, 'معمولی'),
        (PRIORITY_HIGH, 'مهم'),
        (PRIORITY_URGENT, 'فوری'),
    )

    full_name = models.CharField(max_length=120, verbose_name='نام و نام خانوادگی')
    phone = models.CharField(max_length=32, verbose_name='شماره تماس')
    company = models.CharField(max_length=120, blank=True, verbose_name='نام شرکت')
    email = models.EmailField(blank=True, verbose_name='ایمیل')
    note = models.TextField(blank=True, verbose_name='توضیحات')
    source_page = models.CharField(max_length=50, blank=True, verbose_name='صفحه مبدا')
    status = models.CharField(max_length=24, choices=STATUS_CHOICES, default=STATUS_NEW, verbose_name='وضعیت')
    priority = models.CharField(max_length=16, choices=PRIORITY_CHOICES, default=PRIORITY_NORMAL, verbose_name='اولویت')
    assigned_to = models.CharField(max_length=120, blank=True, verbose_name='مسئول پیگیری')
    internal_note = models.TextField(blank=True, verbose_name='یادداشت داخلی')
    follow_up_at = models.DateTimeField(null=True, blank=True, verbose_name='زمان پیگیری بعدی')
    last_contacted_at = models.DateTimeField(null=True, blank=True, verbose_name='آخرین زمان تماس')
    page_url = models.CharField(max_length=255, blank=True, verbose_name='آدرس صفحه ثبت')
    referrer = models.CharField(max_length=255, blank=True, verbose_name='ارجاع‌دهنده')
    utm_source = models.CharField(max_length=80, blank=True, verbose_name='UTM Source')
    utm_campaign = models.CharField(max_length=120, blank=True, verbose_name='UTM Campaign')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP کاربر')
    user_agent = models.TextField(blank=True, verbose_name='مرورگر / دستگاه')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'لید / درخواست مشاوره'
        verbose_name_plural = 'لیدها و درخواست‌های مشاوره'
        indexes = [
            models.Index(fields=['status', 'priority'], name='landing_lead_status_prio_idx'),
            models.Index(fields=['source_page', 'created_at'], name='l_lead_src_cr_idx'),
            models.Index(fields=['follow_up_at'], name='landing_lead_followup_idx'),
        ]

    def __str__(self) -> str:
        return f'{self.full_name} - {self.phone}'

    @property
    def is_open(self) -> bool:
        return self.status in {self.STATUS_NEW, self.STATUS_CONTACTED, self.STATUS_QUALIFIED}


class LeadFollowUpActivity(models.Model):
    ACTIVITY_CALL = 'call'
    ACTIVITY_MESSAGE = 'message'
    ACTIVITY_MEETING = 'meeting'
    ACTIVITY_NOTE = 'note'
    ACTIVITY_STATUS = 'status'
    ACTIVITY_REMINDER = 'reminder'

    ACTIVITY_CHOICES = (
        (ACTIVITY_CALL, 'تماس'),
        (ACTIVITY_MESSAGE, 'پیام / واتساپ / بله'),
        (ACTIVITY_MEETING, 'جلسه / دمو'),
        (ACTIVITY_NOTE, 'یادداشت داخلی'),
        (ACTIVITY_STATUS, 'تغییر وضعیت'),
        (ACTIVITY_REMINDER, 'یادآوری پیگیری'),
    )

    RESULT_NONE = 'none'
    RESULT_CONNECTED = 'connected'
    RESULT_NO_ANSWER = 'no_answer'
    RESULT_INTERESTED = 'interested'
    RESULT_NOT_INTERESTED = 'not_interested'
    RESULT_NEXT_STEP = 'next_step'

    RESULT_CHOICES = (
        (RESULT_NONE, 'بدون نتیجه مشخص'),
        (RESULT_CONNECTED, 'ارتباط برقرار شد'),
        (RESULT_NO_ANSWER, 'پاسخ نداد'),
        (RESULT_INTERESTED, 'علاقه‌مند'),
        (RESULT_NOT_INTERESTED, 'عدم تمایل'),
        (RESULT_NEXT_STEP, 'نیازمند اقدام بعدی'),
    )

    lead = models.ForeignKey(LeadRequest, on_delete=models.CASCADE, related_name='activities', verbose_name='لید')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='کاربر ثبت‌کننده')
    activity_type = models.CharField(max_length=24, choices=ACTIVITY_CHOICES, default=ACTIVITY_NOTE, verbose_name='نوع فعالیت')
    result = models.CharField(max_length=24, choices=RESULT_CHOICES, default=RESULT_NONE, verbose_name='نتیجه')
    note = models.TextField(blank=True, verbose_name='شرح فعالیت')
    next_follow_up_at = models.DateTimeField(null=True, blank=True, verbose_name='پیگیری بعدی')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='زمان ثبت')

    class Meta:
        ordering = ['-created_at', '-id']
        verbose_name = 'فعالیت پیگیری لید'
        verbose_name_plural = 'فعالیت‌های پیگیری لید'
        indexes = [
            models.Index(fields=['lead', 'created_at'], name='lead_act_lead_cr_idx'),
            models.Index(fields=['activity_type', 'created_at'], name='lead_act_type_cr_idx'),
            models.Index(fields=['next_follow_up_at'], name='lead_act_next_idx'),
        ]

    def __str__(self) -> str:
        return f'{self.lead} - {self.get_activity_type_display()}'


class DemoRequest(models.Model):
    DEMO_BEHNICO = 'behnico'
    DEMO_SITBUK = 'sitbuk'
    DEMO_BOTH = 'both'

    DEMO_TYPE_CHOICES = (
        (DEMO_BEHNICO, 'دمو سامانه بهنیکو'),
        (DEMO_SITBUK, 'دمو سامانه سیتباک'),
        (DEMO_BOTH, 'هر دو دمو'),
    )

    STATUS_NEW = 'new'
    STATUS_REVIEWING = 'reviewing'
    STATUS_LINK_READY = 'link_ready'
    STATUS_LINK_SENT = 'link_sent'
    STATUS_ENTERED = 'entered'
    STATUS_FOLLOWED = 'followed'
    STATUS_CONVERTED = 'converted'
    STATUS_CLOSED = 'closed'

    STATUS_CHOICES = (
        (STATUS_NEW, 'جدید'),
        (STATUS_REVIEWING, 'در حال بررسی'),
        (STATUS_LINK_READY, 'لینک دمو آماده'),
        (STATUS_LINK_SENT, 'لینک دمو ارسال شد'),
        (STATUS_ENTERED, 'کاربر وارد دمو شد'),
        (STATUS_FOLLOWED, 'پیگیری شده'),
        (STATUS_CONVERTED, 'تبدیل شده'),
        (STATUS_CLOSED, 'بسته شده'),
    )

    PRIORITY_NORMAL = 'normal'
    PRIORITY_HIGH = 'high'
    PRIORITY_URGENT = 'urgent'

    PRIORITY_CHOICES = (
        (PRIORITY_NORMAL, 'معمولی'),
        (PRIORITY_HIGH, 'مهم'),
        (PRIORITY_URGENT, 'فوری'),
    )

    full_name = models.CharField(max_length=120, verbose_name='نام و نام خانوادگی')
    phone = models.CharField(max_length=32, verbose_name='شماره موبایل')
    email = models.EmailField(verbose_name='ایمیل')
    company = models.CharField(max_length=140, verbose_name='نام شرکت')
    demo_type = models.CharField(max_length=20, choices=DEMO_TYPE_CHOICES, default=DEMO_SITBUK, verbose_name='نوع دمو')
    note = models.TextField(blank=True, verbose_name='توضیحات کاربر')
    status = models.CharField(max_length=24, choices=STATUS_CHOICES, default=STATUS_NEW, verbose_name='وضعیت')
    priority = models.CharField(max_length=16, choices=PRIORITY_CHOICES, default=PRIORITY_NORMAL, verbose_name='اولویت')
    assigned_to = models.CharField(max_length=120, blank=True, verbose_name='مسئول پیگیری')
    internal_note = models.TextField(blank=True, verbose_name='یادداشت داخلی')
    demo_access_token = models.CharField(max_length=40, blank=True, verbose_name='توکن موقت دمو')
    demo_access_url = models.CharField(max_length=255, blank=True, verbose_name='لینک ورود به دمو')
    demo_access_expires_at = models.DateTimeField(null=True, blank=True, verbose_name='اعتبار لینک دمو تا')
    demo_launch_count = models.PositiveIntegerField(default=0, verbose_name='تعداد ورود به دمو')
    last_demo_target = models.CharField(max_length=20, blank=True, verbose_name='آخرین دمو انتخاب‌شده')
    demo_link_sent_at = models.DateTimeField(null=True, blank=True, verbose_name='زمان ارسال لینک دمو')
    demo_entered_at = models.DateTimeField(null=True, blank=True, verbose_name='زمان ورود به دمو')
    source_page = models.CharField(max_length=50, blank=True, verbose_name='صفحه مبدا')
    page_url = models.CharField(max_length=255, blank=True, verbose_name='آدرس صفحه ثبت')
    referrer = models.CharField(max_length=255, blank=True, verbose_name='ارجاع‌دهنده')
    utm_source = models.CharField(max_length=80, blank=True, verbose_name='UTM Source')
    utm_campaign = models.CharField(max_length=120, blank=True, verbose_name='UTM Campaign')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP کاربر')
    user_agent = models.TextField(blank=True, verbose_name='مرورگر / دستگاه')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'درخواست مشاهده دمو'
        verbose_name_plural = 'درخواست‌های مشاهده دمو'
        indexes = [
            models.Index(fields=['status', 'priority'], name='dreq_st_pr_idx'),
            models.Index(fields=['demo_type', 'created_at'], name='dreq_type_cr_idx'),
            models.Index(fields=['demo_access_token'], name='dreq_token_idx'),
        ]

    def __str__(self) -> str:
        return f'{self.full_name} - {self.get_demo_type_display()}'

    @property
    def is_open(self) -> bool:
        return self.status in {self.STATUS_NEW, self.STATUS_REVIEWING, self.STATUS_LINK_READY, self.STATUS_LINK_SENT}

    @property
    def allowed_demo_targets(self):
        if self.demo_type == self.DEMO_BOTH:
            return [self.DEMO_SITBUK, self.DEMO_BEHNICO]
        return [self.demo_type]

    @property
    def is_demo_link_active(self) -> bool:
        from django.utils import timezone
        return bool(self.demo_access_token) and (not self.demo_access_expires_at or self.demo_access_expires_at > timezone.now())

    def ensure_token(self):
        if not self.demo_access_token:
            self.demo_access_token = uuid.uuid4().hex
        return self.demo_access_token

    def save(self, *args, **kwargs):
        self.ensure_token()
        super().save(*args, **kwargs)


class DemoAccessEvent(models.Model):
    EVENT_VIEW = 'view'
    EVENT_LAUNCH = 'launch'
    EVENT_LINK_SENT = 'link_sent'
    EVENT_REGENERATED = 'regenerated'
    EVENT_EXTENDED = 'extended'
    EVENT_REVOKED = 'revoked'
    EVENT_NOTE = 'note'

    EVENT_CHOICES = (
        (EVENT_VIEW, 'مشاهده صفحه لینک امن'),
        (EVENT_LAUNCH, 'ورود به نسخه دمو'),
        (EVENT_LINK_SENT, 'ثبت ارسال لینک'),
        (EVENT_REGENERATED, 'بازسازی لینک امن'),
        (EVENT_EXTENDED, 'تمدید اعتبار لینک'),
        (EVENT_REVOKED, 'لغو لینک امن'),
        (EVENT_NOTE, 'یادداشت عملیاتی'),
    )

    demo_request = models.ForeignKey(DemoRequest, related_name='access_events', on_delete=models.CASCADE, verbose_name='درخواست دمو')
    event_type = models.CharField(max_length=24, choices=EVENT_CHOICES, verbose_name='نوع رویداد')
    target = models.CharField(max_length=24, blank=True, verbose_name='دموی انتخاب‌شده')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP')
    user_agent = models.TextField(blank=True, verbose_name='مرورگر / دستگاه')
    referrer = models.CharField(max_length=255, blank=True, verbose_name='ارجاع‌دهنده')
    note = models.TextField(blank=True, verbose_name='یادداشت')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'رویداد لینک امن دمو'
        verbose_name_plural = 'رویدادهای لینک امن دمو'
        indexes = [
            models.Index(fields=['demo_request', 'created_at'], name='demo_evt_req_cr_idx'),
            models.Index(fields=['event_type', 'created_at'], name='demo_evt_type_cr_idx'),
        ]

    def __str__(self) -> str:
        return f'{self.demo_request} - {self.get_event_type_display()}'


class NewsletterSubscription(models.Model):
    email = models.EmailField(unique=True, verbose_name='ایمیل')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'عضویت خبرنامه'
        verbose_name_plural = 'عضویت‌های خبرنامه'

    def __str__(self) -> str:
        return self.email


class SiteSettings(models.Model):
    site_name = models.CharField(max_length=80, default='سیتباک', verbose_name='نام سایت')
    support_phone = models.CharField(max_length=32, blank=True, verbose_name='شماره پشتیبانی')
    sales_phone = models.CharField(max_length=32, blank=True, verbose_name='شماره فروش')
    support_email = models.EmailField(blank=True, verbose_name='ایمیل')
    address = models.CharField(max_length=255, blank=True, verbose_name='آدرس')
    working_hours = models.CharField(max_length=120, blank=True, verbose_name='ساعات پاسخ‌گویی')
    footer_about = models.TextField(blank=True, verbose_name='توضیح کوتاه فوتر')
    whatsapp_number = models.CharField(max_length=32, blank=True, verbose_name='شماره واتساپ')
    telegram_url = models.URLField(blank=True, verbose_name='لینک تلگرام')
    instagram_url = models.URLField(blank=True, verbose_name='لینک اینستاگرام')
    linkedin_url = models.URLField(blank=True, verbose_name='لینک لینکدین')
    seo_title_suffix = models.CharField(max_length=90, blank=True, verbose_name='پسوند عنوان SEO')
    default_meta_description = models.TextField(blank=True, verbose_name='توضیحات پیش‌فرض متا')
    default_meta_keywords = models.CharField(max_length=255, blank=True, verbose_name='کلمات کلیدی پیش‌فرض')
    default_og_image = models.CharField(max_length=220, blank=True, verbose_name='تصویر پیش‌فرض اشتراک‌گذاری')
    default_og_image_alt = models.CharField(max_length=180, blank=True, verbose_name='متن جایگزین تصویر اشتراک‌گذاری')
    robots_policy = models.CharField(max_length=60, default='index,follow', verbose_name='سیاست پیش‌فرض robots')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'تنظیمات سایت'
        verbose_name_plural = 'تنظیمات سایت'

    def __str__(self) -> str:
        return self.site_name or 'تنظیمات سایت'

    @classmethod
    def get_solo(cls):
        return cls.objects.order_by('id').first()




class SiteRedirect(models.Model):
    STATUS_301 = 301
    STATUS_302 = 302
    STATUS_307 = 307
    STATUS_308 = 308

    STATUS_CHOICES = (
        (STATUS_301, '301 - انتقال دائمی'),
        (STATUS_302, '302 - انتقال موقت'),
        (STATUS_307, '307 - انتقال موقت با حفظ متد'),
        (STATUS_308, '308 - انتقال دائمی با حفظ متد'),
    )

    source_path = models.CharField(max_length=220, unique=True, verbose_name='مسیر قدیمی')
    target_url = models.CharField(max_length=320, verbose_name='مقصد جدید')
    status_code = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=STATUS_301, verbose_name='نوع ریدایرکت')
    internal_note = models.TextField(blank=True, verbose_name='یادداشت داخلی')
    hit_count = models.PositiveIntegerField(default=0, verbose_name='تعداد استفاده')
    last_used_at = models.DateTimeField(null=True, blank=True, verbose_name='آخرین استفاده')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['source_path']
        verbose_name = 'ریدایرکت SEO'
        verbose_name_plural = 'ریدایرکت‌های SEO'
        indexes = [
            models.Index(fields=['source_path', 'is_active'], name='site_redir_src_active_idx'),
            models.Index(fields=['status_code'], name='site_redir_status_idx'),
        ]

    def __str__(self) -> str:
        return f'{self.source_path} → {self.target_url}'

    def save(self, *args, **kwargs):
        if self.source_path and not self.source_path.startswith('/'):
            self.source_path = f'/{self.source_path}'
        if self.source_path and len(self.source_path) > 1:
            self.source_path = self.source_path.rstrip('/')
        super().save(*args, **kwargs)


class BlogPost(models.Model):
    CONTENT_STATUS_IDEA = 'idea'
    CONTENT_STATUS_DRAFT = 'draft'
    CONTENT_STATUS_REVIEW = 'review'
    CONTENT_STATUS_READY = 'ready'
    CONTENT_STATUS_ARCHIVED = 'archived'
    CONTENT_STATUS_CHOICES = (
        (CONTENT_STATUS_IDEA, 'ایده محتوا'),
        (CONTENT_STATUS_DRAFT, 'در حال نگارش'),
        (CONTENT_STATUS_REVIEW, 'نیازمند بازبینی'),
        (CONTENT_STATUS_READY, 'آماده انتشار'),
        (CONTENT_STATUS_ARCHIVED, 'آرشیو داخلی'),
    )

    title = models.CharField(max_length=180, verbose_name='عنوان')
    slug = models.SlugField(max_length=180, unique=True, verbose_name='اسلاگ')
    category = models.CharField(max_length=80, verbose_name='دسته‌بندی')
    content_status = models.CharField(max_length=20, choices=CONTENT_STATUS_CHOICES, default=CONTENT_STATUS_DRAFT, verbose_name='وضعیت تولید محتوا')
    target_keyword = models.CharField(max_length=120, blank=True, verbose_name='کلمه کلیدی هدف')
    summary = models.TextField(verbose_name='خلاصه')
    content = models.TextField(verbose_name='متن کامل')
    editor_note = models.TextField(blank=True, verbose_name='یادداشت داخلی سردبیر')
    cta_label = models.CharField(max_length=80, blank=True, verbose_name='متن دعوت به اقدام')
    cta_url = models.CharField(max_length=220, blank=True, verbose_name='لینک دعوت به اقدام')
    reading_time = models.PositiveSmallIntegerField(default=5, verbose_name='زمان مطالعه (دقیقه)')
    accent = models.CharField(max_length=24, default='gold', verbose_name='رنگ شاخص')
    seo_title = models.CharField(max_length=220, blank=True, verbose_name='عنوان SEO')
    seo_description = models.TextField(blank=True, verbose_name='توضیحات SEO')
    seo_keywords = models.CharField(max_length=255, blank=True, verbose_name='کلمات کلیدی SEO')
    og_image = models.CharField(max_length=220, blank=True, verbose_name='تصویر اشتراک‌گذاری')
    canonical_url = models.CharField(max_length=255, blank=True, verbose_name='Canonical URL اختصاصی')
    robots = models.CharField(max_length=60, default='index,follow', verbose_name='دستور robots')
    is_featured = models.BooleanField(default=False, verbose_name='مطلب ویژه')
    is_published = models.BooleanField(default=True, verbose_name='منتشر شده')
    published_at = models.DateTimeField(verbose_name='تاریخ انتشار')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at', '-created_at']
        verbose_name = 'مطلب وبلاگ'
        verbose_name_plural = 'مطالب وبلاگ'

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self):
        return reverse('blog_detail', kwargs={'slug': self.slug})


class FAQItem(models.Model):
    category = models.CharField(max_length=80, blank=True, default='عمومی', verbose_name='دسته‌بندی')
    question = models.CharField(max_length=220, verbose_name='سوال')
    answer = models.TextField(verbose_name='پاسخ')
    internal_note = models.TextField(blank=True, verbose_name='یادداشت داخلی')
    sort_order = models.PositiveSmallIntegerField(default=0, verbose_name='ترتیب')
    is_active = models.BooleanField(default=True, verbose_name='فعال')

    class Meta:
        ordering = ['sort_order', 'id']
        verbose_name = 'سوال متداول'
        verbose_name_plural = 'سوالات متداول'

    def __str__(self) -> str:
        return self.question


class ContactMessage(models.Model):
    STATUS_NEW = 'new'
    STATUS_REPLIED = 'replied'
    STATUS_CLOSED = 'closed'

    STATUS_CHOICES = (
        (STATUS_NEW, 'جدید'),
        (STATUS_REPLIED, 'پاسخ داده شده'),
        (STATUS_CLOSED, 'بسته شده'),
    )

    PRIORITY_NORMAL = 'normal'
    PRIORITY_HIGH = 'high'
    PRIORITY_URGENT = 'urgent'

    PRIORITY_CHOICES = (
        (PRIORITY_NORMAL, 'معمولی'),
        (PRIORITY_HIGH, 'مهم'),
        (PRIORITY_URGENT, 'فوری'),
    )

    full_name = models.CharField(max_length=120, verbose_name='نام و نام خانوادگی')
    phone = models.CharField(max_length=32, blank=True, verbose_name='شماره تماس')
    email = models.EmailField(blank=True, verbose_name='ایمیل')
    company = models.CharField(max_length=120, blank=True, verbose_name='نام شرکت')
    subject = models.CharField(max_length=160, blank=True, verbose_name='موضوع')
    message = models.TextField(verbose_name='پیام')
    source_page = models.CharField(max_length=50, blank=True, verbose_name='صفحه مبدا')
    status = models.CharField(max_length=24, choices=STATUS_CHOICES, default=STATUS_NEW, verbose_name='وضعیت')
    priority = models.CharField(max_length=16, choices=PRIORITY_CHOICES, default=PRIORITY_NORMAL, verbose_name='اولویت')
    internal_note = models.TextField(blank=True, verbose_name='یادداشت داخلی')
    page_url = models.CharField(max_length=255, blank=True, verbose_name='آدرس صفحه ثبت')
    referrer = models.CharField(max_length=255, blank=True, verbose_name='ارجاع‌دهنده')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP کاربر')
    user_agent = models.TextField(blank=True, verbose_name='مرورگر / دستگاه')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'پیام تماس با ما'
        verbose_name_plural = 'پیام‌های تماس با ما'
        indexes = [
            models.Index(fields=['status', 'priority'], name='l_msg_stat_prio_idx'),
            models.Index(fields=['source_page', 'created_at'], name='l_msg_src_cr_idx'),
        ]

    def __str__(self) -> str:
        return f'{self.full_name} - {self.subject or "پیام جدید"}'


class HomeHeroContent(models.Model):
    eyebrow = models.CharField(max_length=120, default='پلتفرم یکپارچه مدیریت و رشد', verbose_name='متن بالای تیتر')
    kicker_primary = models.CharField(max_length=120, default='CRM، ERP و اتوماسیون در یک سیستم', verbose_name='برچسب اول')
    kicker_secondary = models.CharField(max_length=120, default='راه‌اندازی مرحله‌ای', verbose_name='برچسب دوم')
    title_prefix = models.CharField(max_length=160, default='نرم‌افزارهای سازمانی و', verbose_name='بخش اول تیتر')
    title_highlight = models.CharField(max_length=80, default='اتوماسیون', verbose_name='کلمه برجسته تیتر')
    title_suffix = models.CharField(max_length=80, default='کسب‌وکار', verbose_name='بخش پایانی تیتر')
    description = models.TextField(default='سیتباک راهکار جامع برای مدیریت ارتباط با مشتریان، فرآیندها، منابع، اهداف و گزارش‌های مدیریتی است؛ یک هسته واحد برای رشد سریع‌تر، دقیق‌تر و هوشمندتر.', verbose_name='توضیح Hero')
    primary_button_label = models.CharField(max_length=80, default='درخواست دمو رایگان', verbose_name='متن دکمه اصلی')
    primary_button_url = models.CharField(max_length=160, default='#contact-block', verbose_name='لینک دکمه اصلی')
    secondary_button_label = models.CharField(max_length=80, default='مشاهده امکانات', verbose_name='متن دکمه دوم')
    secondary_button_url_name = models.CharField(max_length=80, default='features', verbose_name='نام URL دکمه دوم')
    hero_image = models.CharField(max_length=220, default='landing/images/home_story_sitbuk.png', verbose_name='مسیر تصویر Hero در static')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'محتوای Hero صفحه اصلی'
        verbose_name_plural = 'CMS صفحه اصلی - Hero'

    def __str__(self) -> str:
        return self.title_highlight or 'Hero صفحه اصلی'

    @classmethod
    def get_solo(cls):
        return cls.objects.filter(is_active=True).order_by('id').first()


class HomeContentItem(models.Model):
    SECTION_QUICK_PROOF = 'quick_proof'
    SECTION_STAT = 'stat'
    SECTION_SERVICE = 'service'
    SECTION_SHOWCASE = 'showcase'
    SECTION_MODULE = 'module'
    SECTION_PROCESS = 'process'

    SECTION_CHOICES = (
        (SECTION_QUICK_PROOF, 'مزیت‌های سریع Hero'),
        (SECTION_STAT, 'آمار صفحه اصلی'),
        (SECTION_SERVICE, 'خدمات اصلی'),
        (SECTION_SHOWCASE, 'نکات نمای محصول'),
        (SECTION_MODULE, 'ماژول‌های اصلی'),
        (SECTION_PROCESS, 'مراحل همکاری'),
    )

    section = models.CharField(max_length=32, choices=SECTION_CHOICES, verbose_name='بخش')
    title = models.CharField(max_length=160, verbose_name='عنوان')
    subtitle = models.CharField(max_length=180, blank=True, verbose_name='زیرعنوان / متن کوتاه')
    description = models.TextField(blank=True, verbose_name='توضیح')
    value = models.CharField(max_length=40, blank=True, verbose_name='عدد / مقدار')
    badge = models.CharField(max_length=80, blank=True, verbose_name='برچسب')
    icon = models.CharField(max_length=48, default='sparkles', verbose_name='کد آیکن')
    sort_order = models.PositiveSmallIntegerField(default=0, verbose_name='ترتیب نمایش')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['section', 'sort_order', 'id']
        verbose_name = 'آیتم CMS صفحه اصلی'
        verbose_name_plural = 'CMS صفحه اصلی - آیتم‌ها'

    def __str__(self) -> str:
        return f'{self.get_section_display()} - {self.title}'

class PageContent(models.Model):
    PAGE_FEATURES = 'features'
    PAGE_ABOUT = 'about'
    PAGE_CASE_STUDY = 'case_study'
    PAGE_PRICING = 'pricing'
    PAGE_PLANS = 'plans'
    PAGE_FAQ = 'faq'
    PAGE_CONTACT = 'contact'

    PAGE_CHOICES = (
        (PAGE_FEATURES, 'صفحه امکانات'),
        (PAGE_ABOUT, 'صفحه درباره ما'),
        (PAGE_CASE_STUDY, 'صفحه مطالعه موردی'),
        (PAGE_PRICING, 'صفحه قیمت‌ها'),
        (PAGE_PLANS, 'صفحه پلن‌ها'),
        (PAGE_FAQ, 'صفحه سوالات متداول'),
        (PAGE_CONTACT, 'صفحه تماس با ما'),
    )

    page_key = models.CharField(max_length=40, choices=PAGE_CHOICES, unique=True, verbose_name='صفحه')
    page_kicker = models.CharField(max_length=160, blank=True, verbose_name='متن کوتاه بالای تیتر')
    page_title = models.CharField(max_length=220, blank=True, verbose_name='تیتر اصلی صفحه')
    page_description = models.TextField(blank=True, verbose_name='توضیح اصلی صفحه')
    seo_title = models.CharField(max_length=220, blank=True, verbose_name='عنوان SEO')
    seo_description = models.TextField(blank=True, verbose_name='توضیحات SEO')
    seo_keywords = models.CharField(max_length=255, blank=True, verbose_name='کلمات کلیدی SEO')
    canonical_path = models.CharField(max_length=160, blank=True, verbose_name='مسیر canonical')
    robots = models.CharField(max_length=60, default='index,follow', verbose_name='دستور robots')
    og_type = models.CharField(max_length=40, default='website', verbose_name='نوع Open Graph')
    schema_type = models.CharField(max_length=60, default='WebPage', verbose_name='نوع Schema')
    og_image = models.CharField(max_length=220, blank=True, verbose_name='تصویر اشتراک‌گذاری')
    og_image_alt = models.CharField(max_length=180, blank=True, verbose_name='متن جایگزین تصویر اشتراک‌گذاری')
    hero_image = models.CharField(max_length=220, blank=True, verbose_name='مسیر تصویر اصلی در static')
    hero_alt = models.CharField(max_length=180, blank=True, verbose_name='متن جایگزین تصویر')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['page_key']
        verbose_name = 'CMS صفحات داخلی - تنظیمات صفحه'
        verbose_name_plural = 'CMS صفحات داخلی - تنظیمات صفحات'

    def __str__(self) -> str:
        return self.get_page_key_display()


class PageContentItem(models.Model):
    page_key = models.CharField(max_length=40, choices=PageContent.PAGE_CHOICES, verbose_name='صفحه')
    section = models.CharField(max_length=60, verbose_name='کد بخش')
    title = models.CharField(max_length=180, verbose_name='عنوان')
    subtitle = models.CharField(max_length=220, blank=True, verbose_name='زیرعنوان / متن کوتاه')
    description = models.TextField(blank=True, verbose_name='توضیح')
    value = models.CharField(max_length=80, blank=True, verbose_name='عدد / مقدار')
    badge = models.CharField(max_length=120, blank=True, verbose_name='برچسب')
    icon = models.CharField(max_length=48, default='sparkles', verbose_name='کد آیکن')
    image = models.CharField(max_length=220, blank=True, verbose_name='نام یا مسیر تصویر')
    url = models.CharField(max_length=220, blank=True, verbose_name='لینک اختیاری')
    sort_order = models.PositiveSmallIntegerField(default=0, verbose_name='ترتیب نمایش')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['page_key', 'section', 'sort_order', 'id']
        verbose_name = 'CMS صفحات داخلی - آیتم محتوا'
        verbose_name_plural = 'CMS صفحات داخلی - آیتم‌های محتوا'
        indexes = [
            models.Index(fields=['page_key', 'section', 'is_active']),
            models.Index(fields=['sort_order']),
        ]

    def __str__(self) -> str:
        return f'{self.get_page_key_display()} / {self.section} - {self.title}'


class PageBuilderSection(models.Model):
    PAGE_HOME = 'home'
    PAGE_CHOICES = ((PAGE_HOME, 'صفحه اصلی'),) + PageContent.PAGE_CHOICES

    LAYOUT_CARDS = 'cards'
    LAYOUT_GRID = 'grid'
    LAYOUT_TIMELINE = 'timeline'
    LAYOUT_STATS = 'stats'
    LAYOUT_MEDIA = 'media'
    LAYOUT_FAQ = 'faq'
    LAYOUT_CTA = 'cta'
    LAYOUT_CUSTOM = 'custom'

    LAYOUT_CHOICES = (
        (LAYOUT_CARDS, 'کارت‌ها'),
        (LAYOUT_GRID, 'گرید / شبکه'),
        (LAYOUT_TIMELINE, 'مسیر / تایم‌لاین'),
        (LAYOUT_STATS, 'آمار و عدد'),
        (LAYOUT_MEDIA, 'رسانه / ویدیو / تصویر'),
        (LAYOUT_FAQ, 'سوالات متداول'),
        (LAYOUT_CTA, 'دعوت به اقدام'),
        (LAYOUT_CUSTOM, 'سفارشی'),
    )

    page_key = models.CharField(max_length=40, choices=PAGE_CHOICES, verbose_name='صفحه')
    section_key = models.CharField(max_length=70, verbose_name='کد سکشن')
    title = models.CharField(max_length=180, verbose_name='عنوان نمایشی سکشن')
    description = models.TextField(blank=True, verbose_name='راهنمای داخلی سکشن')
    layout = models.CharField(max_length=24, choices=LAYOUT_CHOICES, default=LAYOUT_CARDS, verbose_name='نوع چیدمان')
    sort_order = models.PositiveSmallIntegerField(default=0, verbose_name='ترتیب سکشن در داشبورد')
    is_active = models.BooleanField(default=True, verbose_name='فعال در صفحه‌ساز')
    is_published = models.BooleanField(default=True, verbose_name='منتشر در سایت')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['page_key', 'sort_order', 'section_key']
        unique_together = (('page_key', 'section_key'),)
        verbose_name = 'سکشن صفحه‌ساز'
        verbose_name_plural = 'صفحه‌ساز سبک - سکشن‌ها'
        indexes = [
            models.Index(fields=['page_key', 'is_active', 'is_published'], name='pb_sec_page_pub_idx'),
            models.Index(fields=['sort_order'], name='pb_sec_sort_idx'),
        ]

    def __str__(self) -> str:
        return f'{self.get_page_key_display()} / {self.title}'


class PricingPlan(models.Model):
    CONTEXT_PRICING_CARD = 'pricing_card'
    CONTEXT_PLAN_COLUMN = 'plan_column'

    CONTEXT_CHOICES = (
        (CONTEXT_PRICING_CARD, 'کارت پلن صفحه قیمت‌ها'),
        (CONTEXT_PLAN_COLUMN, 'ستون پلن صفحه پلن‌ها'),
    )

    context = models.CharField(max_length=24, choices=CONTEXT_CHOICES, default=CONTEXT_PRICING_CARD, verbose_name='محل نمایش')
    name = models.CharField(max_length=120, verbose_name='نام پلن')
    subtitle = models.CharField(max_length=160, blank=True, verbose_name='زیرعنوان')
    tag = models.CharField(max_length=80, blank=True, verbose_name='برچسب')
    description = models.TextField(blank=True, verbose_name='توضیح')
    users_label = models.CharField(max_length=80, blank=True, verbose_name='ظرفیت کاربران')
    monthly_price = models.CharField(max_length=40, blank=True, verbose_name='قیمت ماهانه')
    annual_price = models.CharField(max_length=40, blank=True, verbose_name='قیمت سالانه / تخفیفی')
    accent = models.CharField(max_length=40, default='gold', verbose_name='رنگ / کلاس ظاهری')
    cta_label = models.CharField(max_length=80, blank=True, verbose_name='متن دکمه')
    cta_url = models.CharField(max_length=180, default='#contact-block', blank=True, verbose_name='لینک دکمه')
    features_text = models.TextField(blank=True, verbose_name='ویژگی‌ها، هر خط یک مورد')
    sort_order = models.PositiveSmallIntegerField(default=0, verbose_name='ترتیب نمایش')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['context', 'sort_order', 'id']
        verbose_name = 'پلن قیمت‌گذاری'
        verbose_name_plural = 'داشبورد قیمت‌گذاری - پلن‌ها'
        indexes = [
            models.Index(fields=['context', 'is_active', 'sort_order'], name='pricing_plan_ctx_idx'),
        ]

    def __str__(self) -> str:
        return f'{self.get_context_display()} - {self.name}'

    @property
    def features(self) -> list[str]:
        return [line.strip() for line in (self.features_text or '').splitlines() if line.strip()]


class PricingComparisonRow(models.Model):
    TABLE_PRICING = 'pricing_comparison'
    TABLE_PACKAGE = 'package_comparison'
    TABLE_PLANS = 'plans_comparison'

    TABLE_CHOICES = (
        (TABLE_PRICING, 'جدول مقایسه صفحه قیمت‌ها'),
        (TABLE_PACKAGE, 'جدول پکیج‌های اشتراکی صفحه قیمت‌ها'),
        (TABLE_PLANS, 'جدول مقایسه صفحه پلن‌ها'),
    )

    table_key = models.CharField(max_length=32, choices=TABLE_CHOICES, default=TABLE_PRICING, verbose_name='جدول')
    group_title = models.CharField(max_length=120, blank=True, verbose_name='عنوان گروه')
    group_icon = models.CharField(max_length=48, blank=True, verbose_name='آیکن گروه')
    label = models.CharField(max_length=180, verbose_name='عنوان ردیف')
    value_1 = models.CharField(max_length=120, blank=True, verbose_name='ستون ۱')
    value_2 = models.CharField(max_length=120, blank=True, verbose_name='ستون ۲')
    value_3 = models.CharField(max_length=120, blank=True, verbose_name='ستون ۳')
    value_4 = models.CharField(max_length=120, blank=True, verbose_name='ستون ۴')
    value_5 = models.CharField(max_length=120, blank=True, verbose_name='ستون ۵')
    value_6 = models.CharField(max_length=120, blank=True, verbose_name='ستون ۶')
    annual_value_1 = models.CharField(max_length=120, blank=True, verbose_name='ستون ۱ سالانه')
    annual_value_2 = models.CharField(max_length=120, blank=True, verbose_name='ستون ۲ سالانه')
    annual_value_3 = models.CharField(max_length=120, blank=True, verbose_name='ستون ۳ سالانه')
    annual_value_4 = models.CharField(max_length=120, blank=True, verbose_name='ستون ۴ سالانه')
    annual_value_5 = models.CharField(max_length=120, blank=True, verbose_name='ستون ۵ سالانه')
    annual_value_6 = models.CharField(max_length=120, blank=True, verbose_name='ستون ۶ سالانه')
    sort_order = models.PositiveSmallIntegerField(default=0, verbose_name='ترتیب نمایش')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['table_key', 'group_title', 'sort_order', 'id']
        verbose_name = 'ردیف جدول قیمت/پلن'
        verbose_name_plural = 'داشبورد قیمت‌گذاری - ردیف‌های جدول'
        indexes = [
            models.Index(fields=['table_key', 'is_active', 'sort_order'], name='pricing_row_tbl_idx'),
            models.Index(fields=['group_title', 'sort_order'], name='pricing_row_grp_idx'),
        ]

    def __str__(self) -> str:
        group = f' / {self.group_title}' if self.group_title else ''
        return f'{self.get_table_key_display()}{group} - {self.label}'

    def values(self, count: int = 6) -> list[str]:
        return [getattr(self, f'value_{idx}', '') for idx in range(1, count + 1)]

    def annual_values(self, count: int = 6) -> list[str]:
        return [getattr(self, f'annual_value_{idx}', '') for idx in range(1, count + 1)]



class MediaAsset(models.Model):
    TYPE_IMAGE = 'image'
    TYPE_VIDEO = 'video'
    TYPE_DOCUMENT = 'document'
    TYPE_OTHER = 'other'

    TYPE_CHOICES = (
        (TYPE_IMAGE, 'تصویر'),
        (TYPE_VIDEO, 'ویدیو'),
        (TYPE_DOCUMENT, 'سند'),
        (TYPE_OTHER, 'سایر فایل‌ها'),
    )

    title = models.CharField(max_length=160, verbose_name='عنوان رسانه')
    asset_type = models.CharField(max_length=24, choices=TYPE_CHOICES, default=TYPE_IMAGE, verbose_name='نوع رسانه')
    file = models.FileField(upload_to='landing/media_assets/%Y/%m/', verbose_name='فایل')
    alt_text = models.CharField(max_length=180, blank=True, verbose_name='متن جایگزین / Alt')
    usage_key = models.CharField(max_length=120, blank=True, verbose_name='محل استفاده پیشنهادی')
    description = models.TextField(blank=True, verbose_name='توضیح داخلی')
    is_active = models.BooleanField(default=True, verbose_name='قابل استفاده')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at', '-id']
        verbose_name = 'رسانه سایت'
        verbose_name_plural = 'مدیریت رسانه‌های سایت'
        indexes = [
            models.Index(fields=['asset_type', 'is_active'], name='media_asset_type_active_idx'),
            models.Index(fields=['usage_key'], name='media_asset_usage_idx'),
        ]

    def __str__(self) -> str:
        return self.title

    @property
    def public_url(self) -> str:
        try:
            return self.file.url if self.file else ''
        except Exception:
            return ''

    @property
    def filename(self) -> str:
        return Path(self.file.name).name if self.file else ''

    @property
    def extension(self) -> str:
        return Path(self.file.name).suffix.lower() if self.file else ''

    @property
    def is_image(self) -> bool:
        return self.asset_type == self.TYPE_IMAGE or self.extension in {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.svg'}

    @property
    def is_video(self) -> bool:
        return self.asset_type == self.TYPE_VIDEO or self.extension in {'.mp4', '.webm', '.mov'}

    @property
    def size_label(self) -> str:
        try:
            size = self.file.size
        except Exception:
            return 'نامشخص'
        if size >= 1024 * 1024:
            return f'{size / (1024 * 1024):.1f} MB'
        return f'{size / 1024:.0f} KB'


class DashboardAuditLog(models.Model):
    ACTION_LOGIN = 'login'
    ACTION_LOGOUT = 'logout'
    ACTION_POST = 'post'
    ACTION_SECURITY = 'security'

    ACTION_CHOICES = (
        (ACTION_LOGIN, 'ورود'),
        (ACTION_LOGOUT, 'خروج'),
        (ACTION_POST, 'تغییر داده'),
        (ACTION_SECURITY, 'امنیت و دسترسی'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='کاربر')
    username = models.CharField(max_length=150, blank=True, verbose_name='نام کاربری ثبت‌شده')
    action = models.CharField(max_length=40, choices=ACTION_CHOICES, default=ACTION_POST, verbose_name='نوع عملیات')
    section = models.CharField(max_length=80, blank=True, verbose_name='بخش داشبورد')
    object_repr = models.CharField(max_length=255, blank=True, verbose_name='موضوع عملیات')
    path = models.CharField(max_length=255, blank=True, verbose_name='مسیر')
    method = models.CharField(max_length=12, blank=True, verbose_name='متد')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP')
    user_agent = models.TextField(blank=True, verbose_name='مرورگر / دستگاه')
    metadata = models.JSONField(default=dict, blank=True, verbose_name='داده تکمیلی')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='زمان ثبت')

    class Meta:
        ordering = ['-created_at', '-id']
        verbose_name = 'گزارش تغییر داشبورد'
        verbose_name_plural = 'گزارش تغییرات داشبورد'
        indexes = [
            models.Index(fields=['section', 'created_at'], name='dash_audit_sec_cr_idx'),
            models.Index(fields=['user', 'created_at'], name='dash_audit_user_cr_idx'),
            models.Index(fields=['action', 'created_at'], name='dash_audit_act_cr_idx'),
        ]

    def __str__(self) -> str:
        return f'{self.username or self.user_id} - {self.section} - {self.action}'


class BaleBotScenario(models.Model):
    ACTION_REPLY = 'reply'
    ACTION_START_CONSULTATION = 'start_consultation'
    ACTION_START_DEMO = 'start_demo'
    ACTION_START_STATUS = 'start_status'
    ACTION_CONTACT = 'contact'
    ACTION_MAIN_MENU = 'main_menu'

    ACTION_CHOICES = (
        (ACTION_REPLY, 'ارسال پاسخ آماده'),
        (ACTION_START_CONSULTATION, 'شروع سناریوی مشاوره'),
        (ACTION_START_DEMO, 'شروع سناریوی دمو'),
        (ACTION_START_STATUS, 'شروع سناریوی پیگیری وضعیت'),
        (ACTION_CONTACT, 'ارسال راه‌های تماس'),
        (ACTION_MAIN_MENU, 'بازگشت به منوی اصلی'),
    )

    MATCH_CONTAINS = 'contains'
    MATCH_EXACT = 'exact'
    MATCH_STARTS_WITH = 'starts_with'

    MATCH_CHOICES = (
        (MATCH_CONTAINS, 'شامل کلمه/عبارت باشد'),
        (MATCH_EXACT, 'دقیقاً برابر باشد'),
        (MATCH_STARTS_WITH, 'با عبارت شروع شود'),
    )

    key = models.SlugField(max_length=80, unique=True, verbose_name='کلید سناریو')
    title = models.CharField(max_length=140, verbose_name='عنوان سناریو')
    trigger_keywords = models.TextField(verbose_name='کلمات محرک')
    match_mode = models.CharField(max_length=20, choices=MATCH_CHOICES, default=MATCH_CONTAINS, verbose_name='نوع تطبیق')
    action = models.CharField(max_length=32, choices=ACTION_CHOICES, default=ACTION_REPLY, verbose_name='عملیات')
    response_text = models.TextField(blank=True, verbose_name='متن پاسخ')
    sort_order = models.PositiveSmallIntegerField(default=0, verbose_name='ترتیب')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'id']
        verbose_name = 'سناریوی ربات بله'
        verbose_name_plural = 'سناریوهای ربات بله'
        indexes = [
            models.Index(fields=['is_active', 'sort_order'], name='bale_scn_active_sort_idx'),
            models.Index(fields=['action'], name='bale_scn_action_idx'),
        ]

    def __str__(self) -> str:
        return self.title

    def keywords(self) -> list[str]:
        return [line.strip() for line in (self.trigger_keywords or '').splitlines() if line.strip()]


class BaleOperatorReplyTemplate(models.Model):
    CATEGORY_GENERAL = 'general'
    CATEGORY_SALES = 'sales'
    CATEGORY_DEMO = 'demo'
    CATEGORY_SUPPORT = 'support'

    CATEGORY_CHOICES = (
        (CATEGORY_GENERAL, 'عمومی'),
        (CATEGORY_SALES, 'فروش'),
        (CATEGORY_DEMO, 'دمو'),
        (CATEGORY_SUPPORT, 'پشتیبانی'),
    )

    category = models.CharField(max_length=24, choices=CATEGORY_CHOICES, default=CATEGORY_GENERAL, verbose_name='دسته')
    title = models.CharField(max_length=120, verbose_name='عنوان قالب')
    text = models.TextField(verbose_name='متن پاسخ آماده')
    sort_order = models.PositiveSmallIntegerField(default=0, verbose_name='ترتیب')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'sort_order', 'id']
        verbose_name = 'قالب پاسخ اپراتور بله'
        verbose_name_plural = 'قالب‌های پاسخ اپراتور بله'
        indexes = [
            models.Index(fields=['category', 'is_active'], name='bale_tpl_cat_active_idx'),
        ]

    def __str__(self) -> str:
        return self.title


class BaleBotSettings(models.Model):
    is_enabled = models.BooleanField(default=True, verbose_name='ربات فعال است')
    auto_polling_enabled = models.BooleanField(default=True, verbose_name='اجرای خودکار همراه سایت')
    only_respond_to_mentions_in_groups = models.BooleanField(default=True, verbose_name='در گروه فقط با منشن پاسخ بدهد')
    bot_username = models.CharField(max_length=80, blank=True, verbose_name='نام کاربری ربات بدون @')
    bot_token = models.CharField(max_length=255, blank=True, verbose_name='کد / توکن ربات بله')
    polling_interval_seconds = models.PositiveSmallIntegerField(default=3, verbose_name='فاصله بررسی پیام‌ها بر حسب ثانیه')
    poller_lock_owner = models.CharField(max_length=160, blank=True, verbose_name='شناسه پردازشگر فعال')
    poller_lock_until = models.DateTimeField(null=True, blank=True, verbose_name='اعتبار قفل پردازشگر')
    welcome_text = models.TextField(default='سلام 👋 به ربات سیتباک خوش آمدید. از منوی زیر درخواست مشاوره یا مشاهده دمو را ثبت کنید.', verbose_name='پیام خوشامد')
    consultation_done_text = models.TextField(default='درخواست مشاوره شما ثبت شد. تیم سیتباک به‌زودی با شما تماس می‌گیرد.', verbose_name='پیام پایان مشاوره')
    demo_done_text = models.TextField(default='درخواست دمو ثبت شد و لینک امن دمو برای شما آماده است.', verbose_name='پیام پایان دمو')
    last_update_id = models.BigIntegerField(default=0, verbose_name='آخرین Update ID دریافت‌شده')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'تنظیمات ربات بله'
        verbose_name_plural = 'تنظیمات ربات بله'

    def __str__(self) -> str:
        return 'تنظیمات ربات بله سیتباک'

    @classmethod
    def get_solo(cls):
        obj = cls.objects.order_by('id').first()
        if obj:
            return obj
        return cls.objects.create()


class BaleBotConversation(models.Model):
    STATUS_OPEN = 'open'
    STATUS_CLOSED = 'closed'

    STATUS_CHOICES = (
        (STATUS_OPEN, 'باز'),
        (STATUS_CLOSED, 'بسته شده'),
    )

    STATE_IDLE = 'idle'
    STATE_CONSULT_NAME = 'consult_name'
    STATE_CONSULT_PHONE = 'consult_phone'
    STATE_CONSULT_COMPANY = 'consult_company'
    STATE_CONSULT_EMAIL = 'consult_email'
    STATE_CONSULT_NOTE = 'consult_note'
    STATE_DEMO_NAME = 'demo_name'
    STATE_DEMO_PHONE = 'demo_phone'
    STATE_DEMO_EMAIL = 'demo_email'
    STATE_DEMO_COMPANY = 'demo_company'
    STATE_DEMO_TYPE = 'demo_type'
    STATE_DEMO_NOTE = 'demo_note'
    STATE_STATUS_PHONE = 'status_phone'

    chat_id = models.CharField(max_length=64, unique=True, verbose_name='شناسه چت بله')
    bale_user_id = models.CharField(max_length=64, blank=True, verbose_name='شناسه کاربر بله')
    chat_type = models.CharField(max_length=32, blank=True, verbose_name='نوع چت')
    display_name = models.CharField(max_length=160, blank=True, verbose_name='نام نمایشی')
    username = models.CharField(max_length=120, blank=True, verbose_name='نام کاربری')
    phone = models.CharField(max_length=32, blank=True, verbose_name='شماره موبایل')
    email = models.EmailField(blank=True, verbose_name='ایمیل')
    company = models.CharField(max_length=140, blank=True, verbose_name='نام شرکت')
    state = models.CharField(max_length=40, default=STATE_IDLE, verbose_name='وضعیت مکالمه')
    session_data = models.JSONField(default=dict, blank=True, verbose_name='داده موقت مکالمه')
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_OPEN, verbose_name='وضعیت گفتگو')
    last_text = models.TextField(blank=True, verbose_name='آخرین پیام کاربر')
    last_seen_at = models.DateTimeField(null=True, blank=True, verbose_name='آخرین فعالیت')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'گفتگوی ربات بله'
        verbose_name_plural = 'گفتگوهای ربات بله'
        indexes = [
            models.Index(fields=['status', 'updated_at'], name='bale_conv_stat_idx'),
            models.Index(fields=['state'], name='bale_conv_state_idx'),
        ]

    def __str__(self) -> str:
        return self.display_name or self.chat_id

    def reset_flow(self):
        self.state = self.STATE_IDLE
        self.session_data = {}


class BaleBotMessage(models.Model):
    DIRECTION_IN = 'in'
    DIRECTION_OUT = 'out'
    DIRECTION_SYSTEM = 'system'

    DIRECTION_CHOICES = (
        (DIRECTION_IN, 'دریافتی'),
        (DIRECTION_OUT, 'ارسالی'),
        (DIRECTION_SYSTEM, 'سیستمی'),
    )

    conversation = models.ForeignKey(BaleBotConversation, on_delete=models.CASCADE, related_name='messages', verbose_name='گفتگو')
    bale_update_id = models.BigIntegerField(null=True, blank=True, verbose_name='Update ID')
    bale_message_id = models.CharField(max_length=80, blank=True, verbose_name='Message ID')
    direction = models.CharField(max_length=12, choices=DIRECTION_CHOICES, default=DIRECTION_IN, verbose_name='جهت')
    message_type = models.CharField(max_length=32, default='text', verbose_name='نوع پیام')
    text = models.TextField(blank=True, verbose_name='متن')
    raw_payload = models.JSONField(default=dict, blank=True, verbose_name='Payload خام')
    related_lead = models.ForeignKey(LeadRequest, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='لید مرتبط')
    related_demo = models.ForeignKey(DemoRequest, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='دموی مرتبط')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'پیام ربات بله'
        verbose_name_plural = 'پیام‌های ربات بله'
        indexes = [
            models.Index(fields=['conversation', 'created_at'], name='bale_msg_conv_cr_idx'),
            models.Index(fields=['direction', 'created_at'], name='bale_msg_dir_cr_idx'),
            models.Index(fields=['bale_update_id'], name='bale_msg_upd_idx'),
        ]
        constraints = [
            models.UniqueConstraint(fields=['direction', 'bale_update_id'], name='uniq_bale_msg_direction_update'),
        ]

    def __str__(self) -> str:
        return f'{self.get_direction_display()} - {self.conversation}'
