import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import FactorRow from './FactorRow'

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

interface Section {
  code: string
  name: string
  description: string | null
  owner_role: string | null
  factors: Factor[]
}

interface Props {
  section: Section
  responses: Record<string, number>
  notes: Record<string, string>
  onResponseChange: (code: string, value: number) => void
  onNoteChange: (code: string, value: string) => void
  groupBySubArea?: boolean
}

export default function SectionStep({
  section, responses, notes, onResponseChange, onNoteChange, groupBySubArea,
}: Props) {
  const activeFactors = section.factors

  if (groupBySubArea) {
    const groups: Record<string, Factor[]> = {}
    for (const f of activeFactors) {
      const area = f.sub_area || 'Altro'
      if (!groups[area]) groups[area] = []
      groups[area].push(f)
    }

    return (
      <div className="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle>{section.name}</CardTitle>
            {section.description && <CardDescription>{section.description}</CardDescription>}
          </CardHeader>
        </Card>

        {Object.entries(groups).map(([area, factors]) => (
          <Card key={area}>
            <CardHeader>
              <CardTitle className="text-base">{area}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {factors.map(factor => (
                <FactorRow
                  key={factor.code}
                  factor={factor}
                  value={responses[factor.code]}
                  note={notes[factor.code] || ''}
                  onValueChange={(v) => onResponseChange(factor.code, v)}
                  onNoteChange={(v) => onNoteChange(factor.code, v)}
                />
              ))}
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{section.name}</CardTitle>
        {section.description && <CardDescription>{section.description}</CardDescription>}
      </CardHeader>
      <CardContent className="space-y-4">
        {activeFactors.map(factor => (
          <FactorRow
            key={factor.code}
            factor={factor}
            value={responses[factor.code]}
            note={notes[factor.code] || ''}
            onValueChange={(v) => onResponseChange(factor.code, v)}
            onNoteChange={(v) => onNoteChange(factor.code, v)}
          />
        ))}
      </CardContent>
    </Card>
  )
}
