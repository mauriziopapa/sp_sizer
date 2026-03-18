import { useState, useEffect } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import api from '@/lib/api'
import { Plus, Pencil, Trash2, X, Save } from 'lucide-react'

interface Section {
  id: number
  code: string
  name: string
  description: string | null
  owner_role: string | null
  display_order: number
  is_active: boolean
  max_score_theoretical: number | null
}

export default function SectionManager() {
  const [sections, setSections] = useState<Section[]>([])
  const [editing, setEditing] = useState<Partial<Section> | null>(null)
  const [isNew, setIsNew] = useState(false)

  const load = () => api.get('/sections').then(res => setSections(res.data))
  useEffect(() => { load() }, [])

  const handleSave = async () => {
    if (!editing) return
    try {
      if (isNew) {
        await api.post('/sections', editing)
      } else {
        await api.put(`/sections/${editing.id}`, editing)
      }
      setEditing(null); setIsNew(false); load()
    } catch (err: any) { alert(err.response?.data?.detail || 'Errore') }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Disattivare questa sezione?')) return
    await api.delete(`/sections/${id}`); load()
  }

  return (
    <div className="max-w-4xl mx-auto space-y-4">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Gestione Sezioni</CardTitle>
            <Button size="sm" onClick={() => {
              setEditing({ code: '', name: '', description: '', owner_role: '', display_order: sections.length + 1 })
              setIsNew(true)
            }}>
              <Plus size={14} className="mr-1" /> Nuova
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-sw-border">
                <th className="text-left py-2 text-sw-text-mid font-medium">Codice</th>
                <th className="text-left py-2 text-sw-text-mid font-medium">Nome</th>
                <th className="text-left py-2 text-sw-text-mid font-medium">Owner</th>
                <th className="text-center py-2 text-sw-text-mid font-medium">Max Score</th>
                <th className="text-right py-2 text-sw-text-mid font-medium">Azioni</th>
              </tr>
            </thead>
            <tbody>
              {sections.map(s => (
                <tr key={s.id} className="border-b border-sw-border/50">
                  <td className="py-2 font-mono text-xs">{s.code}</td>
                  <td className="py-2">{s.name}</td>
                  <td className="py-2 text-sw-text-mid">{s.owner_role || '—'}</td>
                  <td className="py-2 text-center">{s.max_score_theoretical || '—'}</td>
                  <td className="py-2 text-right space-x-1">
                    <Button size="sm" variant="ghost" onClick={() => { setEditing(s); setIsNew(false) }}>
                      <Pencil size={14} />
                    </Button>
                    <Button size="sm" variant="ghost" onClick={() => handleDelete(s.id)}>
                      <Trash2 size={14} />
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
              <CardTitle className="text-base">{isNew ? 'Nuova Sezione' : 'Modifica Sezione'}</CardTitle>
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
                <label className="text-sm font-medium">Nome</label>
                <Input value={editing.name || ''} onChange={(e) => setEditing({ ...editing, name: e.target.value })} />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Owner Role</label>
                <Input value={editing.owner_role || ''} onChange={(e) => setEditing({ ...editing, owner_role: e.target.value })} />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Ordine</label>
                <Input type="number" value={editing.display_order || 0}
                  onChange={(e) => setEditing({ ...editing, display_order: parseInt(e.target.value) })} />
              </div>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Descrizione</label>
              <Textarea value={editing.description || ''} onChange={(e) => setEditing({ ...editing, description: e.target.value })} />
            </div>
            <Button onClick={handleSave}><Save size={14} className="mr-1" /> Salva</Button>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
