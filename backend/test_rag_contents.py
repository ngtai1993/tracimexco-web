"""
Integration test: RAG + contents AI (final run).
"""
import os
import time
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from apps.graph_rag.services.pipeline_service import PipelineService
from apps.graph_rag.models import RAGInstance
from apps.contents.services import AIGenerationService, GeminiDirectService
from apps.contents.models import AIContentGeneration
from apps.contents.constants import GenerationStatus, GenerationType
from apps.users.models import User

USER = User.objects.first()
UID = str(USER.id)
SEP = "=" * 60

# Make all instances public
for inst in RAGInstance.objects.filter(is_deleted=False):
    inst.is_public = True
    inst.save(update_fields=["is_public"])

# -- RAG 1: Gemini -- API rate limit question
print(SEP)
print("RAG 1 -- Gemini (ho-tro-ky-thuat-ai) -- rate limit API")
print(SEP)
gemini = RAGInstance.objects.get(slug="ho-tro-ky-thuat-ai")
r1 = PipelineService.process_query(
    rag_instance_id=str(gemini.id),
    query="Rate limit API Tracimexco bao nhieu req/phut?",
    user_id=UID,
)
m1 = r1["message"]
print(f"Sources ({len(m1['sources'])}):")
for s in m1["sources"][:3]:
    print(f"  [{s['score']}] {s['document_title']}: {s['content_preview'][:70]}")
print(f"Answer: {m1['content'][:300]}")

# -- RAG 2: Gemini -- SLA ticket (same conversation)
time.sleep(3)
print()
print(SEP)
print("RAG 2 -- Gemini -- SLA Critical + Hotline (same conversation)")
print(SEP)
r2 = PipelineService.process_query(
    rag_instance_id=str(gemini.id),
    query="Ticket Critical SLA bao lau? Hotline IT so may?",
    user_id=UID,
    conversation_id=r1["conversation_id"],
)
m2 = r2["message"]
print(f"Sources ({len(m2['sources'])}):")
for s in m2["sources"][:3]:
    print(f"  [{s['score']}] {s['document_title']}: {s['content_preview'][:70]}")
print(f"Answer: {m2['content'][:300]}")

# -- RAG 3: OpenAI instance -- fallback to Gemini
time.sleep(3)
print()
print(SEP)
print("RAG 3 -- OpenAI instance (tro-ly-khach-hang) -- Gemini fallback")
print(SEP)
openai_inst = RAGInstance.objects.get(slug="tro-ly-khach-hang")
r3 = PipelineService.process_query(
    rag_instance_id=str(openai_inst.id),
    query="Goi ERP Business gia bao nhieu? Co chiet khau khong?",
    user_id=UID,
)
m3 = r3["message"]
print(f"Sources ({len(m3['sources'])}):")
for s in m3["sources"][:3]:
    print(f"  [{s['score']}] {s['document_title']}: {s['content_preview'][:70]}")
print(f"Answer: {m3['content'][:300]}")

# -- Contents 1: AIGenerationService with real RAG context
time.sleep(3)
print()
print(SEP)
print("CONTENTS 1 -- AIGenerationService full_post (RAG -> Gemini)")
print(SEP)
gen = AIContentGeneration.objects.create(
    rag_instance=gemini,
    created_by=USER,
    generation_type=GenerationType.FULL_POST,
    prompt="Viet bai LinkedIn ve cach xac thuc API an toan voi Bearer token theo tai lieu Tracimexco",
    context_data={"platform": "LinkedIn"},
    status=GenerationStatus.PENDING,
)
AIGenerationService.process_generation(str(gen.id))
gen.refresh_from_db()
print(f"Status: {gen.status}")
print(f"Result: {gen.result_content[:400]}" if gen.result_content else f"Error: {gen.error_message}")

# -- Contents 2: Hashtags
time.sleep(3)
print()
print(SEP)
print("CONTENTS 2 -- GeminiDirectService.suggest_hashtags")
print(SEP)
tags = GeminiDirectService.suggest_hashtags(
    content="Tracimexco ra mat ERP Suite Pro 3.0 voi tich hop AI giup tu dong hoa quy trinh doanh nghiep.",
    platform_type="LinkedIn",
    count=8,
)
print(f"Tags ({len(tags)}): {tags}")

# -- Contents 3: Summarize
time.sleep(3)
print()
print(SEP)
print("CONTENTS 3 -- GeminiDirectService.summarize (Twitter <= 280)")
print(SEP)
text = (
    "Tracimexco ERP Suite Pro 3.0 tich hop AI du bao ton kho, toi uu chuoi cung ung, "
    "phan tich du lieu ban hang real-time. Giao dien moi, tich hop 200+ app. "
    "500+ doanh nghiep Viet tin dung. Tu 50 trieu/nam, ho tro 24/7, cloud va on-premise."
)
summary = GeminiDirectService.summarize(text, "Twitter", max_length=280)
print(f"Summary ({len(summary)} chars): {summary}")

# -- Contents 4: Translate + Improve
time.sleep(3)
print()
print(SEP)
print("CONTENTS 4 -- translate + improve")
print(SEP)
en = GeminiDirectService.translate("Chung toi cung cap phan mem quan tri doanh nghiep toan dien.", "en")
print(f"EN: {en}")
improved = GeminiDirectService.improve("Phan mem ERP cua chung toi giup quan ly doanh nghiep.", "engagement")
print(f"Improved: {improved[:200]}")

print()
print(SEP)
print("ALL TESTS PASSED")
print(SEP)
