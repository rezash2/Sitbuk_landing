# فایل‌های ویدیویی صفحه اصلی - Stage 32.1

برای نمایش ویدیو اصلی صفحه اول، فایل ویدیوی خودت را با همین نام در مسیر زیر قرار بده:

```text
landing/static/landing/videos/home-hero.mp4
```

اگر روی سرور از `collectstatic` استفاده می‌کنی، بعد از جایگذاری ویدیو اجرا کن:

```bash
python manage.py collectstatic --noinput
```

Poster ویدیو فعلاً از تصویر Hero موجود سایت خوانده می‌شود و بعداً در مراحل بعدی می‌توانیم مدیریت آن را هم داخل داشبورد اختصاصی اضافه کنیم.

## Stage 32.2 - چهار ویدیوی معرفی در صفحه اصلی

علاوه بر ویدیوی اصلی Hero، چهار سکشن ویدیویی جدید در صفحه اول اضافه شد. برای فعال‌شدن ویدیوها، فایل‌ها را با نام‌های زیر قرار بده:

```text
landing/static/landing/videos/home-section-1.mp4
landing/static/landing/videos/home-section-2.mp4
landing/static/landing/videos/home-section-3.mp4
landing/static/landing/videos/home-section-4.mp4
```

Poster هر ویدیو فعلاً از تصاویر موجود پروژه خوانده می‌شود تا صفحه قبل از آپلود ویدیو خراب نشود. بعداً می‌توانیم برای هر ویدیو poster اختصاصی هم از داشبورد یا فایل static تنظیم کنیم.

پیشنهاد محتوایی ویدیوها:

1. `home-section-1.mp4` — مشاوره، تحلیل نیاز و مسیر شروع
2. `home-section-2.mp4` — CRM، لیدها، مشتریان و قیف فروش
3. `home-section-3.mp4` — اتوماسیون، فرم‌ها و گردش‌کارها
4. `home-section-4.mp4` — داشبورد، گزارش مدیریتی و تصمیم‌گیری

## Stage 32.3 - ویدیوی صفحه درباره ما
برای صفحه درباره ما، فایل زیر را بعداً جایگذاری کن:

```text
landing/static/landing/videos/about-story.mp4
```

کاور پیش‌فرض فعلاً این فایل است:

```text
landing/static/landing/images/about_workspace.png
```

بعد از جایگذاری ویدیو روی سرور اجرا کن:

```bash
python manage.py collectstatic --noinput
```

## اصلاح Stage 32.11
- کاور ویدیوی بالایی صفحه اصلی باید همیشه فایل `landing/static/landing/images/video_posters/home_video_1.jpg` باشد.
- کاور چهار ویدیوی پایین به‌ترتیب از `home_video_2.jpg` تا `home_video_5.jpg` خوانده می‌شود.
- فایل‌های اصلی ارسالی `1.jpg` تا `5.jpg` مستقیماً با همین ترتیب داخل پروژه کپی شدند.

## اصلاح Stage 32.14
- طبق درخواست، ویدیو و کاور دو بخش «یکپارچگی سیستم‌ها» و «پیاده‌سازی منعطف / شخصی‌سازی» با هم جابه‌جا شد.
- بخش «یکپارچگی سیستم‌ها» اکنون از `landing/videos/home-section-3.mp4` و کاور `landing/images/video_posters/home_video_4.jpg` استفاده می‌کند.
- بخش «شخصی‌سازی» اکنون از `landing/videos/home-section-1.mp4` و کاور `landing/images/video_posters/home_video_2.jpg` استفاده می‌کند.
- دو بخش دیگر پایین صفحه اصلی و ویدیوی بالایی Hero بدون تغییر باقی ماندند.
