import { useState, useEffect } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import api from '@/lib/api'
import { Plus, Pencil, Trash2, X, Save } from 'lucide-react'

interface Factor {
  id: number
  section_id: number
  code: string
  name: string
  question: string
  weight: number
  min_score: number
  max_score: number
  score_labels: Record<string, string> | null
  sub_area: string | null
  owner_role: string | null
  display_order: number
  is_active: boolean
}

interface Section {
  id: number
  code: string
  name: string
}

export default function FactorManager() {
  const [factors, setFactors] = useState<Factor[]>([])
  const [sections, setSections] = useState<Section[]>([])
  const [editing, setEditing] = useState<Partial<Factor> | null>(null)
  const [isNew, setIsNew] = useState(false)
  const [filterSection, setFilterSection] = useState('')

  const load = () => {
    const params = filterSection ? `?section=${filterSection}` : ''
    api.get(`/factors${params}`).then(res => setFactors(res.data))
  }

  useEffect(() => {
    api.get('/sections').then(res => setSections(res.data))
  }, [])

  useEffect(() => { load() }, [filterSection])

  const handleSave = async () => {
    if (!editing) return
    try {
      if (isNew) {
        await api.post('/factors', editing)
      } else {
        await api.put(`/factors/${editing.id}`, editing)
      }
      setEditing(null)
      setIsNew(false)
      load()
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Errore')
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Disattivare questo fattore?')) return
    await api.delete(`/factors/${id}`)
    load()
  }

  return (
    <div className="max-w-5xl mx-auto space-y-4">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Gestione Fattori</CardTitle>
            <div className="flex items-center gap-3">
              <select
                value={filterSection}
                onChange={(e) => setFilterSection(e.target.value)}
                className="rounded-input border border-sw-border px-3 py-2 text-sm"
              >
                <option value="">Tutte le sezioni</option>
                {sections.map(s => (
                  <option key={s.code} value={s.code}>{s.name}</option>
                ))}
              </select>
              <Button size="sm" onClick={() => {
                setEditing({
                  section_id: sections[0]?.id,
                  code: '', name: '', question: '', weight: 3,
                  min_score: 1, max_score: 5, display_order: factors.length + 1,
                  score_labels: {}, owner_role: '', sub_area: '',
                })
                setIsNew(true)
              }}>
                <Plus size={14} className="mr-1" /> Nuovo
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-sw-border">
                <th className="text-left py-2 text-sw-text-mid font-medium">Codice</th>
                <th className="text-left py-2 text-sw-text-mid font-medium">Nome</th>
                <th className="text-center py-2 text-sw-text-mid font-medium">Peso</th>
                <th className="text-left py-2 text-sw-text-mid font-medium">Owner</th>
                <th className="text-left py-2 text-sw-text-mid font-medium">Sub Area</th>
                <th className="text-right py-2 text-sw-text-mid font-medium">Azioni</th>
              </tr>
            </thead>
            <tbody>
              {factors.map(f => (
                <tr key={f.id} className="border-b border-sw-border/50">
                  <td className="py-2 font-mono text-xs">{f.code}</td>
                  <td className="py-2">{f.name}</td>
                  <td className="py-2 text-center">
                    <Badge variant={f.weight >= 4 ? 'warning' : 'secondary'}>{f.weight}</Badge>
                  </td>
                  <td className="py-2 text-sw-text-mid">{f.owner_role || '—'}</td>
                  <td className="py-2 text-sw-text-mid text-xs">{f.sub_area || '—'}</td>
                  <td className="py-2 text-right space-x-1">
                    <Button size="sm" variant="ghost" onClick={() => { setEditing(f); setIsNew(false) }}>
                      <Pencil size={14} />
                    </Button>
                    <Button size="sm" variant="ghost" onClick={() => handleDelete(f.id)}>
                      <Trash2 size={14} />
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>

      {/* Edit form */}
      {editing && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">{isNew ? 'Nuovo Fattore' : 'Modifica Fattore'}</CardTitle>
              <Button size="sm" variant="ghost" onClick={() => { setEditing(null); setIsNew(false) }}>
                <X size={14} />
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Sezione</label>
                <select
                  value={editing.section_id}
                  onChange={(e) => setEditing({ ...editing, section_id: parseInt(e.target.value) })}
                  className="w-full rounded-input border border-sw-border px-3 py-2 text-sm"
                >
                  {sections.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
                </select>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Codice</label>
                <Input value={editing.code || ''} onChange={(e) => setEditing({ ...editing, code: e.target.value })} />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Nome</label>
                <Input value={editing.name || ''} onChange={(e) => setEditing({ ...editing, name: e.target.value })} />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Peso (1-10)</label>
                <Input type="number" min={1} max={10} value={editing.weight || 3}
                  onChange={(e) => setEditing({ ...editing, weight: parseInt(e.target.value) })} />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Owner Role</label>
                <Input value={editing.owner_role || ''} onChange={(e) => setEditing({ ...editing, owner_role: e.target.value })} />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Sub Area</label>
                <Input value={editing.sub_area || ''} onChange={(e) => setEditing({ ...editing, sub_area: e.target.value })} />
              </div>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Domanda guida</label>
              <Textarea value={editing.question || ''} onChange={(e) => setEditing({ ...editing, question: e.target.value })} />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Score Labels (JSON)</label>
              <Textarea
                value={JSON.stringify(editing.score_labels || {}, null, 2)}
                onChange={(e) => {
                  try { setEditing({ ...editing, score_labels: JSON.parse(e.target.value) }) }
                  catch { /* ignore parse errors while typing */ }
                }}
                rows={5}
                className="font-mono text-xs"
              />
            </div>
            <Button onClick={handleSave}>
              <Save size={14} className="mr-1" /> Salva
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
