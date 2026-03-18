import { useState, useEffect } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import api from '@/lib/api'
import { Save } from 'lucide-react'

interface GovernanceRule {
  id: number
  element: string
  score_range_id: number
  value: string
  size_code: string | null
}

interface ScoreRange {
  id: number
  size_code: string
}

export default function GovernanceManager() {
  const [rules, setRules] = useState<GovernanceRule[]>([])
  const [ranges, setRanges] = useState<ScoreRange[]>([])
  const [editValues, setEditValues] = useState<Record<number, string>>({})

  const load = async () => {
    const [rulesRes, rangesRes] = await Promise.all([
      api.get('/governance-rules'),
      api.get('/score-ranges'),
    ])
    setRules(rulesRes.data)
    setRanges(rangesRes.data)
  }

  useEffect(() => { load() }, [])

  // Group by element
  const elements = [...new Set(rules.map(r => r.element))]
  const getRule = (element: string, sizeCode: string) =>
    rules.find(r => r.element === element && r.size_code === sizeCode)

  const handleSave = async (ruleId: number) => {
    if (editValues[ruleId] === undefined) return
    await api.put(`/governance-rules/${ruleId}`, { value: editValues[ruleId] })
    setEditValues(prev => { const copy = { ...prev }; delete copy[ruleId]; return copy })
    load()
  }

  return (
    <div className="max-w-5xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle>Governance Rules — Matrice</CardTitle>
        </CardHeader>
        <CardContent>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-sw-border">
                <th className="text-left py-2 text-sw-text-mid font-medium">Elemento</th>
                {ranges.map(r => (
                  <th key={r.id} className="text-center py-2 text-sw-text-mid font-medium">{r.size_code}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {elements.map(element => (
                <tr key={element} className="border-b border-sw-border/50">
                  <td className="py-2 font-medium">{element}</td>
                  {ranges.map(range => {
                    const rule = getRule(element, range.size_code)
                    if (!rule) return <td key={range.id} className="py-2 text-center text-sw-text-sub">—</td>
                    const isEditing = editValues[rule.id] !== undefined
                    return (
                      <td key={range.id} className="py-2 text-center">
                        <div className="flex items-center gap-1 justify-center">
                          <Input
                            value={isEditing ? editValues[rule.id] : rule.value}
                            onChange={(e) => setEditValues(prev => ({ ...prev, [rule.id]: e.target.value }))}
                            className="text-center text-xs h-8 max-w-[140px]"
                          />
                          {isEditing && (
                            <Button size="sm" variant="ghost" onClick={() => handleSave(rule.id)}>
                              <Save size={12} />
                            </Button>
                          )}
                        </div>
                      </td>
                    )
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  )
}
