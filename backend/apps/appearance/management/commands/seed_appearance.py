from django.core.management.base import BaseCommand
from apps.appearance.models import ColorToken, MediaAsset


DEFAULT_COLOR_TOKENS = [
    # ── BRAND ──────────────────────────────────────────────────────
    # Light
    {"key": "primary",       "mode": "light", "value": "#0e4475", "name": "Primary",            "group": "brand",    "order": 1},
    {"key": "primary-hover", "mode": "light", "value": "#0b3560", "name": "Primary Hover",       "group": "brand",    "order": 2},
    {"key": "primary-light", "mode": "light", "value": "#e6eef7", "name": "Primary Light",       "group": "brand",    "order": 3},
    {"key": "primary-fg",    "mode": "light", "value": "#ffffff", "name": "Primary Foreground",  "group": "brand",    "order": 4},
    {"key": "secondary",     "mode": "light", "value": "#1565c0", "name": "Secondary",           "group": "brand",    "order": 5},
    {"key": "accent",        "mode": "light", "value": "#0288d1", "name": "Accent",              "group": "brand",    "order": 6},
    # Dark
    {"key": "primary",       "mode": "dark",  "value": "#2b78cc", "name": "Primary",            "group": "brand",    "order": 1},
    {"key": "primary-hover", "mode": "dark",  "value": "#2470be", "name": "Primary Hover",       "group": "brand",    "order": 2},
    {"key": "primary-light", "mode": "dark",  "value": "#0d253d", "name": "Primary Light",       "group": "brand",    "order": 3},
    {"key": "primary-fg",    "mode": "dark",  "value": "#ffffff", "name": "Primary Foreground",  "group": "brand",    "order": 4},
    {"key": "secondary",     "mode": "dark",  "value": "#42a5f5", "name": "Secondary",           "group": "brand",    "order": 5},
    {"key": "accent",        "mode": "dark",  "value": "#29b6f6", "name": "Accent",              "group": "brand",    "order": 6},

    # ── SEMANTIC ────────────────────────────────────────────────────
    # Light
    {"key": "success",       "mode": "light", "value": "#16a34a", "name": "Success",       "group": "semantic", "order": 1},
    {"key": "success-light", "mode": "light", "value": "#dcfce7", "name": "Success Light", "group": "semantic", "order": 2},
    {"key": "warning",       "mode": "light", "value": "#d97706", "name": "Warning",       "group": "semantic", "order": 3},
    {"key": "warning-light", "mode": "light", "value": "#fef3c7", "name": "Warning Light", "group": "semantic", "order": 4},
    {"key": "danger",        "mode": "light", "value": "#dc2626", "name": "Danger",        "group": "semantic", "order": 5},
    {"key": "danger-light",  "mode": "light", "value": "#fee2e2", "name": "Danger Light",  "group": "semantic", "order": 6},
    {"key": "info",          "mode": "light", "value": "#0284c7", "name": "Info",          "group": "semantic", "order": 7},
    {"key": "info-light",    "mode": "light", "value": "#e0f2fe", "name": "Info Light",    "group": "semantic", "order": 8},
    # Dark
    {"key": "success",       "mode": "dark",  "value": "#4ade80", "name": "Success",       "group": "semantic", "order": 1},
    {"key": "success-light", "mode": "dark",  "value": "#052e16", "name": "Success Light", "group": "semantic", "order": 2},
    {"key": "warning",       "mode": "dark",  "value": "#fbbf24", "name": "Warning",       "group": "semantic", "order": 3},
    {"key": "warning-light", "mode": "dark",  "value": "#2d1a00", "name": "Warning Light", "group": "semantic", "order": 4},
    {"key": "danger",        "mode": "dark",  "value": "#f87171", "name": "Danger",        "group": "semantic", "order": 5},
    {"key": "danger-light",  "mode": "dark",  "value": "#2d0a0a", "name": "Danger Light",  "group": "semantic", "order": 6},
    {"key": "info",          "mode": "dark",  "value": "#38bdf8", "name": "Info",          "group": "semantic", "order": 7},
    {"key": "info-light",    "mode": "dark",  "value": "#021d2e", "name": "Info Light",    "group": "semantic", "order": 8},

    # ── NEUTRAL ─────────────────────────────────────────────────────
    # Light
    {"key": "fg",          "mode": "light", "value": "#0f172a", "name": "Foreground",        "group": "neutral", "order": 1},
    {"key": "fg-muted",    "mode": "light", "value": "#475569", "name": "Foreground Muted",  "group": "neutral", "order": 2},
    {"key": "fg-subtle",   "mode": "light", "value": "#94a3b8", "name": "Foreground Subtle", "group": "neutral", "order": 3},
    {"key": "bg",          "mode": "light", "value": "#ffffff", "name": "Background",        "group": "neutral", "order": 4},
    {"key": "bg-subtle",   "mode": "light", "value": "#f8fafc", "name": "Background Subtle", "group": "neutral", "order": 5},
    {"key": "bg-muted",    "mode": "light", "value": "#f1f5f9", "name": "Background Muted",  "group": "neutral", "order": 6},
    {"key": "border",      "mode": "light", "value": "#e2e8f0", "name": "Border",            "group": "neutral", "order": 7},
    {"key": "card",        "mode": "light", "value": "#ffffff", "name": "Card Background",   "group": "neutral", "order": 8},
    {"key": "card-border", "mode": "light", "value": "#e2e8f0", "name": "Card Border",       "group": "neutral", "order": 9},
    {"key": "surface",    "mode": "light", "value": "#f1f5f9", "name": "Surface",           "group": "neutral", "order": 10},
    # Dark
    {"key": "fg",          "mode": "dark",  "value": "#f1f5f9", "name": "Foreground",        "group": "neutral", "order": 1},
    {"key": "fg-muted",    "mode": "dark",  "value": "#94a3b8", "name": "Foreground Muted",  "group": "neutral", "order": 2},
    {"key": "fg-subtle",   "mode": "dark",  "value": "#64748b", "name": "Foreground Subtle", "group": "neutral", "order": 3},
    {"key": "bg",          "mode": "dark",  "value": "#0c1a2e", "name": "Background",        "group": "neutral", "order": 4},
    {"key": "bg-subtle",   "mode": "dark",  "value": "#112036", "name": "Background Subtle", "group": "neutral", "order": 5},
    {"key": "bg-muted",    "mode": "dark",  "value": "#162843", "name": "Background Muted",  "group": "neutral", "order": 6},
    {"key": "border",      "mode": "dark",  "value": "#1e3a5f", "name": "Border",            "group": "neutral", "order": 7},
    {"key": "card",        "mode": "dark",  "value": "#112036", "name": "Card Background",   "group": "neutral", "order": 8},
    {"key": "card-border", "mode": "dark",  "value": "#1e3a5f", "name": "Card Border",       "group": "neutral", "order": 9},
    {"key": "surface",    "mode": "dark",  "value": "#162843", "name": "Surface",           "group": "neutral", "order": 10},
]

DEFAULT_MEDIA_KEYS = [
    {"key": "logo",         "name": "Logo chính",     "alt_text": "Logo"},
    {"key": "logo-dark",    "name": "Logo nền tối",   "alt_text": "Logo"},
    {"key": "favicon",      "name": "Favicon",         "alt_text": ""},
    {"key": "og-image",     "name": "OG Image",        "alt_text": ""},
    {"key": "hero-banner",  "name": "Hero Banner",     "alt_text": ""},
]


class Command(BaseCommand):
    help = "Seed dữ liệu mặc định cho app appearance (color tokens và media asset placeholders)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Xóa toàn bộ token/asset cũ trước khi seed lại.",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            ColorToken.objects.all().delete()
            MediaAsset.objects.all().delete()
            self.stdout.write(self.style.WARNING("Đã xóa toàn bộ token và asset."))

        token_created = token_updated = 0
        for data in DEFAULT_COLOR_TOKENS:
            _, created = ColorToken.objects.update_or_create(
                key=data["key"],
                mode=data["mode"],
                defaults={
                    "name": data["name"],
                    "value": data["value"],
                    "group": data["group"],
                    "order": data["order"],
                    "is_active": True,
                    "is_deleted": False,
                },
            )
            if created:
                token_created += 1
            else:
                token_updated += 1

        asset_created = asset_skipped = 0
        for data in DEFAULT_MEDIA_KEYS:
            _, created = MediaAsset.objects.get_or_create(
                key=data["key"],
                defaults={
                    "name": data["name"],
                    "alt_text": data["alt_text"],
                    "is_active": True,
                    "is_deleted": False,
                },
            )
            if created:
                asset_created += 1
            else:
                asset_skipped += 1

        self.stdout.write(self.style.SUCCESS(
            f"Color tokens: {token_created} tạo mới, {token_updated} cập nhật.\n"
            f"Media assets: {asset_created} tạo mới, {asset_skipped} đã tồn tại (bỏ qua)."
        ))
