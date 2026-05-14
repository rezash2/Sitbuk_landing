# فایل‌های ویدیویی سایت سیت‌باک

این فایل فقط راهنمای داخلی مسیر فایل‌های ویدیویی است و هیچ متن راهنما یا پیام آماده‌سازی در صفحات عمومی سایت نمایش داده نمی‌شود.

## مسیر فایل‌ها

فایل‌های ویدیویی نهایی باید در مسیر زیر قرار بگیرند:

```text
landing/static/landing/videos/
```

نام فایل‌های استفاده‌شده در قالب‌ها:

```text
home-hero.mp4
home-section-1.mp4
home-section-2.mp4
home-section-3.mp4
home-section-4.mp4
about-story.mp4
```

کاورهای فعلی ویدیوها از مسیر زیر خوانده می‌شوند:

```text
landing/static/landing/images/video_posters/
```

پس از تغییر فایل‌های ویدیویی در محیط تولید، در صورت استفاده از static collection، دستور زیر اجرا شود:

```bash
python manage.py collectstatic
```
