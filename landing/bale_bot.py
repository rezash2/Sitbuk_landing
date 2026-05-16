from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from .models import BaleBotConversation, BaleBotMessage, BaleBotSettings, DemoRequest, LeadRequest


MAIN_MENU = {
    'keyboard': [
        [{'text': 'درخواست مشاوره'}, {'text': 'مشاهده دمو'}],
        [{'text': 'وضعیت درخواست'}, {'text': 'راه‌های تماس'}],
    ],
    'resize_keyboard': True,
}

DEMO_TYPE_MENU = {
    'keyboard': [
        [{'text': 'دمو سیتباک'}, {'text': 'دمو بهنیکو'}],
        [{'text': 'هر دو دمو'}],
        [{'text': 'لغو'}],
    ],
    'resize_keyboard': True,
}

CANCEL_WORDS = {'لغو', 'بازگشت', 'منو', '/start', 'شروع'}


@dataclass
class BaleIncomingMessage:
    update_id: int | None
    message_id: str
    chat_id: str
    chat_type: str
    bale_user_id: str
    display_name: str
    username: str
    text: str
    raw: dict[str, Any]


def _configured_bot_token() -> str:
    try:
        db_token = (BaleBotSettings.objects.order_by('id').values_list('bot_token', flat=True).first() or '').strip()
        if db_token:
            return db_token
    except Exception:
        pass
    return (getattr(settings, 'BALE_BOT_TOKEN', '') or '').strip()


class BaleBotAPI:
    def __init__(self, token: str | None = None):
        self.token = (token or _configured_bot_token()).strip()
        self.api_base = getattr(settings, 'BALE_BOT_API_BASE', 'https://tapi.bale.ai').rstrip('/')

    @property
    def is_configured(self) -> bool:
        return bool(self.token)

    def _request(self, method: str, payload: dict[str, Any] | None = None, timeout: int = 25) -> dict[str, Any]:
        if not self.is_configured:
            return {'ok': False, 'description': 'BALE_BOT_TOKEN is not configured'}
        url = f'{self.api_base}/bot{self.token}/{method}'
        data = json.dumps(payload or {}, ensure_ascii=False).encode('utf-8')
        request = urllib.request.Request(
            url,
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST',
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                body = response.read().decode('utf-8')
                return json.loads(body or '{}')
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
            return {'ok': False, 'description': str(exc)}

    def send_message(self, chat_id: str, text: str, reply_markup: dict[str, Any] | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {
            'chat_id': chat_id,
            'text': text,
        }
        if reply_markup:
            payload['reply_markup'] = reply_markup
        return self._request('sendMessage', payload)

    def get_updates(self, offset: int | None = None, limit: int = 50, timeout: int = 25) -> dict[str, Any]:
        payload: dict[str, Any] = {'limit': limit, 'timeout': timeout}
        if offset:
            payload['offset'] = offset
        return self._request('getUpdates', payload, timeout=timeout + 10)

    def get_me(self) -> dict[str, Any]:
        return self._request('getMe', {})


def normalize_phone(value: str) -> str:
    value = value.strip()
    value = value.replace(' ', '').replace('-', '')
    trans = str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩', '01234567890123456789')
    value = value.translate(trans)
    return value


def is_valid_email(value: str) -> bool:
    value = value.strip()
    if value in {'-', 'ندارم', 'خالی'}:
        return True
    return bool(re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', value))


def _site_url() -> str:
    return getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000').rstrip('/')


def _demo_access_hours() -> int:
    try:
        return max(1, int(getattr(settings, 'DEMO_ACCESS_TOKEN_HOURS', 72)))
    except (TypeError, ValueError):
        return 72


def _demo_url(demo_request: DemoRequest) -> str:
    return f"{_site_url()}{reverse('demo_access', kwargs={'token': demo_request.demo_access_token})}"


def _extract_message(update: dict[str, Any]) -> BaleIncomingMessage | None:
    message = update.get('message') or update.get('edited_message') or {}
    if not message:
        callback = update.get('callback_query') or {}
        message = callback.get('message') or {}
        if callback.get('data'):
            message = {**message, 'text': callback.get('data')}
    if not message:
        return None

    chat = message.get('chat') or {}
    sender = message.get('from') or update.get('from') or {}
    chat_id = str(chat.get('id') or sender.get('id') or '')
    if not chat_id:
        return None
    first_name = sender.get('first_name') or ''
    last_name = sender.get('last_name') or ''
    display_name = f'{first_name} {last_name}'.strip() or chat.get('title') or sender.get('username') or chat_id
    return BaleIncomingMessage(
        update_id=update.get('update_id'),
        message_id=str(message.get('message_id') or ''),
        chat_id=chat_id,
        chat_type=str(chat.get('type') or 'private'),
        bale_user_id=str(sender.get('id') or ''),
        display_name=display_name,
        username=str(sender.get('username') or ''),
        text=str(message.get('text') or message.get('caption') or '').strip(),
        raw=update,
    )


def _conversation_for(incoming: BaleIncomingMessage) -> BaleBotConversation:
    conversation, _created = BaleBotConversation.objects.get_or_create(
        chat_id=incoming.chat_id,
        defaults={
            'bale_user_id': incoming.bale_user_id,
            'chat_type': incoming.chat_type,
            'display_name': incoming.display_name,
            'username': incoming.username,
            'last_seen_at': timezone.now(),
        },
    )
    conversation.bale_user_id = incoming.bale_user_id or conversation.bale_user_id
    conversation.chat_type = incoming.chat_type or conversation.chat_type
    conversation.display_name = incoming.display_name or conversation.display_name
    conversation.username = incoming.username or conversation.username
    conversation.last_text = incoming.text[:1000]
    conversation.last_seen_at = timezone.now()
    conversation.save(update_fields=['bale_user_id', 'chat_type', 'display_name', 'username', 'last_text', 'last_seen_at', 'updated_at'])
    return conversation


def _store_message(conversation: BaleBotConversation, direction: str, text: str, raw: dict[str, Any] | None = None, update_id: int | None = None, message_id: str = '', related_lead=None, related_demo=None) -> BaleBotMessage:
    return BaleBotMessage.objects.create(
        conversation=conversation,
        bale_update_id=update_id,
        bale_message_id=message_id,
        direction=direction,
        text=text or '',
        raw_payload=raw or {},
        related_lead=related_lead,
        related_demo=related_demo,
    )


def _reply(conversation: BaleBotConversation, text: str, keyboard: dict[str, Any] | None = None) -> dict[str, Any]:
    result = BaleBotAPI().send_message(conversation.chat_id, text, reply_markup=keyboard)
    _store_message(conversation, BaleBotMessage.DIRECTION_OUT, text, raw=result)
    return result


def _reset_to_menu(conversation: BaleBotConversation, bot_settings: BaleBotSettings, text: str | None = None):
    conversation.reset_flow()
    conversation.save(update_fields=['state', 'session_data', 'updated_at'])
    _reply(conversation, text or bot_settings.welcome_text, MAIN_MENU)


def _should_ignore_group_message(incoming: BaleIncomingMessage, bot_settings: BaleBotSettings) -> bool:
    if incoming.chat_type not in {'group', 'supergroup'}:
        return False
    if not bot_settings.only_respond_to_mentions_in_groups:
        return False
    username = (bot_settings.bot_username or getattr(settings, 'BALE_BOT_USERNAME', '') or '').strip().lstrip('@')
    if not username:
        return False
    return f'@{username}'.lower() not in incoming.text.lower()


def _clean_group_mention(text: str, bot_settings: BaleBotSettings) -> str:
    username = (bot_settings.bot_username or getattr(settings, 'BALE_BOT_USERNAME', '') or '').strip().lstrip('@')
    if username:
        return text.replace(f'@{username}', '').strip()
    return text


def _start_consultation(conversation: BaleBotConversation):
    conversation.state = BaleBotConversation.STATE_CONSULT_NAME
    conversation.session_data = {}
    conversation.save(update_fields=['state', 'session_data', 'updated_at'])
    _reply(conversation, 'برای ثبت درخواست مشاوره، نام و نام خانوادگی را وارد کنید:', {'keyboard': [[{'text': 'لغو'}]], 'resize_keyboard': True})


def _start_demo(conversation: BaleBotConversation):
    conversation.state = BaleBotConversation.STATE_DEMO_NAME
    conversation.session_data = {}
    conversation.save(update_fields=['state', 'session_data', 'updated_at'])
    _reply(conversation, 'برای مشاهده دمو، نام و نام خانوادگی را وارد کنید:', {'keyboard': [[{'text': 'لغو'}]], 'resize_keyboard': True})


def _start_status(conversation: BaleBotConversation):
    conversation.state = BaleBotConversation.STATE_STATUS_PHONE
    conversation.session_data = {}
    conversation.save(update_fields=['state', 'session_data', 'updated_at'])
    _reply(conversation, 'برای بررسی وضعیت، شماره موبایلی که با آن درخواست ثبت کرده‌اید را وارد کنید:', {'keyboard': [[{'text': 'لغو'}]], 'resize_keyboard': True})


def _contact_text() -> str:
    try:
        from .models import SiteSettings
        site = SiteSettings.get_solo()
        phone = site.sales_phone or site.support_phone or 'در سایت ثبت نشده'
        email = site.support_email or 'در سایت ثبت نشده'
        hours = site.working_hours or 'ساعات کاری شرکت'
    except Exception:
        phone = 'در سایت ثبت نشده'
        email = 'در سایت ثبت نشده'
        hours = 'ساعات کاری شرکت'
    return f'راه‌های تماس با سیتباک:\nتلفن: {phone}\nایمیل: {email}\nزمان پاسخ‌گویی: {hours}'


def _parse_demo_type(text: str) -> str | None:
    if 'هر' in text or 'دو' in text:
        return DemoRequest.DEMO_BOTH
    if 'بهنیکو' in text:
        return DemoRequest.DEMO_BEHNICO
    if 'سیتباک' in text or 'سیت باک' in text:
        return DemoRequest.DEMO_SITBUK
    return None


def _handle_consultation_flow(conversation: BaleBotConversation, text: str, bot_settings: BaleBotSettings):
    data = dict(conversation.session_data or {})
    state = conversation.state
    if state == BaleBotConversation.STATE_CONSULT_NAME:
        if len(text) < 3:
            _reply(conversation, 'نام خیلی کوتاه است. لطفاً نام و نام خانوادگی را کامل وارد کنید:')
            return
        data['full_name'] = text
        conversation.state = BaleBotConversation.STATE_CONSULT_PHONE
        prompt = 'شماره موبایل را وارد کنید:'
    elif state == BaleBotConversation.STATE_CONSULT_PHONE:
        phone = normalize_phone(text)
        if len(phone) < 8:
            _reply(conversation, 'شماره موبایل معتبر نیست. لطفاً دوباره وارد کنید:')
            return
        data['phone'] = phone
        conversation.phone = phone
        conversation.state = BaleBotConversation.STATE_CONSULT_COMPANY
        prompt = 'نام شرکت را وارد کنید. اگر شرکت ندارید، «ندارم» بنویسید:'
    elif state == BaleBotConversation.STATE_CONSULT_COMPANY:
        data['company'] = '' if text in {'ندارم', '-'} else text
        conversation.company = data['company']
        conversation.state = BaleBotConversation.STATE_CONSULT_EMAIL
        prompt = 'ایمیل را وارد کنید. اگر ندارید، «ندارم» بنویسید:'
    elif state == BaleBotConversation.STATE_CONSULT_EMAIL:
        if not is_valid_email(text):
            _reply(conversation, 'فرمت ایمیل درست نیست. دوباره وارد کنید یا «ندارم» بنویسید:')
            return
        data['email'] = '' if text in {'ندارم', '-', 'خالی'} else text
        conversation.email = data['email']
        conversation.state = BaleBotConversation.STATE_CONSULT_NOTE
        prompt = 'توضیح کوتاهی درباره نیازتان بنویسید. برای رد شدن، «رد» را بفرستید:'
    elif state == BaleBotConversation.STATE_CONSULT_NOTE:
        data['note'] = '' if text in {'رد', '-', 'ندارم'} else text
        lead = LeadRequest.objects.create(
            full_name=data.get('full_name', conversation.display_name),
            phone=data.get('phone', conversation.phone),
            company=data.get('company', ''),
            email=data.get('email', ''),
            note=data.get('note', ''),
            source_page='bale_bot',
            page_url=f'bale://chat/{conversation.chat_id}',
            referrer='Bale Bot',
            user_agent='Bale Bot',
            priority=LeadRequest.PRIORITY_NORMAL,
        )
        _store_message(conversation, BaleBotMessage.DIRECTION_SYSTEM, 'Lead created from Bale bot', related_lead=lead)
        conversation.reset_flow()
        conversation.save(update_fields=['state', 'session_data', 'phone', 'email', 'company', 'updated_at'])
        _reply(conversation, f'{bot_settings.consultation_done_text}\n\nکد پیگیری مشاوره: #{lead.id}', MAIN_MENU)
        return
    else:
        _reset_to_menu(conversation, bot_settings)
        return
    conversation.session_data = data
    conversation.save(update_fields=['state', 'session_data', 'phone', 'email', 'company', 'updated_at'])
    _reply(conversation, prompt)


def _handle_demo_flow(conversation: BaleBotConversation, text: str, bot_settings: BaleBotSettings):
    data = dict(conversation.session_data or {})
    state = conversation.state
    if state == BaleBotConversation.STATE_DEMO_NAME:
        if len(text) < 3:
            _reply(conversation, 'نام خیلی کوتاه است. لطفاً نام و نام خانوادگی را کامل وارد کنید:')
            return
        data['full_name'] = text
        conversation.state = BaleBotConversation.STATE_DEMO_PHONE
        prompt = 'شماره موبایل را وارد کنید:'
    elif state == BaleBotConversation.STATE_DEMO_PHONE:
        phone = normalize_phone(text)
        if len(phone) < 8:
            _reply(conversation, 'شماره موبایل معتبر نیست. لطفاً دوباره وارد کنید:')
            return
        data['phone'] = phone
        conversation.phone = phone
        conversation.state = BaleBotConversation.STATE_DEMO_EMAIL
        prompt = 'ایمیل کاری یا شخصی را وارد کنید:'
    elif state == BaleBotConversation.STATE_DEMO_EMAIL:
        if not is_valid_email(text) or text in {'ندارم', '-', 'خالی'}:
            _reply(conversation, 'برای ارسال لینک دمو، ایمیل لازم است. لطفاً ایمیل معتبر وارد کنید:')
            return
        data['email'] = text
        conversation.email = text
        conversation.state = BaleBotConversation.STATE_DEMO_COMPANY
        prompt = 'نام شرکت را وارد کنید:'
    elif state == BaleBotConversation.STATE_DEMO_COMPANY:
        if len(text) < 2 or text in {'ندارم', '-'}:
            _reply(conversation, 'برای درخواست دمو، نام شرکت لازم است. لطفاً نام شرکت را وارد کنید:')
            return
        data['company'] = text
        conversation.company = text
        conversation.state = BaleBotConversation.STATE_DEMO_TYPE
        conversation.session_data = data
        conversation.save(update_fields=['state', 'session_data', 'company', 'updated_at'])
        _reply(conversation, 'کدام دمو را می‌خواهید؟', DEMO_TYPE_MENU)
        return
    elif state == BaleBotConversation.STATE_DEMO_TYPE:
        demo_type = _parse_demo_type(text)
        if not demo_type:
            _reply(conversation, 'لطفاً یکی از گزینه‌های دمو را انتخاب کنید.', DEMO_TYPE_MENU)
            return
        data['demo_type'] = demo_type
        conversation.state = BaleBotConversation.STATE_DEMO_NOTE
        prompt = 'توضیح اختیاری درباره نیاز دمو بنویسید. برای رد شدن، «رد» را بفرستید:'
    elif state == BaleBotConversation.STATE_DEMO_NOTE:
        data['note'] = '' if text in {'رد', '-', 'ندارم'} else text
        demo = DemoRequest.objects.create(
            full_name=data.get('full_name', conversation.display_name),
            phone=data.get('phone', conversation.phone),
            email=data.get('email', conversation.email),
            company=data.get('company', conversation.company),
            demo_type=data.get('demo_type', DemoRequest.DEMO_SITBUK),
            note=data.get('note', ''),
            source_page='bale_bot',
            page_url=f'bale://chat/{conversation.chat_id}',
            referrer='Bale Bot',
            user_agent='Bale Bot',
            status=DemoRequest.STATUS_LINK_READY,
        )
        demo.demo_access_expires_at = timezone.now() + timedelta(hours=_demo_access_hours())
        demo.demo_access_url = _demo_url(demo)
        demo.save(update_fields=['demo_access_expires_at', 'demo_access_url', 'status', 'updated_at'])
        _store_message(conversation, BaleBotMessage.DIRECTION_SYSTEM, 'Demo request created from Bale bot', related_demo=demo)
        conversation.reset_flow()
        conversation.save(update_fields=['state', 'session_data', 'phone', 'email', 'company', 'updated_at'])
        _reply(conversation, f'{bot_settings.demo_done_text}\n\nکد درخواست: #{demo.id}\nلینک دمو:\n{demo.demo_access_url}', MAIN_MENU)
        return
    else:
        _reset_to_menu(conversation, bot_settings)
        return
    conversation.session_data = data
    conversation.save(update_fields=['state', 'session_data', 'phone', 'email', 'company', 'updated_at'])
    _reply(conversation, prompt)


def _handle_status_flow(conversation: BaleBotConversation, text: str, bot_settings: BaleBotSettings):
    phone = normalize_phone(text)
    if len(phone) < 8:
        _reply(conversation, 'شماره معتبر نیست. لطفاً شماره موبایل را دوباره وارد کنید:')
        return
    demo = DemoRequest.objects.filter(phone__icontains=phone).order_by('-created_at').first()
    lead = LeadRequest.objects.filter(phone__icontains=phone).order_by('-created_at').first()
    lines = []
    if demo:
        lines.append(f'آخرین درخواست دمو: #{demo.id} - {demo.get_status_display()}')
        if demo.demo_access_url and demo.is_demo_link_active:
            lines.append(f'لینک دمو: {demo.demo_access_url}')
    if lead:
        lines.append(f'آخرین درخواست مشاوره: #{lead.id} - {lead.get_status_display()}')
    if not lines:
        lines.append('درخواستی با این شماره پیدا نشد. می‌توانید از منوی اصلی درخواست جدید ثبت کنید.')
    conversation.reset_flow()
    conversation.save(update_fields=['state', 'session_data', 'updated_at'])
    _reply(conversation, '\n'.join(lines), MAIN_MENU)


def process_update(update: dict[str, Any]) -> bool:
    incoming = _extract_message(update)
    if not incoming:
        return False
    bot_settings = BaleBotSettings.get_solo()
    conversation = _conversation_for(incoming)
    _store_message(
        conversation,
        BaleBotMessage.DIRECTION_IN,
        incoming.text,
        raw=incoming.raw,
        update_id=incoming.update_id,
        message_id=incoming.message_id,
    )
    if not bot_settings.is_enabled:
        return True
    if _should_ignore_group_message(incoming, bot_settings):
        return True
    text = _clean_group_mention(incoming.text, bot_settings).strip()
    if not text:
        _reply(conversation, 'لطفاً یکی از گزینه‌های منو را انتخاب کنید.', MAIN_MENU)
        return True
    if text in CANCEL_WORDS:
        _reset_to_menu(conversation, bot_settings)
        return True
    if conversation.state.startswith('consult_'):
        _handle_consultation_flow(conversation, text, bot_settings)
        return True
    if conversation.state.startswith('demo_'):
        _handle_demo_flow(conversation, text, bot_settings)
        return True
    if conversation.state == BaleBotConversation.STATE_STATUS_PHONE:
        _handle_status_flow(conversation, text, bot_settings)
        return True
    if 'مشاوره' in text:
        _start_consultation(conversation)
    elif 'دمو' in text or 'مشاهده' in text:
        _start_demo(conversation)
    elif 'وضعیت' in text or 'پیگیری' in text:
        _start_status(conversation)
    elif 'تماس' in text:
        _reply(conversation, _contact_text(), MAIN_MENU)
    else:
        _reply(conversation, bot_settings.welcome_text, MAIN_MENU)
    return True


def is_webhook_allowed(secret: str = '') -> bool:
    expected = getattr(settings, 'BALE_WEBHOOK_SECRET', '').strip()
    if not expected:
        return True
    return secret == expected


def poll_once(limit: int = 50, timeout: int = 25) -> int:
    bot_settings = BaleBotSettings.get_solo()
    offset = bot_settings.last_update_id + 1 if bot_settings.last_update_id else None
    response = BaleBotAPI().get_updates(offset=offset, limit=limit, timeout=timeout)
    if not response.get('ok'):
        return 0
    updates = response.get('result') or []
    processed = 0
    max_update_id = bot_settings.last_update_id
    for update in updates:
        update_id = update.get('update_id') or 0
        if process_update(update):
            processed += 1
        if update_id > max_update_id:
            max_update_id = update_id
    if max_update_id != bot_settings.last_update_id:
        bot_settings.last_update_id = max_update_id
        bot_settings.save(update_fields=['last_update_id', 'updated_at'])
    return processed


def poll_forever(limit: int = 50, timeout: int = 25, sleep_seconds: float = 1.0):
    while True:
        poll_once(limit=limit, timeout=timeout)
        time.sleep(sleep_seconds)
