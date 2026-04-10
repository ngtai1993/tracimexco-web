class ScheduleNotFound(Exception):
    """Không tìm thấy lịch đăng bài."""
    pass


class InvalidScheduleStatus(Exception):
    """Trạng thái lịch đăng không hợp lệ để thực hiện thao tác này."""
    pass


class PostNotApproved(Exception):
    """Bài viết chưa được duyệt — không thể lên lịch."""
    pass


class ScheduleTimeInPast(Exception):
    """Thời gian đăng bài phải ở tương lai."""
    pass
