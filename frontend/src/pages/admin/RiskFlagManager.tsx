import { useState, useEffect } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import api from '@/lib/api'
import { Plus, Pencil, X, Save } from 'lucide-react'

interface RiskFlag {
  id: number
  code: string
  label: string
  description: string
  condition_logic: any
  severity: string
  display_order: number
}

export default function RiskFlagManager() {
  const [flags, setFlags] = useState<RiskFlag[]>([])
  const [editing, setEditing] = useState<Partial<RiskFlag> | null>(null)
  const [isNew, setIsNew] = useState(false)

  const load = () => api.get('/risk-flags').then(res => setFlags(res.data))
  useEffect(() => { load() }, [])

  const handleSave = async () => {
    if (!editing) return
    try {
      if (isNew) {
        await api.post('/risk-flags', editing)
      } else {
        await api.put(`/risk-flags/${editing.id}`, editing)
      }
      setEditing(null); setIsNew(false); load()
    } catch (err: any) { alert(err.response?.data?.detail || 'Errore') }
  }

  return (
    <div className="max-w-5xl mx-auto space-y-4">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Gestione Risk Flags</CardTitle>
            <Button size="sm" onClick={() => {
              setEditing({
                code: '', label: '', description: '', severity: 'WARNING',
                condition_logic: { factors: [], logic: 'AND' },
                display_order: flags.length + 1,
              })
              setIsNew(true)
            }}>
              <Plus size={14} className="mr-1" /> Nuovo
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-sw-border">
                <th className="text-left py-2 text-sw-text-mid font-medium">Codice</th>
                <th className="text-left py-2 text-sw-text-mid font-medium">Label</th>
                <th className="text-center py-2 text-sw-text-mid font-medium">Severità</th>
                <th className="text-left py-2 text-sw-text-mid font-medium">Condizioni</th>
                <th className="text-right py-2 text-sw-text-mid font-medium">Azioni</th>
              </tr>
            </thead>
            <tbody>
              {flags.map(f => (
                <tr key={f.id} className="border-b border-sw-border/50">
                  <td className="py-2 font-mono text-xs">{f.code}</td>
                  <td className="py-2">{f.label}</td>
                  <td className="py-2 text-center">
                    <Badge variant={f.severity === 'CRITICAL' ? 'destructive' : 'warning'}>{f.severity}</Badge>
                  </td>
                  <td className="py-2 text-xs text-sw-text-mid">
                    {f.condition_logic?.factors?.map((c: any) =>
                      `${c.code} ${c.operator} ${c.value}`
                    ).join(` ${f.condition_logic?.logic} `)}
                  </td>
                  <td className="py-2 text-right">
                    <Button size="sm" variant="ghost" onClick={() => { setEditing(f); setIsNew(false) }}>
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
              <CardTitle className="text-base">{isNew ? 'Nuovo Risk Flag' : 'Modifica Risk Flag'}</CardTitle>
              <Button size="sm" variant="ghost" onClick={() => { setEditing(null); setIsNew(false) }}>
                <X size={14} />
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Codice</label>
                <Input value={editing.code || ''} onChange={(e) => setEditing({ ...editing, code: e.target.value })} />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Severità</label>
                <select
                  value={editing.severity || 'WARNING'}
                  onChange={(e) => setEditing({ ...editing, severity: e.target.value })}
                  className="w-full rounded-input border border-sw-border px-3 py-2 text-sm"
                >
                  <option value="WARNING">WARNING</option>
                  <option value="CRITICAL">CRITICAL</option>
                  <option value="BLOCKER">BLOCKER</option>
                </select>
              </div>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Label</label>
              <Input value={editing.label || ''} onChange={(e) => setEditing({ ...editing, label: e.target.value })} />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Descrizione</label>
              <Textarea value={editing.description || ''} onChange={(e) => setEditing({ ...editing, description: e.target.value })} />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Condition Logic (JSON)</label>
              <Textarea
                value={JSON.stringify(editing.condition_logic || {}, null, 2)}
                onChange={(e) => {
                  try { setEditing({ ...editing, condition_logic: JSON.parse(e.target.value) }) }
                  catch { /* ignore */ }
                }}
                rows={6}
                className="font-mono text-xs"
              />
            </div>
            <Button onClick={handleSave}><Save size={14} className="mr-1" /> Salva</Button>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
