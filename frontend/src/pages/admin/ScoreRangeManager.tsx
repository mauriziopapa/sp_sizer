import { useState, useEffect } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import api from '@/lib/api'
import { Pencil, X, Save } from 'lucide-react'

interface ScoreRange {
  id: number
  size_code: string
  size_label: string
  min_score: number
  max_score: number
  color: string | null
  emoji: string | null
  display_order: number
}

export default function ScoreRangeManager() {
  const [ranges, setRanges] = useState<ScoreRange[]>([])
  const [editing, setEditing] = useState<Partial<ScoreRange> | null>(null)

  const load = () => api.get('/score-ranges').then(res => setRanges(res.data))
  useEffect(() => { load() }, [])

  const handleSave = async () => {
    if (!editing) return
    await api.put(`/score-ranges/${editing.id}`, editing)
    setEditing(null); load()
  }

  return (
    <div className="max-w-4xl mx-auto space-y-4">
      <Card>
        <CardHeader><CardTitle>Gestione Soglie di Classificazione</CardTitle></CardHeader>
        <CardContent>
          {/* Preview gauge */}
          <div className="mb-6">
            <div className="relative h-8 rounded-full overflow-hidden flex">
              {ranges.map(r => (
                <div
                  key={r.id}
                  className="h-full flex items-center justify-center text-white text-xs font-semibold"
                  style={{
                    backgroundColor: r.color || '#ccc',
                    width: `${r.max_score - r.min_score + 1}%`,
                  }}
                >
                  {r.size_code} ({r.min_score}-{r.max_score})
                </div>
              ))}
            </div>
          </div>

          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-sw-border">
                <th className="text-left py-2 text-sw-text-mid font-medium">Size</th>
                <th className="text-left py-2 text-sw-text-mid font-medium">Label</th>
                <th className="text-center py-2 text-sw-text-mid font-medium">Range</th>
                <th className="text-center py-2 text-sw-text-mid font-medium">Colore</th>
                <th className="text-right py-2 text-sw-text-mid font-medium">Azioni</th>
              </tr>
            </thead>
            <tbody>
              {ranges.map(r => (
                <tr key={r.id} className="border-b border-sw-border/50">
                  <td className="py-2 font-semibold">{r.emoji} {r.size_code}</td>
                  <td className="py-2 text-sw-text-mid">{r.size_label}</td>
                  <td className="py-2 text-center">{r.min_score} – {r.max_score}</td>
                  <td className="py-2 text-center">
                    <span className="inline-block w-6 h-6 rounded" style={{ backgroundColor: r.color || '#ccc' }} />
                  </td>
                  <td className="py-2 text-right">
                    <Button size="sm" variant="ghost" onClick={() => setEditing(r)}>
                      <Pencil size={14} />
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>

      {editing && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">Modifica {editing.size_code}</CardTitle>
              <Button size="sm" variant="ghost" onClick={() => setEditing(null)}><X size={14} /></Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Label</label>
                <Input value={editing.size_label || ''} onChange={(e) => setEditing({ ...editing, size_label: e.target.value })} />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Colore</label>
                <div className="flex items-center gap-2">
                  <input type="color" value={editing.color || '#000000'} onChange={(e) => setEditing({ ...editing, color: e.target.value })} />
                  <Input value={editing.color || ''} onChange={(e) => setEditing({ ...editing, color: e.target.value })} />
                </div>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Score Min</label>
                <Input type="number" value={editing.min_score} onChange={(e) => setEditing({ ...editing, min_score: parseInt(e.target.value) })} />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Score Max</label>
                <Input type="number" value={editing.max_score} onChange={(e) => setEditing({ ...editing, max_score: parseInt(e.target.value) })} />
              </div>
            </div>
            <Button onClick={handleSave}><Save size={14} className="mr-1" /> Salva</Button>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
