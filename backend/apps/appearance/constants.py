class ColorMode:
    LIGHT = "light"
    DARK = "dark"

    CHOICES = [
        (LIGHT, "Light"),
        (DARK, "Dark"),
    ]


class ColorGroup:
    BRAND = "brand"
    SEMANTIC = "semantic"
    NEUTRAL = "neutral"
    CUSTOM = "custom"

    CHOICES = [
        (BRAND, "Brand"),
        (SEMANTIC, "Semantic"),
        (NEUTRAL, "Neutral"),
        (CUSTOM, "Custom"),
    ]

    ALL = [BRAND, SEMANTIC, NEUTRAL, CUSTOM]


APPEARANCE_CACHE_KEY = "appearance:config"
