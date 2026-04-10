"""
Management command: seed_agents
Tạo dữ liệu mẫu cho app agents (providers, API keys, configs).

Usage:
    python manage.py seed_agents
    python manage.py seed_agents --reset   # xóa toàn bộ rồi tạo lại
"""

import logging
from django.core.management.base import BaseCommand
from django.conf import settings

from apps.agents.models import AgentProvider, AgentAPIKey, AgentConfig
from apps.agents.services.agent_encryption_service import AgentEncryptionService

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Sample provider data
# ---------------------------------------------------------------------------
PROVIDERS = [
    {
        "slug": "openai",
        "name": "OpenAI",
        "description": "Nhà cung cấp mô hình GPT-4o, GPT-4 Turbo, GPT-3.5 Turbo từ OpenAI.",
        "website_url": "https://platform.openai.com",
    },
    {
        "slug": "anthropic",
        "name": "Anthropic",
        "description": "Nhà cung cấp mô hình Claude 3.7 Sonnet, Claude 3.5 Haiku từ Anthropic.",
        "website_url": "https://console.anthropic.com",
    },
    {
        "slug": "google-gemini",
        "name": "Google Gemini",
        "description": "Nhà cung cấp mô hình Gemini 2.0 Flash, Gemini 1.5 Pro từ Google AI.",
        "website_url": "https://ai.google.dev",
    },
    {
        "slug": "groq",
        "name": "Groq",
        "description": "Nhà cung cấp inference tốc độ cao cho Llama, Mixtral, Gemma qua Groq LPU.",
        "website_url": "https://console.groq.com",
    },
]

# ---------------------------------------------------------------------------
# Sample API key data (plain text — sẽ được mã hóa khi seed)
# ---------------------------------------------------------------------------
API_KEYS = [
    # OpenAI
    {
        "provider_slug": "openai",
        "name": "Production Key",
        "raw_key": "sk-proj-sample-openai-production-key-for-dev-only",
        "priority": 1,
    },
    {
        "provider_slug": "openai",
        "name": "Backup Key",
        "raw_key": "sk-proj-sample-openai-backup-key-for-dev-only-xxxx",
        "priority": 2,
    },
    # Anthropic
    {
        "provider_slug": "anthropic",
        "name": "Main API Key",
        "raw_key": "sk-ant-sample-anthropic-main-key-for-dev-only-xxxxxxx",
        "priority": 1,
    },
    {
        "provider_slug": "anthropic",
        "name": "Dev Key",
        "raw_key": "sk-ant-sample-anthropic-dev-key-for-dev-only-xxxxxxxx",
        "priority": 2,
    },
    # Google Gemini
    {
        "provider_slug": "google-gemini",
        "name": "Gemini API Key",
        "raw_key": "AIzaSy-sample-google-gemini-api-key-for-dev-only-xxx",
        "priority": 1,
    },
    # Groq
    {
        "provider_slug": "groq",
        "name": "Groq Fast Key",
        "raw_key": "gsk_sample-groq-api-key-for-dev-env-only-xxxxxxxxxxx",
        "priority": 1,
    },
]

# ---------------------------------------------------------------------------
# Sample config data
# ---------------------------------------------------------------------------
CONFIGS = [
    # ── OpenAI ──────────────────────────────────────────────────────────────
    {
        "provider_slug": "openai",
        "name": "GPT-4o Standard",
        "model_name": "gpt-4o",
        "is_default": True,
        "config_json": {
            "temperature": 0.7,
            "max_tokens": 4096,
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
        },
    },
    {
        "provider_slug": "openai",
        "name": "GPT-4o Mini Fast",
        "model_name": "gpt-4o-mini",
        "is_default": False,
        "config_json": {
            "temperature": 0.5,
            "max_tokens": 2048,
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
        },
    },
    {
        "provider_slug": "openai",
        "name": "GPT-4 Turbo Pro",
        "model_name": "gpt-4-turbo",
        "is_default": False,
        "config_json": {
            "temperature": 0.3,
            "max_tokens": 8192,
            "top_p": 0.95,
            "frequency_penalty": 0.1,
            "presence_penalty": 0.1,
        },
    },
    # ── Anthropic ───────────────────────────────────────────────────────────
    {
        "provider_slug": "anthropic",
        "name": "Claude 3.7 Sonnet",
        "model_name": "claude-3-7-sonnet-20250219",
        "is_default": True,
        "config_json": {
            "temperature": 0.7,
            "max_tokens": 4096,
            "top_p": 1.0,
        },
    },
    {
        "provider_slug": "anthropic",
        "name": "Claude 3.5 Haiku Fast",
        "model_name": "claude-3-5-haiku-20241022",
        "is_default": False,
        "config_json": {
            "temperature": 0.5,
            "max_tokens": 2048,
            "top_p": 1.0,
        },
    },
    # ── Google Gemini ────────────────────────────────────────────────────────
    {
        "provider_slug": "google-gemini",
        "name": "Gemini 2.0 Flash",
        "model_name": "gemini-2.0-flash",
        "is_default": True,
        "config_json": {
            "temperature": 0.7,
            "max_tokens": 4096,
            "top_p": 1.0,
        },
    },
    {
        "provider_slug": "google-gemini",
        "name": "Gemini 1.5 Pro",
        "model_name": "gemini-1.5-pro",
        "is_default": False,
        "config_json": {
            "temperature": 0.4,
            "max_tokens": 8192,
            "top_p": 0.95,
        },
    },
    # ── Groq ────────────────────────────────────────────────────────────────
    {
        "provider_slug": "groq",
        "name": "Llama 3 70B",
        "model_name": "llama3-70b-8192",
        "is_default": True,
        "config_json": {
            "temperature": 0.6,
            "max_tokens": 4096,
            "top_p": 1.0,
        },
    },
    {
        "provider_slug": "groq",
        "name": "Mixtral 8x7B",
        "model_name": "mixtral-8x7b-32768",
        "is_default": False,
        "config_json": {
            "temperature": 0.5,
            "max_tokens": 8192,
            "top_p": 1.0,
        },
    },
]


class Command(BaseCommand):
    help = "Seed dữ liệu mẫu cho app agents (providers, API keys, model configs)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Xóa toàn bộ dữ liệu agents trước khi seed.",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            AgentConfig.objects.all().delete()
            AgentAPIKey.objects.all().delete()
            AgentProvider.objects.all().delete()
            self.stdout.write(self.style.WARNING("Đã xóa toàn bộ providers, keys và configs."))

        # ── Providers ────────────────────────────────────────────────────────
        provider_objects: dict[str, AgentProvider] = {}
        p_created = p_updated = 0
        for data in PROVIDERS:
            obj, created = AgentProvider.objects.update_or_create(
                slug=data["slug"],
                defaults={
                    "name": data["name"],
                    "description": data["description"],
                    "website_url": data["website_url"],
                    "is_active": True,
                    "is_deleted": False,
                },
            )
            provider_objects[data["slug"]] = obj
            if created:
                p_created += 1
            else:
                p_updated += 1

        self.stdout.write(f"Providers: {p_created} tạo mới, {p_updated} cập nhật.")

        # ── API Keys ─────────────────────────────────────────────────────────
        encryption_ok = bool(getattr(settings, "AGENT_ENCRYPTION_KEY", ""))
        if not encryption_ok:
            self.stdout.write(
                self.style.WARNING(
                    "AGENT_ENCRYPTION_KEY chưa được cấu hình → bỏ qua tạo API keys."
                )
            )
        else:
            k_created = k_skipped = 0
            for data in API_KEYS:
                provider = provider_objects.get(data["provider_slug"])
                if not provider:
                    continue
                # Dùng key_preview để xác định unique (không tái tạo keys đã tồn tại)
                preview = AgentEncryptionService.generate_preview(data["raw_key"])
                exists = AgentAPIKey.objects.filter(
                    provider=provider, key_preview=preview
                ).exists()
                if exists:
                    k_skipped += 1
                    continue
                encrypted = AgentEncryptionService.encrypt(data["raw_key"])
                AgentAPIKey.objects.create(
                    provider=provider,
                    name=data["name"],
                    encrypted_key=encrypted,
                    key_preview=preview,
                    priority=data["priority"],
                    is_active=True,
                    is_deleted=False,
                )
                k_created += 1
            self.stdout.write(
                f"API Keys: {k_created} tạo mới, {k_skipped} đã tồn tại (bỏ qua)."
            )

        # ── Configs ───────────────────────────────────────────────────────────
        c_created = c_updated = 0
        for data in CONFIGS:
            provider = provider_objects.get(data["provider_slug"])
            if not provider:
                continue
            _, created = AgentConfig.objects.update_or_create(
                provider=provider,
                name=data["name"],
                defaults={
                    "model_name": data["model_name"],
                    "config_json": data["config_json"],
                    "is_default": data["is_default"],
                    "is_active": True,
                    "is_deleted": False,
                },
            )
            if created:
                c_created += 1
            else:
                c_updated += 1

        self.stdout.write(f"Configs: {c_created} tạo mới, {c_updated} cập nhật.")
        self.stdout.write(self.style.SUCCESS("✓ seed_agents hoàn tất."))
