"""
Management command: seed_graph_rag
Tạo dữ liệu mẫu cho app graph_rag (knowledge bases, documents, RAG instances).

Usage:
    python manage.py seed_graph_rag
    python manage.py seed_graph_rag --reset   # xóa toàn bộ rồi tạo lại
"""

import logging
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from apps.agents.models import AgentProvider, AgentConfig
from apps.graph_rag.models import (
    KnowledgeBase,
    Document,
    RAGInstance,
    RAGInstanceKnowledgeBase,
)
from apps.graph_rag.constants import DEFAULT_RETRIEVAL_CONFIG, DEFAULT_GENERATION_CONFIG
from apps.graph_rag.services.document_processor import DocumentProcessorService

User = get_user_model()
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Sample knowledge bases
# ---------------------------------------------------------------------------
KNOWLEDGE_BASES = [
    {
        "slug": "tai-lieu-noi-bo",
        "name": "Tài liệu Nội bộ",
        "description": "Tổng hợp quy trình vận hành, hướng dẫn nội bộ và tài liệu onboarding nhân viên.",
        "chunk_strategy": "recursive",
        "chunk_size": 512,
        "chunk_overlap": 50,
        "embedding_model": "text-embedding-3-small",
    },
    {
        "slug": "san-pham-dich-vu",
        "name": "Sản phẩm & Dịch vụ",
        "description": "Danh mục sản phẩm, bảng giá, thông số kỹ thuật và chính sách bán hàng.",
        "chunk_strategy": "semantic",
        "chunk_size": 600,
        "chunk_overlap": 80,
        "embedding_model": "text-embedding-3-small",
    },
    {
        "slug": "chinh-sach-cong-ty",
        "name": "Chính sách Công ty",
        "description": "Nội quy lao động, chính sách bảo mật, quy định an toàn thông tin và compliance.",
        "chunk_strategy": "fixed",
        "chunk_size": 400,
        "chunk_overlap": 40,
        "embedding_model": "text-embedding-3-small",
    },
    {
        "slug": "ho-tro-ky-thuat",
        "name": "Hỗ trợ Kỹ thuật",
        "description": "FAQ kỹ thuật, hướng dẫn troubleshooting và tài liệu API cho đội kỹ thuật.",
        "chunk_strategy": "recursive",
        "chunk_size": 512,
        "chunk_overlap": 64,
        "embedding_model": "text-embedding-3-small",
    },
]

# ---------------------------------------------------------------------------
# Sample documents (source_type = "text" để không cần file upload)
# ---------------------------------------------------------------------------
DOCUMENTS = [
    # ── Tài liệu Nội bộ ─────────────────────────────────────────────────────
    {
        "kb_slug": "tai-lieu-noi-bo",
        "title": "Quy trình Onboarding Nhân viên Mới",
        "description": "Hướng dẫn từng bước cho nhân viên mới từ ngày đầu đến hết tháng thử việc.",
        "source_type": "text",
        "content_text": (
            "# Quy trình Onboarding Nhân viên Mới\n\n"
            "## Tuần 1: Làm quen môi trường\n"
            "- Nhận thiết bị làm việc tại bộ phận IT (tầng 2, phòng 201)\n"
            "- Tham gia buổi định hướng công ty lúc 9:00 sáng ngày đầu tiên\n"
            "- Hoàn thiện hồ sơ nhân sự và ký hợp đồng lao động\n"
            "- Cài đặt các công cụ: Slack, Notion, Jira, VPN\n\n"
            "## Tuần 2-4: Đào tạo chuyên môn\n"
            "- Tham gia chương trình đào tạo theo phòng ban\n"
            "- Hoàn thành 3 khóa học bắt buộc trên LMS nội bộ\n"
            "- Gặp gỡ mentor được phân công ít nhất 2 lần/tuần\n\n"
            "## Cuối tháng thử việc\n"
            "- Đánh giá 360° với quản lý trực tiếp\n"
            "- Nộp báo cáo thử việc qua hệ thống HR\n"
            "- Xác nhận ký hợp đồng chính thức nếu đạt yêu cầu\n"
        ),
        "processing_status": "completed",
    },
    {
        "kb_slug": "tai-lieu-noi-bo",
        "title": "Hướng dẫn Sử dụng Hệ thống Nội bộ",
        "description": "Mô tả các công cụ và hệ thống phần mềm được sử dụng trong công ty.",
        "source_type": "text",
        "content_text": (
            "# Hệ thống Nội bộ Tracimexco\n\n"
            "## Công cụ Giao tiếp\n"
            "- **Slack**: Kênh liên lạc chính theo team và dự án\n"
            "  - #general: thông báo toàn công ty\n"
            "  - #tech-team: đội phát triển\n"
            "  - #support: yêu cầu hỗ trợ nội bộ\n\n"
            "## Quản lý Dự án\n"
            "- **Jira**: Theo dõi sprint, issue và bug report\n"
            "- **Notion**: Tài liệu kỹ thuật, wiki nội bộ\n"
            "- **GitHub**: Quản lý source code và CI/CD\n\n"
            "## Hệ thống HR\n"
            "- Đăng ký nghỉ phép: hrms.tracimexco.com\n"
            "- Xem bảng lương: payroll.tracimexco.com\n"
            "- Đào tạo: lms.tracimexco.com\n"
        ),
        "processing_status": "completed",
    },
    {
        "kb_slug": "tai-lieu-noi-bo",
        "title": "Quy trình Xử lý Yêu cầu IT",
        "description": "Hướng dẫn tạo ticket và theo dõi yêu cầu hỗ trợ kỹ thuật.",
        "source_type": "text",
        "content_text": (
            "# Quy trình Xử lý Yêu cầu IT\n\n"
            "## Tạo Ticket Hỗ trợ\n"
            "1. Truy cập helpdesk.tracimexco.com\n"
            "2. Chọn loại yêu cầu: Hardware / Software / Network / Account\n"
            "3. Mô tả chi tiết vấn đề kèm screenshot nếu có\n"
            "4. Chọn mức độ ưu tiên: Low / Medium / High / Critical\n\n"
            "## SLA Xử lý\n"
            "- Critical: phản hồi trong 1 giờ, xử lý trong 4 giờ\n"
            "- High: phản hồi trong 4 giờ, xử lý trong 1 ngày làm việc\n"
            "- Medium: xử lý trong 3 ngày làm việc\n"
            "- Low: xử lý trong 5 ngày làm việc\n\n"
            "## Liên hệ Khẩn cấp\n"
            "- Hotline IT: 1900-xxxx (nội bộ: 1234)\n"
            "- Email: it-support@tracimexco.com\n"
        ),
        "processing_status": "completed",
    },
    # ── Sản phẩm & Dịch vụ ───────────────────────────────────────────────────
    {
        "kb_slug": "san-pham-dich-vu",
        "title": "Danh mục Sản phẩm Chủ lực",
        "description": "Thông tin chi tiết về các dòng sản phẩm chính của Tracimexco.",
        "source_type": "text",
        "content_text": (
            "# Danh mục Sản phẩm Tracimexco\n\n"
            "## Nhóm Phần mềm Doanh nghiệp\n"
            "### ERP Suite Pro\n"
            "- Phân hệ: Kế toán, Kho vận, Nhân sự, Mua hàng, Bán hàng\n"
            "- Phù hợp: doanh nghiệp vừa và lớn (50–5000 nhân viên)\n"
            "- Giá: từ 50.000.000 VNĐ/năm\n"
            "- Hỗ trợ: triển khai on-premise và cloud\n\n"
            "### HRM Cloud\n"
            "- Quản lý nhân sự, chấm công, tính lương tự động\n"
            "- Tích hợp với các hệ thống ERP phổ biến\n"
            "- Giá: 200.000 VNĐ/nhân viên/tháng\n\n"
            "## Nhóm Dịch vụ Tư vấn\n"
            "### Digital Transformation Consulting\n"
            "- Đánh giá hiện trạng và lộ trình chuyển đổi số\n"
            "- Đội ngũ tư vấn 50+ chuyên gia\n"
            "- Dự án từ 3–18 tháng\n"
        ),
        "processing_status": "completed",
    },
    {
        "kb_slug": "san-pham-dich-vu",
        "title": "Bảng Giá Dịch vụ 2026",
        "description": "Bảng giá chính thức các gói dịch vụ và sản phẩm năm 2026.",
        "source_type": "text",
        "content_text": (
            "# Bảng Giá Dịch vụ Tracimexco 2026\n\n"
            "## Gói Phần mềm ERP\n"
            "| Gói | Số user | Giá/năm |\n"
            "|-----|---------|----------|\n"
            "| Starter | 1–10 | 15.000.000 VNĐ |\n"
            "| Business | 11–50 | 50.000.000 VNĐ |\n"
            "| Enterprise | 51–200 | 150.000.000 VNĐ |\n"
            "| Unlimited | 200+ | Liên hệ |\n\n"
            "## Gói Dịch vụ Hỗ trợ\n"
            "- **Bronze**: giờ hành chính, email support — 5.000.000 VNĐ/tháng\n"
            "- **Silver**: 24/5, email + chat — 10.000.000 VNĐ/tháng\n"
            "- **Gold**: 24/7, ưu tiên cao, dedicated AM — 25.000.000 VNĐ/tháng\n\n"
            "## Chiết khấu\n"
            "- Thanh toán 1 năm: -10%\n"
            "- Thanh toán 2 năm: -20%\n"
            "- Đối tác chiến lược: -30% (theo hợp đồng)\n"
        ),
        "processing_status": "completed",
    },
    # ── Chính sách Công ty ───────────────────────────────────────────────────
    {
        "kb_slug": "chinh-sach-cong-ty",
        "title": "Nội quy Lao động",
        "description": "Quy định về giờ làm việc, nghỉ phép, trang phục và hành vi ứng xử.",
        "source_type": "text",
        "content_text": (
            "# Nội quy Lao động Tracimexco\n\n"
            "## Giờ Làm Việc\n"
            "- Thứ 2 – Thứ 6: 8:30 – 17:30\n"
            "- Giờ nghỉ trưa: 12:00 – 13:00\n"
            "- Làm thêm giờ: cần phê duyệt của quản lý trước 24 giờ\n\n"
            "## Chế độ Nghỉ Phép\n"
            "- Nghỉ phép năm: 12 ngày/năm (tăng theo thâm niên)\n"
            "- Nghỉ bệnh: 30 ngày/năm (có giấy xác nhận y tế)\n"
            "- Nghỉ thai sản: theo quy định Bộ luật Lao động\n"
            "- Nghỉ đột xuất: báo cáo quản lý trực tiếp qua Slack/phone\n\n"
            "## Trang phục\n"
            "- Thứ 2 – Thứ 5: business casual\n"
            "- Thứ 6: tự do (casual Friday)\n"
            "- Khi gặp khách hàng/đối tác: formal\n"
        ),
        "processing_status": "completed",
    },
    {
        "kb_slug": "chinh-sach-cong-ty",
        "title": "Chính sách Bảo mật Thông tin",
        "description": "Quy định về xử lý dữ liệu khách hàng, bảo mật nội bộ và an toàn thông tin.",
        "source_type": "text",
        "content_text": (
            "# Chính sách Bảo mật Thông tin\n\n"
            "## Phân loại Dữ liệu\n"
            "- **Công khai**: thông tin marketing, tài liệu quảng bá\n"
            "- **Nội bộ**: quy trình, hướng dẫn nội bộ\n"
            "- **Bảo mật**: dữ liệu khách hàng, hợp đồng, tài chính\n"
            "- **Tuyệt mật**: mã nguồn core, chiến lược kinh doanh\n\n"
            "## Xử lý Dữ liệu Khách hàng\n"
            "- Tuân thủ Nghị định 13/2023/NĐ-CP về bảo vệ dữ liệu cá nhân\n"
            "- Mã hóa AES-256 cho dữ liệu lưu trữ\n"
            "- TLS 1.3 cho dữ liệu truyền tải\n"
            "- Không chia sẻ dữ liệu khách hàng cho bên thứ ba khi chưa có sự đồng ý\n\n"
            "## Quản lý Truy cập\n"
            "- Nguyên tắc least privilege cho tất cả hệ thống\n"
            "- 2FA bắt buộc cho tài khoản admin và truy cập dữ liệu bảo mật\n"
            "- Review quyền truy cập định kỳ mỗi quý\n"
        ),
        "processing_status": "completed",
    },
    # ── Hỗ trợ Kỹ thuật ─────────────────────────────────────────────────────
    {
        "kb_slug": "ho-tro-ky-thuat",
        "title": "FAQ Kỹ thuật Thường gặp",
        "description": "Tổng hợp các câu hỏi kỹ thuật phổ biến và hướng xử lý.",
        "source_type": "text",
        "content_text": (
            "# FAQ Kỹ thuật Thường gặp\n\n"
            "## Vấn đề Đăng nhập\n"
            "**Q: Không đăng nhập được vào hệ thống?**\n"
            "A: Kiểm tra: (1) Caps Lock; (2) đặt lại mật khẩu qua 'Quên mật khẩu'; "
            "(3) xóa cookie/cache trình duyệt; (4) liên hệ IT nếu vẫn không được.\n\n"
            "**Q: Tài khoản bị khóa?**\n"
            "A: Sau 5 lần đăng nhập sai, tài khoản tự khóa 30 phút. "
            "Liên hệ it-support@tracimexco.com để mở khóa khẩn cấp.\n\n"
            "## Vấn đề Hiệu năng\n"
            "**Q: Hệ thống chạy chậm?**\n"
            "A: Thử: (1) xóa cache; (2) dùng Chrome/Edge phiên bản mới nhất; "
            "(3) kiểm tra kết nối mạng; (4) báo cáo IT nếu toàn bộ user bị ảnh hưởng.\n\n"
            "## API & Tích hợp\n"
            "**Q: Lấy API key tích hợp ở đâu?**\n"
            "A: Truy cập Settings → Integrations → API Keys trong dashboard. "
            "Rate limit mặc định: 1000 req/phút. Liên hệ để tăng giới hạn.\n"
        ),
        "processing_status": "completed",
    },
    {
        "kb_slug": "ho-tro-ky-thuat",
        "title": "Tài liệu API Tích hợp",
        "description": "Hướng dẫn sử dụng REST API cho đối tác và developer.",
        "source_type": "text",
        "content_text": (
            "# Tài liệu API Tracimexco\n\n"
            "## Xác thực\n"
            "Tất cả API yêu cầu Bearer token trong header:\n"
            "```\nAuthorization: Bearer <your-api-key>\n```\n\n"
            "## Endpoints Chính\n"
            "### Quản lý Khách hàng\n"
            "- `GET /api/v1/customers` — Danh sách khách hàng\n"
            "- `POST /api/v1/customers` — Tạo khách hàng mới\n"
            "- `GET /api/v1/customers/{id}` — Chi tiết khách hàng\n"
            "- `PUT /api/v1/customers/{id}` — Cập nhật thông tin\n\n"
            "### Quản lý Đơn hàng\n"
            "- `GET /api/v1/orders` — Danh sách đơn hàng\n"
            "- `POST /api/v1/orders` — Tạo đơn hàng\n"
            "- `GET /api/v1/orders/{id}/status` — Trạng thái đơn hàng\n\n"
            "## Giới hạn & Lỗi\n"
            "- Rate limit: 1000 req/phút/token\n"
            "- HTTP 429: vượt rate limit — đợi `Retry-After` giây\n"
            "- HTTP 401: token hết hạn — làm mới tại /auth/refresh\n"
        ),
        "processing_status": "completed",
    },
]

# ---------------------------------------------------------------------------
# Sample RAG instances
# ---------------------------------------------------------------------------
RAG_INSTANCES = [
    {
        "slug": "tro-ly-khach-hang",
        "name": "Trợ lý Hỗ trợ Khách hàng",
        "description": "Chatbot hỗ trợ khách hàng tự động, trả lời các câu hỏi về sản phẩm, giá cả và chính sách.",
        "purpose": "customer_support",
        "provider_slug": "openai",
        "config_name": "GPT-4o Standard",
        "is_public": True,
        "system_prompt": (
            "Bạn là trợ lý hỗ trợ khách hàng của Tracimexco. "
            "Hãy trả lời dựa trên thông tin được cung cấp trong ngữ cảnh.\n\n"
            "Ngữ cảnh:\n{context}\n\n"
            "Nguồn tham khảo: {sources}\n\n"
            "Trả lời bằng {language}, giọng điệu chuyên nghiệp và thân thiện."
        ),
        "kb_slugs": ["san-pham-dich-vu", "chinh-sach-cong-ty"],
        "retrieval_override": {"top_k_final": 7, "search_strategy": "hybrid"},
        "generation_override": {"language": "vi", "tone": "professional", "temperature": 0.6},
    },
    {
        "slug": "qa-noi-bo",
        "name": "Q&A Nội bộ",
        "description": "Hệ thống tìm kiếm và trả lời câu hỏi dựa trên tài liệu nội bộ cho nhân viên.",
        "purpose": "internal_qa",
        "provider_slug": "anthropic",
        "config_name": "Claude 3.7 Sonnet",
        "is_public": False,
        "system_prompt": (
            "Bạn là trợ lý Q&A nội bộ của Tracimexco. "
            "Chỉ trả lời dựa trên tài liệu nội bộ được cung cấp.\n\n"
            "Tài liệu:\n{context}\n\n"
            "Nếu không tìm thấy thông tin, hãy trả lời trực tiếp rằng bạn không có thông tin đó "
            "và gợi ý liên hệ bộ phận liên quan.\n\n"
            "Ngôn ngữ: {language}. Nguồn: {sources}"
        ),
        "kb_slugs": ["tai-lieu-noi-bo", "chinh-sach-cong-ty"],
        "retrieval_override": {"top_k_final": 5, "search_strategy": "vector"},
        "generation_override": {"language": "vi", "tone": "professional", "temperature": 0.3},
    },
    {
        "slug": "ho-tro-ky-thuat-ai",
        "name": "Trợ lý Kỹ thuật",
        "description": "Hỗ trợ đội kỹ thuật tra cứu tài liệu API, troubleshooting và hướng dẫn tích hợp.",
        "purpose": "general",
        "provider_slug": "google-gemini",
        "config_name": "Gemini 2.0 Flash",
        "is_public": False,
        "system_prompt": (
            "Bạn là trợ lý kỹ thuật, chuyên trả lời các câu hỏi về API, "
            "troubleshooting và tài liệu kỹ thuật.\n\n"
            "Tài liệu kỹ thuật:\n{context}\n\n"
            "Trả lời ngắn gọn, chính xác, kèm ví dụ code khi cần thiết. "
            "Nguồn: {sources}. Ngôn ngữ: {language}"
        ),
        "kb_slugs": ["ho-tro-ky-thuat", "tai-lieu-noi-bo"],
        "retrieval_override": {"top_k_final": 6, "search_strategy": "hybrid"},
        "generation_override": {"language": "vi", "tone": "technical", "temperature": 0.4},
    },
    {
        "slug": "phan-tich-du-lieu",
        "name": "Phân tích Dữ liệu Kinh doanh",
        "description": "Trợ lý phân tích báo cáo, xu hướng thị trường và đưa ra khuyến nghị kinh doanh.",
        "purpose": "data_analysis",
        "provider_slug": "openai",
        "config_name": "GPT-4 Turbo Pro",
        "is_public": False,
        "system_prompt": (
            "Bạn là chuyên gia phân tích kinh doanh. "
            "Hãy phân tích dữ liệu và đưa ra nhận định dựa trên ngữ cảnh được cung cấp.\n\n"
            "Dữ liệu:\n{context}\n\n"
            "Trình bày có cấu trúc, kèm bảng số liệu khi có. "
            "Nguồn: {sources}. Ngôn ngữ: {language}"
        ),
        "kb_slugs": ["san-pham-dich-vu"],
        "retrieval_override": {
            "top_k_final": 10,
            "search_strategy": "hybrid",
            "query_decomposition": True,
        },
        "generation_override": {
            "language": "vi",
            "tone": "professional",
            "temperature": 0.2,
            "max_tokens": 4096,
        },
    },
]


class Command(BaseCommand):
    help = "Seed dữ liệu mẫu cho app graph_rag (knowledge bases, documents, RAG instances)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Xóa toàn bộ dữ liệu graph_rag trước khi seed.",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            RAGInstanceKnowledgeBase.objects.all().delete()
            RAGInstance.objects.all().delete()
            Document.objects.all().delete()
            KnowledgeBase.objects.all().delete()
            self.stdout.write(self.style.WARNING(
                "Đã xóa toàn bộ RAG instances, knowledge bases và documents."
            ))

        # Lấy admin user để gán created_by
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = User.objects.first()
        if not admin_user:
            self.stdout.write(self.style.WARNING(
                "Không tìm thấy user nào trong DB. "
                "Chạy seed_users trước hoặc tạo superuser. created_by sẽ là NULL."
            ))

        # ── Knowledge Bases ──────────────────────────────────────────────────
        kb_objects: dict[str, KnowledgeBase] = {}
        kb_created = kb_updated = 0
        for data in KNOWLEDGE_BASES:
            obj, created = KnowledgeBase.objects.update_or_create(
                slug=data["slug"],
                defaults={
                    "name": data["name"],
                    "description": data["description"],
                    "chunk_strategy": data["chunk_strategy"],
                    "chunk_size": data["chunk_size"],
                    "chunk_overlap": data["chunk_overlap"],
                    "embedding_model": data["embedding_model"],
                    "is_active": True,
                    "is_deleted": False,
                    "created_by": admin_user,
                },
            )
            kb_objects[data["slug"]] = obj
            if created:
                kb_created += 1
            else:
                kb_updated += 1

        self.stdout.write(f"Knowledge Bases: {kb_created} tạo mới, {kb_updated} cập nhật.")

        # ── Documents ────────────────────────────────────────────────────────
        doc_created = doc_skipped = 0
        new_doc_ids = []
        for data in DOCUMENTS:
            kb = kb_objects.get(data["kb_slug"])
            if not kb:
                continue
            doc, created = Document.objects.get_or_create(
                knowledge_base=kb,
                title=data["title"],
                defaults={
                    "description": data["description"],
                    "source_type": data["source_type"],
                    "content_text": data["content_text"],
                    "processing_status": "pending",
                    "is_deleted": False,
                },
            )
            if created:
                doc_created += 1
                new_doc_ids.append(str(doc.id))
                # Cập nhật document_count cho KB
                kb.document_count += 1
                kb.save(update_fields=["document_count"])
            else:
                doc_skipped += 1

        self.stdout.write(f"Documents: {doc_created} tạo mới, {doc_skipped} đã tồn tại (bỏ qua).")

        # ── Process new documents → tạo DocumentChunks ────────────────────────
        if new_doc_ids:
            chunk_total = 0
            for doc_id in new_doc_ids:
                try:
                    DocumentProcessorService.process_document(doc_id)
                    from apps.graph_rag.models import DocumentChunk
                    count = DocumentChunk.objects.filter(document_id=doc_id).count()
                    chunk_total += count
                except Exception as exc:
                    self.stdout.write(
                        self.style.WARNING(f"  ⚠ Không thể process document {doc_id}: {exc}")
                    )
            self.stdout.write(f"DocumentChunks: {chunk_total} chunks tạo từ {len(new_doc_ids)} documents.")

        # ── RAG Instances ────────────────────────────────────────────────────
        inst_created = inst_updated = 0
        for data in RAG_INSTANCES:
            # Lấy provider
            try:
                provider = AgentProvider.objects.get(slug=data["provider_slug"])
            except AgentProvider.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f"Provider '{data['provider_slug']}' không tồn tại. "
                        f"Bỏ qua instance '{data['slug']}'. Chạy seed_agents trước."
                    )
                )
                continue

            # Lấy agent config (có thể None)
            agent_config = AgentConfig.objects.filter(
                provider=provider, name=data["config_name"]
            ).first()

            # Build configs
            retrieval_cfg = {**DEFAULT_RETRIEVAL_CONFIG, **data.get("retrieval_override", {})}
            generation_cfg = {**DEFAULT_GENERATION_CONFIG, **data.get("generation_override", {})}

            instance, created = RAGInstance.objects.update_or_create(
                slug=data["slug"],
                defaults={
                    "name": data["name"],
                    "description": data["description"],
                    "purpose": data["purpose"],
                    "provider": provider,
                    "agent_config": agent_config,
                    "system_prompt": data["system_prompt"],
                    "retrieval_config": retrieval_cfg,
                    "generation_config": generation_cfg,
                    "is_public": data["is_public"],
                    "is_active": True,
                    "is_deleted": False,
                    "created_by": admin_user,
                },
            )
            if created:
                inst_created += 1
            else:
                inst_updated += 1

            # Gán Knowledge Bases cho instance
            for priority, kb_slug in enumerate(data.get("kb_slugs", []), start=1):
                kb = kb_objects.get(kb_slug)
                if not kb:
                    continue
                RAGInstanceKnowledgeBase.objects.get_or_create(
                    rag_instance=instance,
                    knowledge_base=kb,
                    defaults={"priority": priority, "is_deleted": False},
                )

        self.stdout.write(f"RAG Instances: {inst_created} tạo mới, {inst_updated} cập nhật.")
        self.stdout.write(self.style.SUCCESS("✓ seed_graph_rag hoàn tất."))
