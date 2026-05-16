# Sitbuk Landing - Django

لندینگ چندصفحه‌ای سیتباک با Django 4.2.25 و SQLite.

## صفحات
- `/` خانه
- `/features/` امکانات
- `/about/` درباره ما
- `/case-study/` مطالعه موردی
- `/pricing/` قیمت‌ها
- `/plans/` پلن‌ها و مقایسه کامل
- `/blog/` وبلاگ
- `/blog/<slug>/` جزئیات مقاله
- `/contact/` تماس با ما
- `/sitemap.xml` سایت‌مپ
- `/robots.txt` فایل robots
- `/healthz/` هلس‌چک

## امکانات این نسخه
- استفاده از لوگوی جدید سیتباک در کل سایت
- ساختار RTL و ریسپانسیو
- فرم‌های ذخیره‌شونده در دیتابیس:
  - درخواست مشاوره
  - خبرنامه
  - تماس با ما
- ارسال Ajax برای فرم‌ها با پیام موفقیت/خطا بدون رفرش صفحه
- مدل‌های مدیریتی جدید در ادمین:
  - `SiteSettings`
  - `BlogPost`
  - `FAQItem`
  - `ContactMessage`
  - `LeadRequest`
  - `NewsletterSubscription`
- وبلاگ با صفحه لیست و جزئیات مقاله
- جستجو، فیلتر دسته‌بندی و صفحه‌بندی برای وبلاگ
- سئو پایه:
  - متاتگ‌های SEO
  - Open Graph و Twitter Card
  - Canonical URL
  - JSON-LD
  - `sitemap.xml`
  - `robots.txt`
- صفحه‌های خطای سفارشی `404` و `500`
- فایل‌های نمونه استقرار برای `IIS` و `Nginx`
- داده اولیه برای تنظیمات سایت، FAQ و چند مقاله نمونه
- فونت محلی `IRANSansWebFaNum` از داخل پروژه بدون وابستگی به CDN
- preload فونت‌ها برای رندر نرم‌تر و یکدست‌تر تایپوگرافی فارسی

## اجرا
```bash
python -m venv venv
source venv/bin/activate  # ویندوز: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py runserver
```

## نکته
در پنل ادمین می‌توانید اطلاعات تماس، مطالب وبلاگ و سوالات متداول را تغییر دهید تا بخشی از محتوای سایت بدون دست‌کاری کد قابل مدیریت باشد.

## تنظیم استاتیک و مدیا روی سرور

این نسخه برای اینکه فایل‌های `static` و `media` در سرور راحت‌تر شناسایی شوند، این تغییرها را دارد:

- `STATIC_URL`, `STATIC_ROOT`, `MEDIA_URL`, `MEDIA_ROOT` در `config/settings.py` تنظیم شده‌اند.
- در `config/urls.py` مسیرهای سرو استاتیک و مدیا اضافه شده‌اند.
- پوشه `staticfiles/` با اجرای `collectstatic` داخل پروژه ساخته شده است.

### دستورهای لازم پس از استقرار

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

### اگر روی سرور هنوز فایل استاتیک لود نشد

مطمئن شوید این آدرس‌ها در تنظیمات وب‌سرور یا ریورس‌پراکسی قابل دسترسی هستند:

- `/static/`  → پوشه `staticfiles`
- `/media/`   → پوشه `media`

> نکته: اضافه کردن `static` و `media` در `urls.py` برای اجرای مستقیم Django کافی است، ولی در استقرار نهایی بهتر است خود وب‌سرور نیز این دو پوشه را سرو کند.

## فایل‌های استقرار

- نمونه تنظیم `Nginx`: `deployment/nginx/sitbuk.conf.example`
- نمونه تنظیم `IIS`: `deployment/iis/web.config.example`
- نمونه متغیرهای محیطی: `.env.example`


### آخرین به‌روزرسانی
این نسخه شامل Stage 9 است: بازطراحی صفحات داخلی، بهبود تجربه کاربری و همگام‌سازی استاتیک‌ها برای استقرار راحت‌تر.

### Stage 10 additions

New route:

```text
/faq/
```

This stage improves the content side of the site: blog hub, article detail UX, reading progress, copy-link action, FAQ page, footer link and sitemap entry. After deploying on server, run:

```bash
python manage.py collectstatic --noinput
```


## Stage 11

در نسخه Stage 11 صفحه اصلی با جزئیات بیشتر بازطراحی شده است. پس از انتقال روی سرور، دستورات زیر را اجرا کنید:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

## Stage 12 + Stage 13

در این نسخه صفحه اصلی از نظر جزئیات محصول، سناریوهای واقعی، اعتمادسازی و تبدیل کاربر بهتر شد. موارد جدید:

- جریان واقعی کار در سیتباک
- کارت‌های نقش‌محور برای مدیرعامل، فروش، عملیات و مالی
- تور تعاملی محصول
- ناوبری چسبان داخل صفحه اصلی برای دسترسی سریع به بخش‌های مهم
- کارت‌های اطمینان در Hero
- سکشن جدید کنترل مدیریتی در لحظه با داشبورد CSS-only
- سکشن تصمیم‌گیری مدیریتی
- سکشن اعتمادسازی قبل از CTA نهایی
- JavaScript فعال‌سازی خودکار بخش‌ها هنگام اسکرول

بعد از جایگزینی روی سرور:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

## Stage 14

در این نسخه اندازه متن‌ها، کارت‌ها، فاصله‌ها، آیکن‌ها، دکمه‌ها و اجزای صفحه کوچک‌تر و متراکم‌تر شد تا سایت نمای حرفه‌ای‌تر و پرجزئیات‌تری داشته باشد. تمرکز این مرحله روی density طراحی، کاهش فضای خالی اضافه، و نمایش اطلاعات بیشتر بدون شلوغی بود.

بعد از جایگزینی روی سرور:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

### Stage 16 note
در این نسخه اصلاح واحد قیمت‌ها و یک لایه CSS جدید برای پولیش دقیق صفحه اصلی اضافه شده است. بعد از استقرار روی سرور، برای نمایش آخرین CSS اجرا کنید:

```bash
python manage.py collectstatic --noinput
```


### Stage 17
در این نسخه اندازه کلی UI نسبت به نسخه خیلی فشرده Stage 16 کمی بزرگ‌تر و خواناتر شد. صفحات قیمت‌ها و پلن‌ها نیز از نظر جدول‌ها، واحد قیمت، راهنمای انتخاب پلن و ظاهر حرفه‌ای‌تر اصلاح شدند.

### Stage 18
در این نسخه صفحه امکانات بازطراحی شده و برای نمایش بهتر ارزش ماژول‌های سیتباک از تب‌های تعاملی، ماتریس نقش‌ها، سناریوهای آماده و بخش قبل/بعد استفاده شده است. بعد از استقرار روی سرور، دستور `python manage.py collectstatic --noinput` را اجرا کنید.

### آخرین وضعیت: Stage 19
این نسخه از Stage 18 ادامه داده شده و صفحات درباره ما، تماس و مطالعه موردی از نظر UI/UX، روایت محتوایی، اعتمادسازی، CTA و ریسپانسیو پولیش شده‌اند. مرحله پیشنهادی بعدی ساخت CMS برای مدیریت سکشن‌های سایت از پنل ادمین است.

### Stage 25 - مدیریت لیدها و فرم‌ها
بعد از دریافت این نسخه روی سرور اجرا کنید:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py check
```

در پنل ادمین، بخش‌های «لیدها و درخواست‌های مشاوره» و «پیام‌های تماس با ما» امکان تغییر وضعیت، تعیین اولویت، ثبت یادداشت داخلی و خروجی Excel دارند.

### Stage 26 - SEO، Open Graph و Schema حرفه‌ای
این نسخه از Stage 25 ادامه داده شده و برای آماده‌سازی بهتر سایت در گوگل و اشتراک‌گذاری شبکه‌های اجتماعی، امکانات زیر اضافه شده است:

- تنظیمات SEO عمومی سایت در پنل ادمین
- کنترل meta title/description/keywords، canonical، robots، Open Graph و Schema برای صفحات داخلی
- فیلدهای SEO اختصاصی برای مطالب وبلاگ
- JSON-LD ساختاریافته برای Organization، WebSite، WebPage/Article/FAQPage و BreadcrumbList
- بهبود robots.txt برای جلوگیری از ایندکس URLهای فیلتر/جستجو
- اضافه شدن مسیر `llms.txt` برای معرفی ساختاری سایت به ابزارهای AI/Search
- بهبود sitemap با priority/changefreq و lastmod صفحات CMS

بعد از دریافت این نسخه روی سرور اجرا کنید:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py check
python manage.py collectstatic --noinput
```

## نقشه راه جدید پنل مدیریت اختصاصی

از Stage 26.2 به بعد، توسعه مدیریت سایت بر پایه داشبورد اختصاصی انجام می‌شود و استفاده عملیاتی از پنل پیش‌فرض Django Admin هدف نهایی نیست. جزئیات کامل در فایل زیر ثبت شده است:

- `CUSTOM_ADMIN_DASHBOARD_ROADMAP_FA.md`

قدم بعدی پیشنهادی: Stage 27 برای ساخت پایه داشبورد اختصاصی شامل login/logout، layout، sidebar، dashboard summary و permission guard.

## داشبورد اختصاصی مدیریت

از Stage 27 مسیر اصلی مدیریت سایت، پنل اختصاصی جدید است:

- ورود: `/dashboard/login/`
- داشبورد: `/dashboard/`
- خروج: `/dashboard/logout/`

برای ورود، کاربر باید `is_staff=True` یا `is_superuser=True` داشته باشد. Django Admin فقط به عنوان ابزار فنی/اضطراری باقی مانده و قابلیت‌های مدیریتی سایت مرحله‌به‌مرحله به داشبورد جدید منتقل می‌شوند.

## Stage 28 - مدیریت صفحه اول در داشبورد اختصاصی

در Stage 28 مسیر `/dashboard/home/` عملیاتی شد و مدیریت صفحه اول دیگر وابسته به Django Admin نیست.

قابلیت‌ها:
- ویرایش Hero صفحه اول
- ویرایش دکمه‌ها و تصویر Hero
- افزودن و ویرایش آیتم‌های صفحه اصلی
- فعال/غیرفعال کردن آیتم‌ها
- حذف آیتم‌ها
- گروه‌بندی آیتم‌ها بر اساس سکشن

این مرحله migration جدید ندارد و از مدل‌های CMS ساخته‌شده در Stage 23 استفاده می‌کند.

## Stage 29 - مدیریت صفحات داخلی در داشبورد اختصاصی

در Stage 29 مسیر `/dashboard/pages/` عملیاتی شد و مدیریت صفحات داخلی از پنل اختصاصی انجام می‌شود.

قابلیت‌ها:
- انتخاب صفحه داخلی از بین امکانات، درباره ما، مطالعه موردی، قیمت‌ها، پلن‌ها، FAQ و تماس با ما
- ویرایش عنوان، توضیح، تصویر Hero و وضعیت فعال صفحه
- ویرایش SEO هر صفحه شامل meta title، meta description، canonical، robots، Open Graph و Schema
- افزودن، ویرایش، فعال/غیرفعال‌سازی و حذف آیتم‌های سکشن‌های داخلی
- پیش‌نمایش سریع صفحه واقعی سایت

این مرحله migration جدید ندارد و از مدل‌های Stage 24 استفاده می‌کند.

## Stage 30 - مدیریت لیدها و پیام‌ها در داشبورد اختصاصی
- مسیر `/dashboard/leads/` از حالت placeholder خارج شد و به CRM سبک اختصاصی تبدیل شد.
- لیست لیدها و پیام‌های تماس با tab جداگانه، جستجو و فیلتر وضعیت/اولویت/صفحه مبدا اضافه شد.
- تغییر وضعیت و اولویت گروهی برای لیدها و پیام‌ها اضافه شد.
- صفحه جزئیات لید با مدیریت وضعیت، اولویت، مسئول پیگیری، زمان پیگیری بعدی، آخرین تماس و یادداشت داخلی اضافه شد.
- صفحه جزئیات پیام تماس با مدیریت وضعیت، اولویت و یادداشت داخلی اضافه شد.
- خروجی Excel/CSV برای لیدها و پیام‌ها از داخل پنل اختصاصی اضافه شد.
- این مرحله migration جدید ندارد و از مدل‌های Stage 25 استفاده می‌کند.


### Stage 31 - Custom dashboard blog and FAQ management
Stage 31 moves blog and FAQ content management into the custom Sitbuk dashboard. Use `/dashboard/content/` after logging in with a staff/superuser account. This stage does not add a new migration; run `python manage.py check` and `python manage.py collectstatic --noinput` after deployment.

### Stage 32 - Custom pricing/plans dashboard
The custom dashboard now includes `/dashboard/pricing/` for managing pricing and plan-page CMS content without using Django Admin.  
It supports page settings, SEO metadata, section items, preview links, active/inactive state, ordering and deletion for pricing/plans sections.

## Stage 32.1 - ویدیوی اصلی صفحه اول
- تصویر Hero صفحه اصلی با ساختار ویدیوی HTML5 جایگزین شد.
- مسیر آماده ویدیو: `landing/static/landing/videos/home-hero.mp4`.
- poster ویدیو فعلاً از تصویر Hero فعلی خوانده می‌شود تا تا زمان جایگذاری فایل ویدیو ظاهر صفحه خراب نشود.
- استایل ریسپانسیو ویدیو با تم تیره/طلایی و حالت شبیه کارت ویدیویی اضافه شد.
- فایل راهنما `HOMEPAGE_VIDEO_ASSETS_FA.md` برای جایگذاری ویدیو اضافه شد.

## Stage 32.2 - Homepage video story sections
- Added four structured video story sections to the homepage after the hero/stats area.
- Prepared video asset paths: `home-section-1.mp4` to `home-section-4.mp4` under `landing/static/landing/videos/`.
- Added responsive RTL video/text layout matching the requested reference: video beside long copy and benefit items.
- Preserved Stage 32.1 hero video and all custom dashboard work through Stage 32.

## Stage 32.3 - About page video section
- Added a new video section to the About page with a responsive HTML5 video frame.
- Prepared `landing/static/landing/videos/about-story.mp4` as the expected video path.
- Used the existing `about_workspace.png` image as the default poster so the page stays stable before the video file is uploaded.
- Added copy and three benefit points explaining the story/team/product vision around the video.
- Synced CSS and video-folder README files with `staticfiles`.

### Stage 32.4 - Demo requests
Demo request capture is now available at `/forms/demo/`. The global demo modal collects name, phone, email, company and demo type before any demo access is granted. Run migrations after deployment:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

## Stage 32.5 - اتصال نسخه‌های دمو

برای اتصال دموهای جداگانه، این متغیرها را در محیط سرور تنظیم کن:

```env
BEHNICO_DEMO_BASE_URL=https://behnico-demo.sitbuk.com
SITBUK_DEMO_BASE_URL=https://erp-demo.sitbuk.com
DEMO_ACCESS_TOKEN_HOURS=72
```

بعد از ثبت فرم مشاهده دمو، کاربر به `/demo/<token>/` هدایت می‌شود و از آنجا نسخه بهنیکو یا سیتباک را باز می‌کند.


### Stage 32.6 - مدیریت درخواست‌های دمو و اصلاح تم ویدیوهای صفحه اول
- مدیریت درخواست‌های دمو از داشبورد اختصاصی اضافه شد: `/dashboard/demos/`
- صفحه جزئیات درخواست دمو برای وضعیت، اولویت، مسئول پیگیری، یادداشت داخلی، لینک امن و ثبت زمان ارسال لینک اضافه شد.
- خروجی Excel/CSV درخواست‌های دمو از `/dashboard/demos/export/` در دسترس است.
- رنگ و ظاهر چهار سکشن ویدیویی صفحه اصلی با تم تیره/طلایی سیتباک هماهنگ شد.

## Stage 32.7 - Bale bot

The project now includes a Bale bot integration skeleton. Configure `BALE_BOT_TOKEN`, `BALE_BOT_USERNAME`, optional `BALE_WEBHOOK_SECRET`, then run `python manage.py poll_bale` or connect Bale webhook to `/bale/webhook/<secret>/`. The bot can register consultation requests and demo requests and stores conversations/messages for the next dashboard stage.

## Stage 32.8 - مدیریت ربات بله در داشبورد اختصاصی
- صفحه `/dashboard/bale/` برای مدیریت گفتگوهای ربات بله ساخته شد.
- تنظیمات ربات، فیلتر گفتگوها، خروجی، صفحه جزئیات گفتگو، ریست جریان مکالمه و ارسال پاسخ اپراتور از داخل داشبورد اضافه شد.
- پیام‌های مرتبط با LeadRequest و DemoRequest در صفحه جزئیات قابل مشاهده و پیگیری هستند.

### Stage 32.9 update
Homepage video posters now use the uploaded custom covers and the four video-story sections have topic-specific copy aligned with the poster text.

### Stage 32.10 update
The about page video section now uses a custom story poster, dark/gold styling, and updated copy aligned with the cover theme.

### Stage 32.11 update
Homepage video poster mapping was corrected: cover #1 is forced for the top video and cover #5 is assigned to the last video section.

### Stage 32.12 update
Homepage video cover mapping was corrected: the product-introduction cover is now used for the first video, and the final lower section now uses the financial-savings cover with aligned copy.

### Stage 32.13 update
The homepage hero video now uses the latest approved poster image supplied by the client. Lower video sections remain unchanged.

## Stage 39 - پاکسازی متن‌های آماده‌سازی از صفحات عمومی
- متن راهنمای «فایل ویدیو را با نام home-hero.mp4...» از Hero صفحه اصلی حذف شد.
- متن آماده‌سازی ویدیوهای پایین صفحه اصلی با متن نهایی و بازاریابی جایگزین شد.
- نمایش مسیر فایل‌های ویدیویی زیر ویدیوهای صفحه اصلی و صفحه درباره ما حذف شد.
- چند عبارت نمایان که حس تستی/ناتمام بودن سایت می‌دادند در صفحات عمومی، صفحه تماس و متن‌های ویدیویی اصلاح شدند.
- راهنمای داخلی فایل‌های ویدیویی بازنویسی شد تا فقط در مستندات پروژه باقی بماند و در UI نمایش داده نشود.


## Stage 51 - پاکسازی متن‌های داشبورد و اجرای خودکار ربات بله
- ادامه از Stage 50 بدون rollback انجام شد.
- متن‌ها و برچسب‌های آزمایشی/Stage در UI داشبورد با متن‌های کاربردی و مناسب نسخه عملیاتی جایگزین شدند.
- متن placeholder بخش‌های رسانه و امنیت اصلاح شد تا به‌جای نمایش اسکلت/مرحله، برنامه تکمیل عملیاتی و داده‌های مرتبط را نشان دهد.
- در صفحه اصلی داشبورد، چک‌لیست «پیشنهادهای بهبود بعدی داشبورد» اضافه شد.
- در تنظیمات ربات بله، فیلد ورود کد/توکن ربات اضافه شد.
- گزینه «اجرای خودکار همراه سایت» و فاصله polling به تنظیمات ربات بله اضافه شد.
- یک worker سبک و daemon برای polling خودکار پیام‌های بله همراه با اجرای سایت اضافه شد؛ بنابراین در حالت عادی به اجرای دستور جداگانه نیاز نیست.
- دکمه‌های «تست اتصال ربات» و «بررسی دستی پیام‌های جدید» به داشبورد ربات بله اضافه شدند.
- migration جدید برای فیلدهای تنظیمات ربات بله اضافه شد.
