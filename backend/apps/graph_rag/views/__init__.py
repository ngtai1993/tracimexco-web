from apps.graph_rag.views.instance_views import (
    RAGInstanceListCreateView,
    RAGInstanceDetailView,
    RAGInstanceConfigView,
    RAGInstanceCloneView,
    RAGInstanceKBView,
    RAGInstanceKBRemoveView,
    RAGInstanceSkillView,
)
from apps.graph_rag.views.kb_views import (
    KnowledgeBaseListCreateView,
    KnowledgeBaseDetailView,
    DocumentListView,
    DocumentUploadView,
    DocumentTextView,
    DocumentURLView,
    DocumentDetailView,
    DocumentChunkListView,
    KnowledgeBaseGraphBuildView,
)
from apps.graph_rag.views.chat_views import (
    ChatQueryView,
    ConversationListView,
    ConversationDetailView,
    MessageFeedbackView,
)
from apps.graph_rag.views.access_views import (
    AccessPermissionListCreateView,
    AccessPermissionDeleteView,
    MyAccessView,
)
from apps.graph_rag.views.analytics_views import (
    InstanceAnalyticsView,
    UsageLogListView,
    ConfigHistoryListView,
)

__all__ = [
    "RAGInstanceListCreateView",
    "RAGInstanceDetailView",
    "RAGInstanceConfigView",
    "RAGInstanceCloneView",
    "RAGInstanceKBView",
    "RAGInstanceSkillView",
    "KnowledgeBaseListCreateView",
    "KnowledgeBaseDetailView",
    "DocumentListView",
    "DocumentUploadView",
    "DocumentTextView",
    "DocumentURLView",
    "DocumentDetailView",
    "DocumentChunkListView",
    "KnowledgeBaseGraphBuildView",
    "ChatQueryView",
    "ConversationListView",
    "ConversationDetailView",
    "MessageFeedbackView",
    "AccessPermissionListCreateView",
    "AccessPermissionDeleteView",
    "MyAccessView",
    "InstanceAnalyticsView",
    "UsageLogListView",
    "ConfigHistoryListView",
]
