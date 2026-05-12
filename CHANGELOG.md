# CHANGELOG

## v7
- افزودن فونت محلی `IRANSansWebFaNum` و لود کامل آن از داخل پروژه بدون CDN
- Preload فونت‌ها در `base.html` برای رندر سریع‌تر و جلوگیری از FOUT
- بهبود سراسری تایپوگرافی، فاصله‌گذاری، دکمه‌ها، کارت‌ها، فرم‌ها و هدر
- افزودن افکت‌های hover، glow، scrollbar سفارشی و polish بصری برای نزدیک‌تر شدن UI به نسخه پرمیوم
- بهبود رفتار هدر در اسکرول و بستن خودکار منوی موبایل بعد از کلیک
- حفظ کامل تمام قابلیت‌ها و صفحات قبلی بدون rollback

## v6
- افزودن جستجو، فیلتر دسته‌بندی و صفحه‌بندی برای وبلاگ
- افزودن سئوی پایه برای همه صفحات شامل meta tags، Open Graph، Twitter Card و canonical
- افزودن JSON-LD برای صفحات و مقالات وبلاگ
- افزودن `sitemap.xml`, `robots.txt`, و `healthz/`
- افزودن صفحه‌های خطای سفارشی `404` و `500`
- بهبود تنظیمات آماده استقرار با متغیرهای محیطی برای دامنه، SSL و پروکسی
- افزودن فایل‌های نمونه استقرار برای `IIS` و `Nginx`
- حفظ کامل تمام تغییرات نسخه‌های قبلی بدون بازگشت به عقب

## v5
- رفع زیرساخت استاتیک و مدیا برای سرور: اضافه شدن `MEDIA_URL` و `MEDIA_ROOT`، سرو `static/media` در `config/urls.py`، و ساخت پوشه `staticfiles` با `collectstatic` برای جلوگیری از خطای پیدا نشدن فایل‌های استاتیک.

## v4
- افزودن صفحه وبلاگ و جزئیات مقاله
- افزودن صفحه تماس با ما
- افزودن Ajax برای فرم‌های مشاوره، خبرنامه و تماس
- افزودن مدل‌های `SiteSettings`, `BlogPost`, `FAQItem`, `ContactMessage`
- افزودن داده اولیه برای وبلاگ، FAQ و تنظیمات سایت
- بهبود هدر و فوتر و لینک‌دهی واقعی صفحات
- افزودن پیش‌نمایش مقالات جدید به صفحه خانه
- حفظ و ادامه تمام صفحات نسخه قبلی بدون بازگشت به عقب

## v3
- افزودن صفحات امکانات، درباره ما، مطالعه موردی، قیمت‌ها و پلن‌ها
- اتصال فرم‌های اصلی به دیتابیس

## v2
- جایگزینی لوگوی جدید سیتباک
- بازطراحی و بهبود لندینگ اصلی

## v1
- ساخت نسخه اولیه لندینگ سیتباک با Django

## Stage 8 - Premium homepage polish + static robustness
- بازطراحی سکشن هیرو و اضافه شدن لایه‌های بصری جدید، چیپ‌ها، کارت‌های شناور و لیست مزیت‌ها
- اضافه شدن سکشن Showcase برای نمایش حرفه‌ای‌تر محصول با تصویر واقعی از پنل
- اضافه شدن سکشن مراحل همکاری، تجربه مشتریان و پیش‌نمایش FAQ در صفحه اصلی
- اعمال واقعی فونت IRANSansX روی کل سایت به جای fallback قبلی
- بهبود رفتار منوی موبایل و وضعیت aria-expanded
- اضافه شدن WhiteNoise به تنظیمات پروژه برای پایداری بیشتر سرو استاتیک در استقرار


## Stage 9 - بازطراحی صفحات داخلی
- بازطراحی و تقویت صفحات features, about, pricing, plans, contact
- اضافه شدن KPI و FAQ به صفحه امکانات
- اضافه شدن timeline و فرهنگ همکاری به صفحه درباره ما
- اضافه شدن کارت‌های پلن پیشنهادی و FAQ قیمت‌گذاری
- اضافه شدن recommendation ها و CTA سازمانی به صفحه پلن‌ها
- اضافه شدن SLA/commitment و مراحل ارتباط به صفحه تماس با ما
- همگام‌سازی CSS جدید با staticfiles برای استقرار ساده‌تر

## Stage 10 - Content Hub, Article UX and FAQ Page

- بازطراحی حرفه‌ای صفحه وبلاگ به شکل مرکز دانش/Resource Center.
- اضافه شدن مسیرهای یادگیری، کارت‌های محتوایی، دسته‌بندی‌های آماری و ستون کناری وبلاگ.
- بازطراحی صفحه جزئیات مقاله با Hero اختصاصی، نوار پیشرفت مطالعه، خلاصه اجرایی، CTA انتهای مقاله، کپی لینک و ناوبری مقاله قبلی/بعدی.
- اضافه شدن صفحه مستقل سوالات متداول در مسیر `/faq/` با جستجو، فیلتر دسته‌بندی، کارت‌های هایلایت و CTA مشاوره.
- اضافه شدن لینک FAQ به فوتر و sitemap.
- بهبود JavaScript برای progress bar مقاله و کپی لینک.
- هماهنگ‌سازی فایل‌های CSS/JS در `staticfiles` برای استقرار روی سرور.
## Stage 11 - Homepage Detail Refinement

- بازطراحی جزئی‌تر صفحه اصلی با تمرکز روی هیرو، داشبورد مدیریتی و روایت محصول.
- اضافه شدن بخش مشکل/راهکار برای توضیح دقیق‌تر ارزش سیتباک در یکپارچه‌سازی داده‌ها.
- اضافه شدن سکشن هسته‌های اصلی محصول شامل CRM، اتوماسیون، ERP/مالی و TMO/OKR.
- بازسازی بخش تحلیل و داده به‌صورت Command Center با KPI cardها و نمودار CSS-only.
- بهبود مسیر همکاری با خروجی‌های قابل تحویل در هر مرحله.
- اضافه شدن بخش یکپارچگی و امنیت با تاکید روی API، دسترسی نقش‌محور، استقرار و گزارش سفارشی.
- اضافه شدن بخش شروع مرحله‌ای و پلن‌های پیشنهادی در صفحه اصلی.
- بهبود ریسپانسیو صفحه اصلی و هماهنگ‌سازی CSS در staticfiles برای استقرار سرور.

## Stage 12 + Stage 13 - Homepage deep polish, product tour, cockpit and conversion details

- ادامه بهبود صفحه اصلی قبل از شروع CMS، با حفظ کامل تغییرات قبلی.
- اضافه شدن سکشن «جریان واقعی کار در سیتباک» برای نمایش مسیر سرنخ، فروش، اجرا و گزارش.
- اضافه شدن بخش «ارزش سیتباک برای هر نقش» شامل مدیرعامل، فروش، عملیات و مالی.
- اضافه شدن تور تعاملی محصول با تب‌های داشبورد، CRM، اتوماسیون و گزارش‌ها.
- اضافه شدن سکشن «جزئیات اجرای حرفه‌ای» برای افزایش حس محصول واقعی و قابل اعتماد.
- اضافه شدن نوار ناوبری چسبان مخصوص صفحه اصلی برای پرش سریع بین بخش‌های مهم.
- اضافه شدن کارت‌های اطمینان در Hero برای جلسه تحلیل رایگان، توسعه مرحله‌ای و استقرار امن.
- اضافه شدن متای بصری روی Hero برای نمایش سریع ماژول‌های CRM، ERP، اتوماسیون و گزارش زنده.
- اضافه شدن سکشن «کنترل مدیریتی در لحظه» با داشبورد CSS-only، KPIهای زنده و پایپ‌لاین اجرایی.
- اضافه شدن سکشن «جزئیات تصمیم‌گیری» برای پاسخ به سوال‌های واقعی مدیران در صفحه اصلی.
- اضافه شدن سکشن اعتمادسازی قبل از CTA نهایی برای شروع مرحله‌ای، کاهش وابستگی به اکسل، رابط قابل فهم و توسعه آینده.
- اضافه شدن JavaScript سبک برای تب‌های تور محصول و active شدن خودکار ناوبری چسبان هنگام اسکرول.
- به‌روزرسانی CSS/JS و همگام‌سازی دوباره با `staticfiles` برای استقرار راحت‌تر.

## Stage 14 - Compact density and visual detail pass

- کاهش سراسری اندازه متن‌ها برای حرفه‌ای‌تر شدن نمای صفحه و دیده شدن جزئیات بیشتر در هر viewport.
- کاهش فاصله‌های عمودی سکشن‌ها، gap گریدها، padding کارت‌ها، دکمه‌ها، فرم‌ها و منوها.
- کوچک‌سازی کنترل‌شده آیکن‌ها، کارت‌های KPI، کارت‌های Hero، کارت‌های شناور و اجزای داشبورد CSS-only.
- افزایش عرض مفید container در دسکتاپ برای نمایش متراکم‌تر و کامل‌تر بخش‌ها.
- فشرده‌سازی سکشن‌های اصلی صفحه خانه شامل Hero، جریان کار، cockpit مدیریتی، تور محصول، کارت‌های نقش‌محور، CTA و فوتر.
- حفظ خوانایی متن فارسی در موبایل با سایزبندی جداگانه برای تبلت و موبایل.
- همگام‌سازی دوباره فایل CSS با `staticfiles` برای استقرار روی سرور.

## Stage 15/16 - Fine compact pricing + screenshot-based homepage precision

- عبارت «هزار / میلیون تومان» در صفحات قیمت و پلن‌ها به «میلیون تومان» اصلاح شد.
- صفحه اصلی بر اساس اسکرین‌شات واقعی خروجی دوباره پولیش شد.
- ارتفاع بخش هیرو، کارت‌های داشبورد، کارت‌های اعتماد و آمار کمتر و متعادل‌تر شد.
- سکشن‌های داخلی صفحه اصلی فشرده‌تر، ریزتر و پرجزئیات‌تر شدند بدون اینکه خوانایی از بین برود.
- فاصله‌های عمودی، اندازه کارت‌ها، hoverها، سایه‌ها و شعاع گوشه‌ها یکدست‌تر شد.
- کارت‌های سرویس، ماژول، تور محصول، جریان کار، داشبورد مدیریتی، CTA نهایی و فوتر ریزتنظیم شدند.
- CSS نسخه staticfiles با نسخه اصلی همگام‌سازی شد تا روی سرور خروجی جدید نمایش داده شود.


## Stage 17 - Pricing/Plans polish + balanced density
- اندازه متن‌ها و آیتم‌ها نسبت به Stage 16 کمی بزرگ‌تر شد تا خوانایی بهتر شود، بدون اینکه طراحی دوباره حجیم شود.
- صفحه قیمت‌ها با راهنمای انتخاب پلن، جدول خواناتر، کارت‌های کمک انتخاب و استایل حرفه‌ای‌تر بازطراحی شد.
- صفحه پلن‌ها با پیام واحد قیمت، معرفی جدول مقایسه، تراکم بهتر ستون‌ها و خوانایی بهتر اعداد اصلاح شد.
- واحد قیمت در جدول‌ها و پلن‌ها روی «میلیون تومان» یکدست شد.
- CSS اصلی و نسخه staticfiles همگام‌سازی شد.

## Stage 18 - بازطراحی حرفه‌ای صفحه امکانات
- صفحه امکانات از حالت لیست ساده‌تر به صفحه محصول‌محور و سناریومحور ارتقا پیدا کرد.
- Hero صفحه امکانات بازطراحی شد و یک نمای CSS-only از مرکز کنترل امکانات اضافه شد.
- بخش تب‌دار «هسته‌های اصلی محصول» برای CRM، اتوماسیون، گزارش‌ها و مالی/ERP اضافه شد.
- ماتریس ارزش امکانات برای نقش‌های مختلف سازمانی اضافه شد.
- سناریوهای آماده اجرا برای لید تا قرارداد، درخواست داخلی تا تایید، و پروژه تا تحویل اضافه شدند.
- بخش قبل/بعد از سیتباک برای نمایش اثر واقعی امکانات اضافه شد.
- کارت‌های امنیت، اتصال‌پذیری، توسعه‌پذیری و پشتیبانی اجرا اضافه شدند.
- CSS و JS جدید با staticfiles همگام‌سازی شد.

## Stage 19 - پولیش صفحات درباره ما، تماس و مطالعه موردی
- ادامه از Stage 18 بدون rollback و با حفظ لوگو، فونت local، RTL، طراحی تیره/طلایی، WhiteNoise، Ajax forms، وبلاگ، FAQ و SEO.
- صفحه درباره ما بازطراحی محتوایی/بصری شد: Hero با proof chips، کارت‌های شناور، سیستم کاری سیتباک، تیم، ماموریت و نحوه همکاری حرفه‌ای‌تر شد.
- صفحه تماس حرفه‌ای‌تر شد: مسیر سریع ارتباط، راهنمای اطلاعات لازم قبل از تماس، کارت‌های ارتباطی، فرم برجسته و فرآیند بعد از ارسال فرم اضافه شد.
- صفحه مطالعه موردی پولیش شد: Badgeهای Hero، نقشه اجرای پروژه، خروجی‌های تحویل‌شده، نتایج، رسانه‌ها و CTA نهایی تقویت شد.
- داده‌های محتوایی جدید بدون migration و داخل `landing/data.py` اضافه شدند.
- CSS اصلی و نسخه `staticfiles` همگام‌سازی شد تا ZIP روی سرور خروجی جدید را نمایش دهد.

## Stage 20 - Homepage story hero image
- Replaced the homepage hero visual with the provided Sitbuk story banner image.
- Added `landing/static/landing/images/home_story_sitbuk.png` and mirrored it into `staticfiles/landing/images/`.
- Simplified the hero visual block so the first screen now shows the supplied image in a fitted, responsive frame.

## Stage 21 - About page real board member photos
- Replaced the About page board member images for `مهندس پویا فریدی` and `دکتر مهدی فرامرزیان` with the provided transparent PNG photos.
- Kept the existing template/data structure intact by updating `about_member_pouya.png` and `about_member_farmarzian.png`.
- Added the original Persian-named image files to static assets for traceability: `فریدی.png` and `فرامرزیان.png`.
- Added responsive fitting CSS so the transparent portraits sit cleanly inside the About page leader cards without awkward cropping.

## Stage 22 - Compact homepage
- Shortened the homepage significantly by removing repeated long sections, the sticky anchor navigation, FAQ/blog previews, extra analytics blocks, long role/outcome sections, and duplicate final CTA content.
- Kept a concise homepage structure: hero, quick proof cards, compact stats, three core services, product showcase, four key modules, and a short cooperation workflow.
- Preserved the Stage 20 hero story image and Stage 21 about-page board photos.
- Added compact responsive CSS rules while keeping existing design language, RTL layout, local fonts, dark/gold visual identity, WhiteNoise/static setup, SEO pages, forms, blog, FAQ, pricing, and all previous assets.


## Stage 23 - Homepage CMS from admin
- Added admin-manageable CMS models for the compact homepage without rolling back Stage 20/21/22 changes.
- Added `HomeHeroContent` for managing Hero eyebrow, kicker chips, title parts, description, buttons, and hero image static path.
- Added `HomeContentItem` for managing homepage quick proof cards, stats, core services, product showcase points, modules, and cooperation workflow steps.
- Added migrations `0004_homepage_cms.py` and `0005_seed_homepage_cms.py` with seeded content matching the current compact homepage.
- Updated the homepage view to merge CMS content over the static fallback safely; if migrations are not applied yet, the page still falls back to the existing static data instead of crashing.
- Updated the homepage template to use CMS-driven Hero text, buttons, image, and section items.
- Updated the included SQLite database with the new CMS tables and seeded rows for immediate local testing.

## Stage 24 - Internal pages CMS from admin
- Added CMS models for internal static pages without rolling back Stage 20/21/22/23 changes.
- Added `PageContent` to manage title, kicker, description, SEO fields, hero image path, and active status for Features, About, Case Study, Pricing, Plans, FAQ, and Contact pages.
- Added `PageContentItem` to manage reusable section rows/cards for internal pages, including About proof/stat/timeline/leaders, Contact route/commitment/process blocks, Case Study facts/results/deliverables, Features stats/use cases/security points, Pricing highlights/assurances, Plans recommendations/badges, and FAQ highlights/categories.
- Added migrations `0006_internal_pages_cms.py` and `0007_seed_internal_pages_cms.py` with seeded content matching the current site copy.
- Updated internal page views to merge CMS content over static fallback safely; if migrations are not applied yet, the pages still render from existing static data.
- Updated Django admin with searchable/filterable management screens for internal page settings and content items.
- Updated the bundled SQLite database with the new CMS tables, seed rows, and migration records for immediate local testing.

## Stage 25 - Lead and Form Management
- Added sales pipeline fields to `LeadRequest`: status, priority, owner, internal notes, follow-up date, last-contact date, page URL, referrer, UTM source/campaign, IP, user-agent, and updated timestamp.
- Added tracking/status fields to `ContactMessage`: status, priority, internal note, source page, page URL, referrer, IP, user-agent, and updated timestamp.
- Added migration `0008_lead_pipeline_tracking.py` and updated the bundled SQLite database.
- Improved admin management for leads and contact messages with list filters, editable status/priority fields, internal notes, follow-up controls, and bulk status actions.
- Added XLSX export actions for selected leads/contact messages; if `openpyxl` is not installed, the export safely falls back to UTF-8 CSV.
- Added hidden tracking fields to lead/contact forms and saved source page, page URL, referrer, and UTM data on submission.
- Added safe email notification hooks using the configured site support email when email settings are available.

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

## Stage 26.1 - Fix Django index name length
- Shortened three manually named indexes added for lead/contact tracking so they comply with Django's 30-character index-name limit.
- Updated both `landing/models.py` and `landing/migrations/0008_lead_pipeline_tracking.py` to avoid `models.E034` during `manage.py check` / `migrate`.

## Stage 26.2 - تغییر نقشه راه به داشبورد ادمین اختصاصی

- تصمیم محصولی جدید ثبت شد: مدیریت محتوای سیتباک نباید بر پایه پنل پیش‌فرض Django Admin باشد.
- مسیر توسعه از این نقطه به بعد به سمت داشبورد اختصاصی مدیریت تغییر کرد.
- فایل `CUSTOM_ADMIN_DASHBOARD_ROADMAP_FA.md` اضافه شد و مراحل Stage 27 تا Stage 36 برای پنل جدید تعریف شدند.
- مدل‌ها و CMSهای Stage 23 تا Stage 26 حذف نمی‌شوند؛ در مراحل بعدی به صفحات اختصاصی پنل جدید وصل خواهند شد.
- Django Admin فقط می‌تواند به عنوان ابزار اضطراری/فنی باقی بماند، نه پنل اصلی مدیریت سایت.

## Stage 27 - پایه داشبورد ادمین اختصاصی سیتباک

- اسکلت پنل اختصاصی مدیریت در مسیر `/dashboard/` اضافه شد و مسیرهای `/dashboard/login/` و `/dashboard/logout/` ایجاد شدند.
- پنل جدید از ظاهر و تجربه Django Admin مستقل است و با تم RTL تیره/طلایی، فونت local و CSS اختصاصی ساخته شد.
- دسترسی پنل با احراز هویت Django و شرط `is_staff`/`is_superuser` محافظت شد.
- داشبورد اولیه شامل کارت‌های خلاصه برای لیدهای باز، پیام‌های جدید، مقاله‌های منتشرشده و صفحات CMS فعال اضافه شد.
- سایدبار مرحله‌ای برای انتقال قابلیت‌ها به پنل جدید اضافه شد: صفحه اول، صفحات داخلی، لیدها، بلاگ/FAQ، SEO، رسانه‌ها و دسترسی‌ها.
- صفحات placeholder نقشه راه برای بخش‌های آینده ساخته شد تا از Stage 28 به بعد قابلیت‌ها صفحه‌به‌صفحه به همین layout متصل شوند.
- `robots.txt` به‌روزرسانی شد تا مسیر `/dashboard/` ایندکس نشود.
- هیچ مدل یا CMS قبلی حذف نشد؛ Stage 23 تا Stage 26 فقط به پنل جدید وصل خواهند شد.

## Stage 28 - Custom Dashboard Homepage CMS
- صفحه `/dashboard/home/` از placeholder به صفحه واقعی مدیریت صفحه اول تبدیل شد.
- فرم ویرایش `HomeHeroContent` داخل داشبورد اختصاصی اضافه شد: تیتر، توضیح، برچسب‌ها، دکمه‌ها، route دکمه دوم، مسیر تصویر و وضعیت فعال.
- مدیریت کامل `HomeContentItem` داخل داشبورد اضافه شد: افزودن آیتم، ویرایش آیتم، فعال/غیرفعال کردن و حذف آیتم.
- آیتم‌های صفحه اول بر اساس بخش‌ها گروه‌بندی شدند: مزیت‌های سریع، آمارها، خدمات، نمای محصول، ماژول‌ها و مراحل همکاری.
- کارت‌های خلاصه و پیش‌نمایش صفحه اول به پنل اضافه شد.
- CSS اختصاصی فرم‌ها و ویرایشگر آیتم‌ها در `admin-dashboard.css` اضافه و با `staticfiles` همگام شد.
- این مرحله migration جدید ندارد و از مدل‌های Stage 23 استفاده می‌کند.

## Stage 29 - Internal Pages CMS inside Custom Dashboard
- مسیر `/dashboard/pages/` از placeholder به صفحه واقعی مدیریت صفحات داخلی تبدیل شد.
- فرم اختصاصی `PageContent` داخل داشبورد اضافه شد تا عنوان، توضیح، Hero، SEO، canonical، robots، OG و Schema هر صفحه از پنل جدید مدیریت شود.
- مدیریت `PageContentItem` برای صفحات داخلی اضافه شد: افزودن آیتم، ویرایش آیتم، فعال/غیرفعال‌سازی و حذف.
- صفحات قابل مدیریت شامل امکانات، درباره ما، مطالعه موردی، قیمت‌ها، پلن‌ها، FAQ و تماس با ما هستند.
- صفحه مدیریت داخلی دارای tab برای انتخاب صفحه، کارت‌های KPI، پیش‌نمایش سریع و راهنمای کد سکشن‌های هر صفحه است.
- CSS داشبورد برای tabهای صفحات داخلی، فرم‌های SEO و مدیریت سکشن‌ها تکمیل شد و با `staticfiles` همگام شد.
- این مرحله migration جدید ندارد و از مدل‌های `PageContent` و `PageContentItem` ساخته‌شده در Stage 24 استفاده می‌کند.

## Stage 30 - مدیریت لیدها و پیام‌ها در داشبورد اختصاصی
- مسیر `/dashboard/leads/` از حالت placeholder خارج شد و به CRM سبک اختصاصی تبدیل شد.
- لیست لیدها و پیام‌های تماس با tab جداگانه، جستجو و فیلتر وضعیت/اولویت/صفحه مبدا اضافه شد.
- تغییر وضعیت و اولویت گروهی برای لیدها و پیام‌ها اضافه شد.
- صفحه جزئیات لید با مدیریت وضعیت، اولویت، مسئول پیگیری، زمان پیگیری بعدی، آخرین تماس و یادداشت داخلی اضافه شد.
- صفحه جزئیات پیام تماس با مدیریت وضعیت، اولویت و یادداشت داخلی اضافه شد.
- خروجی Excel/CSV برای لیدها و پیام‌ها از داخل پنل اختصاصی اضافه شد.
- این مرحله migration جدید ندارد و از مدل‌های Stage 25 استفاده می‌کند.


## Stage 31 - Blog and FAQ custom dashboard
- Continued from Stage 30 without rollback.
- Replaced the placeholder custom dashboard content section with a real management interface at `/dashboard/content/`.
- Added custom-dashboard blog management: search, category filter, publication filter, featured filter, bulk publish/draft, bulk featured/normal, list view and edit/create pages.
- Added blog post editor pages at `/dashboard/content/posts/new/` and `/dashboard/content/posts/<id>/` with full content, summary, slug, category, reading time, publication date, featured/published status and SEO fields.
- Added custom-dashboard FAQ management: search, active/inactive filter, bulk active/inactive, list view and edit/create pages.
- Added FAQ editor pages at `/dashboard/content/faqs/new/` and `/dashboard/content/faqs/<id>/` with question, answer, sort order and active status.
- Added Stage 31 dashboard styling to `admin-dashboard.css` and mirrored it into `staticfiles`.
- No new migration was required; the stage uses existing `BlogPost` and `FAQItem` models.

## Stage 32 - Pricing and Plans Custom Dashboard
- Added a dedicated custom dashboard page for pricing and plans management at `/dashboard/pricing/`.
- Added Stage 32 navigation item to the custom Sitbuk dashboard.
- Pricing and plans CMS now has focused tabs for `pricing` and `plans` instead of relying only on the generic internal-pages editor.
- The new page manages page settings, SEO fields, section items, active/inactive state, ordering, deletion and preview links.
- Added field usage guides for pricing sections: `pricing_highlights`, `pricing_faqs`, `assurances`, `plan_recommendations`, and `plan_badges`.
- Preserved all previous CMS models and public-page fallbacks without rollback.

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
## Stage 32.4 - Demo request workflow foundation
- Added `DemoRequest` model and migration `0010_demo_request.py` for collecting demo access requests.
- Added `/forms/demo/` endpoint and AJAX modal form for demo requests.
- Connected homepage/header demo CTAs to the modal form instead of sending users directly to a generic contact section.
- Added tracking fields, UTM fields, demo type selection, status workflow, temporary token and future demo access URL fields.
- Added `DEMO_REQUEST_WORKFLOW_FA.md` for the next integration steps.

## Stage 32.5 - Secure demo systems access
- Added secure temporary demo access page at `/demo/<token>/`.
- Added target launch routes for Behnico and Sitbuk demo copies.
- Added environment variables for demo base URLs and token lifetime.
- Demo requests now generate a temporary access URL and redirect users to the demo selection page after form submission.
- Added tracking fields for demo link expiry, launch count, last target, and entered timestamp.
- Added `DEMO_SYSTEM_INTEGRATION_FA.md`.


## Stage 32.6 - Demo requests dashboard + homepage video theme alignment
- Added a dedicated custom dashboard section for demo requests at `/dashboard/demos/`.
- Added demo request list, filters, bulk status/priority actions, detail page, secure demo link preview, link regeneration and link-sent tracking.
- Added Excel/CSV export for demo requests.
- Added dashboard routes: `/dashboard/demos/`, `/dashboard/demos/export/`, `/dashboard/demos/<id>/`.
- Updated the custom dashboard sidebar to include “درخواست‌های دمو”.
- Aligned the four homepage video sections with the site dark/gold Sitbuk theme instead of the previous light/green treatment.
- Preserved all previous Stage 32.1 to Stage 32.5 changes without rollback.

## Stage 32.7 - Bale Bot Infrastructure
- Added Bale bot infrastructure for Sitbuk landing.
- Added `BaleBotSettings`, `BaleBotConversation`, and `BaleBotMessage`.
- Added `/bale/webhook/` and `/bale/webhook/<secret>/` endpoints.
- Added `python manage.py poll_bale` for polling mode.
- Bot can register consultation leads as `LeadRequest` and demo requests as `DemoRequest`.
- Bot creates secure demo access links for Bale users.
- Added dashboard roadmap entry for the Bale bot section.
## Stage 32.8 - Bale bot custom dashboard management
- Added a real custom dashboard page for the Bale bot at `/dashboard/bale/`.
- Added Bale conversation filtering by query, status, and conversation state.
- Added Bale bot settings management inside the custom dashboard, including enabled flag, group mention behavior, bot username, and main reply texts.
- Added Bale conversation detail page with full message thread, conversation metadata editing, flow reset, related leads/demo requests, and operator reply sending through the Bale API.
- Added conversation export at `/dashboard/bale/export/`.
- Updated dashboard navigation and roadmap to mark Stage 32.8 as completed.
- Fixed the Stage 32.6 demo dashboard templates to use the correct dashboard content block.

## Stage 32.9 - Homepage video poster refresh
- Replaced the homepage hero video poster with uploaded cover image #1.
- Replaced the four lower homepage video posters with uploaded cover images #2 to #5.
- Rewrote the four homepage video section copy blocks and benefit items to match the text shown on the uploaded posters.
- Reduced the title/body text size of the four lower video sections for a cleaner visual balance.

## Stage 32.10 - About page video cover and theming
- Replaced the about-page video poster with the uploaded story cover image.
- Rewrote the about video section copy based on the cover text: story of Sitbuk and how a concern became a product.
- Aligned the about video block with the dark/gold site theme and refined title/body/item text sizes.

## Stage 32.11 - Correct homepage video cover mapping
- Fixed the top homepage video poster to always use uploaded cover #1, independent of CMS hero image values.
- Re-copied uploaded files `1.jpg` through `5.jpg` directly into `landing/static/landing/images/video_posters/` and mirrored them to `staticfiles`.
- Confirmed cover #5 is assigned to the final homepage video section and its copy remains aligned with the integrated management software introduction.

## Stage 32.12 - Homepage poster mapping correction
- Reassigned the cover titled "معرفی نرم‌افزار مدیریت یکپارچه سیت‌باک" to the first/homepage hero video poster.
- Replaced the fifth/lower final section cover with the newly uploaded image about financial savings at the purchase stage.
- Rewrote the last lower homepage video section copy and benefit items to match the new financial-savings cover.

## Stage 32.13 - Homepage hero poster final fix
- Replaced the top homepage video poster with the latest uploaded cover image for the main hero video only.
- Kept the four lower homepage video sections unchanged.

