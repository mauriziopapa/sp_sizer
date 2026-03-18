import { useState, useEffect, useCallback } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import api from '@/lib/api'
import ProjectInfoStep from '@/components/sizer/ProjectInfoStep'
import SectionStep from '@/components/sizer/SectionStep'
import ResultStep from '@/components/sizer/ResultStep'
import { ChevronLeft, ChevronRight, Check } from 'lucide-react'

interface Section {
  id: number
  code: string
  name: string
  description: string | null
  owner_role: string | null
  factors: Factor[]
}

interface Factor {
  id: number
  code: string
  name: string
  question: string
  weight: number
  min_score: number
  max_score: number
  score_labels: Record<string, string> | null
  sub_area: string | null
  owner_role: string | null
}

export interface ProjectInfo {
  project_name: string
  client_name: string
  compiled_by: string
  validated_by: string
}

export interface SizingResult {
  id: number
  normalized_score: number
  resulting_size: string
  section_scores: Record<string, { raw: number; max: number }>
  total_raw_score: number
  total_max_score: number
  completeness: Record<string, number>
  governance_rules: { element: string; value: string }[]
  triggered_risk_flags_detail: { code: string; label: string; description: string; severity: string }[]
  triggered_risk_flags: string[]
  status: string
}

const STEPS = ['Dati Progetto', 'Sezione Business', 'Sezione Tecnica', 'Risultato']

export default function SizerWizard() {
  const [step, setStep] = useState(0)
  const [sections, setSections] = useState<Section[]>([])
  const [projectInfo, setProjectInfo] = useState<ProjectInfo>({
    project_name: '', client_name: '', compiled_by: '', validated_by: '',
  })
  const [responses, setResponses] = useState<Record<string, number>>({})
  const [notes, setNotes] = useState<Record<string, string>>({})
  const [result, setResult] = useState<SizingResult | null>(null)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    api.get('/sections').then(res => setSections(res.data))
  }, [])

  const businessSection = sections.find(s => s.code === 'BUSINESS')
  const techSection = sections.find(s => s.code === 'TECNICO')

  const allFactors = sections.flatMap(s => s.factors)
  const filledCount = allFactors.filter(f => responses[f.code] != null).length
  const totalCount = allFactors.length
  const completeness = totalCount > 0 ? filledCount / totalCount : 0

  // Live preview of normalized score
  const liveScore = useCallback(() => {
    let totalRaw = 0, totalMax = 0
    for (const f of allFactors) {
      totalMax += f.weight * f.max_score
      if (responses[f.code] != null) {
        totalRaw += responses[f.code] * f.weight
      }
    }
    return totalMax > 0 ? Math.round((totalRaw / totalMax) * 100) : 0
  }, [allFactors, responses])

  const handleSubmit = async () => {
    setSubmitting(true)
    try {
      const res = await api.post('/sizings', {
        ...projectInfo,
        responses,
        notes: Object.keys(notes).length > 0 ? notes : null,
      })
      setResult(res.data)
      setStep(3)
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Errore durante il salvataggio')
    } finally {
      setSubmitting(false)
    }
  }

  const canProceed = () => {
    if (step === 0) return projectInfo.project_name.trim() !== ''
    return true
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Stepper */}
      <div className="flex items-center justify-between mb-8">
        {STEPS.map((label, i) => (
          <div key={i} className="flex items-center flex-1">
            <div className="flex items-center gap-2">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold ${
                i < step ? 'bg-sw-green text-white' :
                i === step ? 'bg-sw-blue text-white' :
                'bg-sw-border text-sw-text-mid'
              }`}>
                {i < step ? <Check size={16} /> : i + 1}
              </div>
              <span className={`text-sm font-medium hidden sm:block ${
                i === step ? 'text-sw-blue' : 'text-sw-text-mid'
              }`}>
                {label}
              </span>
            </div>
            {i < STEPS.length - 1 && (
              <div className={`flex-1 h-0.5 mx-3 ${i < step ? 'bg-sw-green' : 'bg-sw-border'}`} />
            )}
          </div>
        ))}
      </div>

      {/* Live score bar */}
      {step > 0 && step < 3 && (
        <Card className="mb-4">
          <CardContent className="py-3 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <span className="text-sm text-sw-text-mid">Score live:</span>
              <span className="text-lg font-bold text-sw-navy">{liveScore()}/100</span>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-sw-text-mid">
                Completezza: {Math.round(completeness * 100)}%
              </span>
              <div className="w-32 h-2 bg-sw-border rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all ${completeness >= 0.75 ? 'bg-sw-green' : 'bg-sw-orange'}`}
                  style={{ width: `${completeness * 100}%` }}
                />
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step content */}
      {step === 0 && (
        <ProjectInfoStep info={projectInfo} onChange={setProjectInfo} />
      )}
      {step === 1 && businessSection && (
        <SectionStep
          section={businessSection}
          responses={responses}
          notes={notes}
          onResponseChange={(code, value) => setResponses(prev => ({ ...prev, [code]: value }))}
          onNoteChange={(code, value) => setNotes(prev => ({ ...prev, [code]: value }))}
        />
      )}
      {step === 2 && techSection && (
        <SectionStep
          section={techSection}
          responses={responses}
          notes={notes}
          onResponseChange={(code, value) => setResponses(prev => ({ ...prev, [code]: value }))}
          onNoteChange={(code, value) => setNotes(prev => ({ ...prev, [code]: value }))}
          groupBySubArea
        />
      )}
      {step === 3 && result && (
        <ResultStep result={result} />
      )}

      {/* Navigation */}
      <div className="flex justify-between mt-6">
        <Button
          variant="outline"
          onClick={() => setStep(s => s - 1)}
          disabled={step === 0}
        >
          <ChevronLeft size={16} className="mr-1" /> Indietro
        </Button>

        {step < 2 && (
          <Button onClick={() => setStep(s => s + 1)} disabled={!canProceed()}>
            Avanti <ChevronRight size={16} className="ml-1" />
          </Button>
        )}
        {step === 2 && (
          <Button onClick={handleSubmit} disabled={submitting}>
            {submitting ? 'Calcolo...' : 'Calcola Sizing'}
            <Check size={16} className="ml-1" />
          </Button>
        )}
      </div>
    </div>
  )
}
