import logging
from django.db import transaction

from apps.graph_rag.models import (
    RAGInstance,
    RAGInstanceKnowledgeBase,
    RAGInstanceSkill,
    RAGConfigHistory,
)
from apps.graph_rag.constants import DEFAULT_RETRIEVAL_CONFIG, DEFAULT_GENERATION_CONFIG
from apps.graph_rag.exceptions import RAGInstanceNotFound

logger = logging.getLogger(__name__)


class RAGInstanceService:
    """Business logic cho CRUD RAG instances."""

    @staticmethod
    def create(
        *,
        name: str,
        slug: str,
        description: str = "",
        purpose: str = "general",
        system_prompt: str,
        provider_id,
        agent_config_id=None,
        retrieval_config: dict | None = None,
        generation_config: dict | None = None,
        is_public: bool = False,
        created_by=None,
    ) -> RAGInstance:
        """Tạo RAG instance mới, merge input config với defaults."""
        merged_retrieval = {**DEFAULT_RETRIEVAL_CONFIG, **(retrieval_config or {})}
        merged_generation = {**DEFAULT_GENERATION_CONFIG, **(generation_config or {})}

        return RAGInstance.objects.create(
            name=name,
            slug=slug,
            description=description,
            purpose=purpose,
            system_prompt=system_prompt,
            provider_id=provider_id,
            agent_config_id=agent_config_id,
            retrieval_config=merged_retrieval,
            generation_config=merged_generation,
            is_public=is_public,
            created_by=created_by,
        )

    @staticmethod
    def update_config(
        *,
        instance_id,
        config_type: str,
        new_config: dict,
        changed_by=None,
        reason: str = "",
    ) -> RAGInstance:
        """Update config (deep merge) và log history."""
        instance = RAGInstance.objects.get(id=instance_id, is_deleted=False)

        if config_type == "retrieval":
            old_value = instance.retrieval_config.copy()
            instance.retrieval_config = {**old_value, **new_config}
            field_name = "retrieval_config"
        elif config_type == "generation":
            old_value = instance.generation_config.copy()
            instance.generation_config = {**old_value, **new_config}
            field_name = "generation_config"
        elif config_type == "system_prompt":
            old_value = {"system_prompt": instance.system_prompt}
            instance.system_prompt = new_config.get("system_prompt", instance.system_prompt)
            field_name = "system_prompt"
        else:
            raise ValueError(f"Invalid config_type: {config_type}")

        with transaction.atomic():
            instance.save(update_fields=[field_name, "updated_at"])
            RAGConfigHistory.objects.create(
                rag_instance=instance,
                config_type=config_type,
                old_value=old_value,
                new_value=new_config,
                changed_by=changed_by,
                reason=reason,
            )

        return instance

    @staticmethod
    def clone(*, source_id, new_name: str, new_slug: str, created_by=None) -> RAGInstance:
        """Clone RAG instance — copy config, KB assignments, skill assignments."""
        source = RAGInstance.objects.get(id=source_id, is_deleted=False)

        with transaction.atomic():
            clone = RAGInstance.objects.create(
                name=new_name,
                slug=new_slug,
                description=source.description,
                purpose=source.purpose,
                system_prompt=source.system_prompt,
                provider=source.provider,
                agent_config=source.agent_config,
                retrieval_config=source.retrieval_config.copy(),
                generation_config=source.generation_config.copy(),
                is_public=source.is_public,
                created_by=created_by,
            )

            # Copy KB assignments
            for ikb in RAGInstanceKnowledgeBase.objects.filter(
                rag_instance=source, is_deleted=False
            ):
                RAGInstanceKnowledgeBase.objects.create(
                    rag_instance=clone,
                    knowledge_base=ikb.knowledge_base,
                    priority=ikb.priority,
                )

            # Copy skill assignments
            for isk in RAGInstanceSkill.objects.filter(
                rag_instance=source, is_deleted=False
            ):
                RAGInstanceSkill.objects.create(
                    rag_instance=clone,
                    skill=isk.skill,
                    is_enabled=isk.is_enabled,
                    config_override=isk.config_override.copy(),
                )

        return clone

    @staticmethod
    def assign_knowledge_base(*, instance_id, kb_id, priority: int = 1):
        return RAGInstanceKnowledgeBase.objects.create(
            rag_instance_id=instance_id,
            knowledge_base_id=kb_id,
            priority=priority,
        )

    @staticmethod
    def remove_knowledge_base(*, instance_id, kb_id) -> bool:
        deleted, _ = RAGInstanceKnowledgeBase.objects.filter(
            rag_instance_id=instance_id,
            knowledge_base_id=kb_id,
        ).delete()
        return deleted > 0

    @staticmethod
    def assign_skill(*, instance_id, skill_id, config_override: dict | None = None):
        return RAGInstanceSkill.objects.create(
            rag_instance_id=instance_id,
            skill_id=skill_id,
            config_override=config_override or {},
        )

    @staticmethod
    def soft_delete(instance_id) -> None:
        """Soft delete instance + cascade assignments."""
        with transaction.atomic():
            RAGInstance.objects.filter(id=instance_id, is_deleted=False).update(
                is_deleted=True
            )
            RAGInstanceKnowledgeBase.objects.filter(
                rag_instance_id=instance_id
            ).update(is_deleted=True)
            RAGInstanceSkill.objects.filter(rag_instance_id=instance_id).update(
                is_deleted=True
            )
