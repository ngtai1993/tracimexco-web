'use client'
import { useState } from 'react'
import Image from 'next/image'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { FileDropzone } from '@/components/ui/FileDropzone'
import { useCreateAsset, useUpdateAsset } from '../hooks'
import type { MediaAssetAdmin } from '../types'

interface AssetFormProps {
  asset?: MediaAssetAdmin | null
  onSuccess: (asset: MediaAssetAdmin) => void
  onCancel: () => void
}

export function AssetForm({ asset, onSuccess, onCancel }: AssetFormProps) {
  const isEdit = !!asset
  const [name, setName] = useState(() => asset?.name ?? '')
  const [key, setKey] = useState(() => asset?.key ?? '')
  const [altText, setAltText] = useState(() => asset?.alt_text ?? '')
  const [description, setDescription] = useState(() => asset?.description ?? '')
  const [isActive, setIsActive] = useState(() => asset?.is_active ?? true)
  const [file, setFile] = useState<File | null>(null)

  const { create, loading: creating, error: createError, fieldErrors: createFE } = useCreateAsset()
  const { update, loading: updating, error: updateError, fieldErrors: updateFE } = useUpdateAsset()

  const loading = creating || updating
  const serverError = createError ?? updateError
  const fieldErrors = createFE ?? updateFE

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (isEdit && asset) {
      // Nếu có file mới → FormData, không → plain object
      if (file) {
        const fd = new FormData()
        fd.append('name', name)
        fd.append('alt_text', altText)
        fd.append('description', description)
        fd.append('is_active', String(isActive))
        fd.append('file', file)
        const result = await update(asset.id, fd)
        if (result) onSuccess(result)
      } else {
        const result = await update(asset.id, { name, alt_text: altText, description, is_active: isActive })
        if (result) onSuccess(result)
      }
    } else {
      const fd = new FormData()
      fd.append('name', name)
      fd.append('key', key)
      fd.append('alt_text', altText)
      fd.append('description', description)
      fd.append('is_active', String(isActive))
      if (file) fd.append('file', file)
      const result = await create(fd)
      if (result) onSuccess(result)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <Input
          label="Tên *"
          value={name}
          onChange={(e) => setName(e.target.value)}
          error={fieldErrors?.name?.[0]}
          required
        />
        <Input
          label="Key (slug) *"
          value={key}
          onChange={(e) => setKey(e.target.value)}
          error={fieldErrors?.key?.[0]}
          hint="vd: logo, favicon, banner"
          required={!isEdit}
          disabled={isEdit}
        />
      </div>

      <Input
        label="Alt text"
        value={altText}
        onChange={(e) => setAltText(e.target.value)}
        error={fieldErrors?.alt_text?.[0]}
        hint="Mô tả ảnh cho accessibility"
      />

      <Input
        label="Mô tả"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
      />

      {/* Preview ảnh hiện tại khi edit */}
      {isEdit && asset?.file_url && !file && (
        <div className="flex flex-col gap-1.5">
          <span className="text-sm font-medium text-fg">Ảnh hiện tại</span>
          <div className="w-32 h-20 rounded-lg border border-border bg-bg-subtle flex items-center justify-center overflow-hidden">
            <Image
              src={asset.file_url}
              alt={asset.alt_text || asset.name}
              width={128}
              height={80}
              className="object-contain w-full h-full p-1"
            />
          </div>
        </div>
      )}

      <FileDropzone
        label={isEdit ? 'Thay ảnh (tuỳ chọn)' : 'File ảnh'}
        value={file}
        onChange={setFile}
        error={fieldErrors?.file?.[0]}
      />

      <label className="flex items-center gap-2 cursor-pointer">
        <input
          type="checkbox"
          checked={isActive}
          onChange={(e) => setIsActive(e.target.checked)}
          className="accent-primary"
        />
        <span className="text-sm text-fg-muted">Hoạt động</span>
      </label>

      {serverError && <p className="text-sm text-danger">{serverError}</p>}

      <div className="flex justify-end gap-2 pt-2">
        <Button type="button" variant="ghost" size="sm" onClick={onCancel}>Hủy</Button>
        <Button type="submit" size="sm" loading={loading}>
          {isEdit ? 'Lưu thay đổi' : 'Upload asset'}
        </Button>
      </div>
    </form>
  )
}
