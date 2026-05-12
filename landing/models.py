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


class BlogPost(models.Model):
    title = models.CharField(max_length=180, verbose_name='عنوان')
    slug = models.SlugField(max_length=180, unique=True, verbose_name='اسلاگ')
    category = models.CharField(max_length=80, verbose_name='دسته‌بندی')
    summary = models.TextField(verbose_name='خلاصه')
    content = models.TextField(verbose_name='متن کامل')
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
    question = models.CharField(max_length=220, verbose_name='سوال')
    answer = models.TextField(verbose_name='پاسخ')
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

