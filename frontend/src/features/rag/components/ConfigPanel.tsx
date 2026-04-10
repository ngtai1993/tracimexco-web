'use client'
import { useState } from 'react'
import { Button } from '@/components/ui/Button'
import { Slider } from '@/components/ui/Slider'
import { Switch } from '@/components/ui/Switch'
import { Select } from '@/components/ui/Select'
import { Input } from '@/components/ui/Input'
import { useUpdateConfig } from '../hooks'
import type { RAGInstance, RetrievalConfig, GenerationConfig } from '../types'

interface ConfigPanelProps {
  instance: RAGInstance
  onUpdated: () => void
  onToast: (msg: string, variant: 'success' | 'danger') => void
}

export function ConfigPanel({ instance, onUpdated, onToast }: ConfigPanelProps) {
  const [tab, setTab] = useState<'retrieval' | 'generation'>('retrieval')
  const [retrieval, setRetrieval] = useState<RetrievalConfig>({ ...instance.retrieval_config })
  const [generation, setGeneration] = useState<GenerationConfig>({ ...instance.generation_config })
  const [reason, setReason] = useState('')
  const { updateConfig, loading, error } = useUpdateConfig()

  const handleSave = async () => {
    const config = tab === 'retrieval' ? retrieval : generation
    const result = await updateConfig(instance.slug, {
      config_type: tab,
      config: config as unknown as Record<string, unknown>,
      reason: reason || undefined,
    })
    if (result) {
      onToast(`Cập nhật ${tab} config thành công`, 'success')
      setReason('')
      onUpdated()
    } else {
      onToast(error ?? 'Cập nhật thất bại', 'danger')
    }
  }

  return (
    <div className="space-y-6">
      {/* Tab Switcher */}
      <div className="flex gap-1 p-1 rounded-bento bg-surface border border-border w-fit">
        {(['retrieval', 'generation'] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 text-sm rounded-md transition-colors ${
              tab === t
                ? 'bg-primary text-white font-medium'
                : 'text-fg-muted hover:text-fg'
            }`}
          >
            {t === 'retrieval' ? 'Retrieval' : 'Generation'}
          </button>
        ))}
      </div>

      {/* Retrieval Config */}
      {tab === 'retrieval' && (
        <div className="space-y-5">
          <Select
            label="Search Strategy"
            value={retrieval.search_strategy}
            onChange={(e) =>
              setRetrieval({ ...retrieval, search_strategy: e.target.value as RetrievalConfig['search_strategy'] })
            }
            options={[
              { value: 'hybrid', label: 'Hybrid' },
              { value: 'vector', label: 'Vector' },
              { value: 'keyword', label: 'Keyword' },
              { value: 'graph', label: 'Graph' },
            ]}
          />

          <Slider
            label="Top-K Vector"
            min={1} max={50} step={1}
            value={retrieval.top_k_vector}
            onChange={(v) => setRetrieval({ ...retrieval, top_k_vector: v })}
          />
          <Slider
            label="Top-K Graph"
            min={1} max={50} step={1}
            value={retrieval.top_k_graph}
            onChange={(v) => setRetrieval({ ...retrieval, top_k_graph: v })}
          />
          <Slider
            label="Top-K Final"
            min={1} max={50} step={1}
            value={retrieval.top_k_final}
            onChange={(v) => setRetrieval({ ...retrieval, top_k_final: v })}
          />
          <Slider
            label="Similarity Threshold"
            min={0} max={1} step={0.05}
            value={retrieval.similarity_threshold}
            onChange={(v) => setRetrieval({ ...retrieval, similarity_threshold: v })}
          />
          <Slider
            label="Graph Depth"
            min={1} max={5} step={1}
            value={retrieval.graph_depth}
            onChange={(v) => setRetrieval({ ...retrieval, graph_depth: v })}
          />
          <Input
            label="Embedding Model"
            value={retrieval.embedding_model}
            onChange={(e) => setRetrieval({ ...retrieval, embedding_model: e.target.value })}
          />
          <Switch
            checked={retrieval.images_enabled}
            onChange={(c) => setRetrieval({ ...retrieval, images_enabled: c })}
            label="Bật xử lý hình ảnh"
          />
          <Switch
            checked={retrieval.reranking_enabled}
            onChange={(c) => setRetrieval({ ...retrieval, reranking_enabled: c })}
            label="Bật reranking"
          />
          <Switch
            checked={retrieval.query_decomposition}
            onChange={(c) => setRetrieval({ ...retrieval, query_decomposition: c })}
            label="Query Decomposition"
          />
        </div>
      )}

      {/* Generation Config */}
      {tab === 'generation' && (
        <div className="space-y-5">
          <Slider
            label="Temperature"
            min={0} max={2} step={0.1}
            value={generation.temperature}
            onChange={(v) => setGeneration({ ...generation, temperature: v })}
          />
          <Slider
            label="Max Tokens"
            min={256} max={32768} step={256}
            value={generation.max_tokens}
            onChange={(v) => setGeneration({ ...generation, max_tokens: v })}
          />
          <Select
            label="Response Format"
            value={generation.response_format}
            onChange={(e) =>
              setGeneration({ ...generation, response_format: e.target.value as GenerationConfig['response_format'] })
            }
            options={[
              { value: 'markdown', label: 'Markdown' },
              { value: 'text', label: 'Text' },
            ]}
          />
          <Select
            label="Language"
            value={generation.language}
            onChange={(e) =>
              setGeneration({ ...generation, language: e.target.value as GenerationConfig['language'] })
            }
            options={[
              { value: 'vi', label: 'Tiếng Việt' },
              { value: 'en', label: 'English' },
            ]}
          />
          <Select
            label="Tone"
            value={generation.tone}
            onChange={(e) =>
              setGeneration({ ...generation, tone: e.target.value as GenerationConfig['tone'] })
            }
            options={[
              { value: 'professional', label: 'Professional' },
              { value: 'casual', label: 'Casual' },
              { value: 'technical', label: 'Technical' },
            ]}
          />
          <Switch
            checked={generation.include_sources}
            onChange={(c) => setGeneration({ ...generation, include_sources: c })}
            label="Hiển thị nguồn tham khảo"
          />
          <Switch
            checked={generation.stream}
            onChange={(c) => setGeneration({ ...generation, stream: c })}
            label="Streaming response"
          />
        </div>
      )}

      {/* Reason + Save */}
      <div className="space-y-3 pt-4 border-t border-border">
        <Input
          label="Lý do thay đổi (tùy chọn)"
          placeholder="Tối ưu retrieval cho tài liệu mới..."
          value={reason}
          onChange={(e) => setReason(e.target.value)}
        />
        {error && <p className="text-sm text-danger">{error}</p>}
        <div className="flex justify-end">
          <Button size="sm" loading={loading} onClick={handleSave}>
            Lưu cấu hình
          </Button>
        </div>
      </div>
    </div>
  )
}
