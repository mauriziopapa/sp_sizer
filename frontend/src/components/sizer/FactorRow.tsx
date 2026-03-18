import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Textarea } from '@/components/ui/textarea'
import { ChevronDown, ChevronUp } from 'lucide-react'

interface Factor {
  code: string
  name: string
  question: string
  weight: number
  min_score: number
  max_score: number
  score_labels: Record<string, string> | null
  owner_role: string | null
}

interface Props {
  factor: Factor
  value: number | undefined
  note: string
  onValueChange: (value: number) => void
  onNoteChange: (value: string) => void
}

export default function FactorRow({ factor, value, note, onValueChange, onNoteChange }: Props) {
  const [showNote, setShowNote] = useState(false)
  const scores = Array.from(
    { length: factor.max_score - factor.min_score + 1 },
    (_, i) => factor.min_score + i
  )
  const weightedScore = value != null ? value * factor.weight : 0
  const maxWeighted = factor.max_score * factor.weight

  return (
    <div className="border border-sw-border rounded-card p-4 space-y-3">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-mono text-sw-text-sub">{factor.code}</span>
            <span className="font-semibold text-sw-navy">{factor.name}</span>
            {factor.owner_role && (
              <Badge variant="secondary" className="text-[10px]">{factor.owner_role}</Badge>
            )}
          </div>
          <p className="text-sm text-sw-text-mid">{factor.question}</p>
        </div>
        <div className="text-right shrink-0">
          <Badge variant={factor.weight >= 4 ? 'warning' : 'secondary'}>
            Peso: {factor.weight}
          </Badge>
          <div className="text-xs text-sw-text-sub mt-1">
            {weightedScore}/{maxWeighted}
          </div>
        </div>
      </div>

      {/* Score selection */}
      <div className="flex flex-wrap gap-2">
        {scores.map(score => {
          const label = factor.score_labels?.[String(score)]
          const isSelected = value === score
          return (
            <button
              key={score}
              onClick={() => onValueChange(score)}
              className={`flex-1 min-w-[100px] rounded-input border p-2 text-left transition-all ${
                isSelected
                  ? 'border-sw-blue bg-sw-blue/5 ring-2 ring-sw-blue/20'
                  : 'border-sw-border hover:border-sw-blue/30 hover:bg-sw-bg'
              }`}
            >
              <div className={`text-sm font-semibold ${isSelected ? 'text-sw-blue' : 'text-sw-text'}`}>
                {score}
              </div>
              {label && (
                <div className="text-xs text-sw-text-mid mt-0.5 line-clamp-2">{label}</div>
              )}
            </button>
          )
        })}
      </div>

      {/* Note toggle */}
      <button
        onClick={() => setShowNote(!showNote)}
        className="flex items-center gap-1 text-xs text-sw-text-sub hover:text-sw-blue transition-colors"
      >
        {showNote ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        {showNote ? 'Nascondi nota' : 'Aggiungi nota'}
      </button>
      {showNote && (
        <Textarea
          value={note}
          onChange={(e) => onNoteChange(e.target.value)}
          placeholder="Motivazione o note aggiuntive..."
          className="text-sm"
          rows={2}
        />
      )}
    </div>
  )
}
