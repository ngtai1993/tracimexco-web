class PostNotFound(Exception):
    """Không tìm thấy bài viết."""
    pass


class CategoryNotFound(Exception):
    """Không tìm thấy danh mục."""
    pass


class TagNotFound(Exception):
    """Không tìm thấy tag."""
    pass


class PostTemplateNotFound(Exception):
    """Không tìm thấy post template."""
    pass


class InvalidStatusTransition(Exception):
    """Trạng thái bài viết không hợp lệ để thực hiện thao tác này."""
    pass


class AIGenerationNotFound(Exception):
    """Không tìm thấy generation record."""
    pass


class BannerLayoutNotFound(Exception):
    """Không tìm thấy banner layout."""
    pass


class LayoutTemplateNotFound(Exception):
    """Không tìm thấy layout template."""
    pass


class PostMediaNotFound(Exception):
    """Không tìm thấy media."""
    pass


class CircularCategoryError(Exception):
    """Tạo vòng lặp cha-con trong category."""
    pass


class CategoryHasChildren(Exception):
    """Không thể xóa category đang có category con."""
    pass


class CategoryHasPosts(Exception):
    """Không thể xóa category đang có bài viết."""
    pass
