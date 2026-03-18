import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import api from '@/lib/api'
import { Eye, Download, Search } from 'lucide-react'

interface SizingItem {
  id: number
  project_name: string
  client_name: string | null
  compiled_by: string | null
  sizing_date: string
  normalized_score: number
  resulting_size: string
  status: string
  created_at: string
}

const SIZE_BADGE: Record<string, 'success' | 'warning' | 'destructive'> = {
  SMALL: 'success',
  PMI: 'warning',
  ENTERPRISE: 'destructive',
}

export default function History() {
  const navigate = useNavigate()
  const [sizings, setSizings] = useState<SizingItem[]>([])
  const [filter, setFilter] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/sizings').then(res => {
      setSizings(res.data)
      setLoading(false)
    })
  }, [])

  const filtered = sizings.filter(s =>
    s.project_name.toLowerCase().includes(filter.toLowerCase()) ||
    (s.client_name || '').toLowerCase().includes(filter.toLowerCase())
  )

  return (
    <div className="max-w-4xl mx-auto">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Storico Sizing</CardTitle>
            <div className="relative w-64">
              <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-sw-text-sub" />
              <Input
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                placeholder="Cerca progetto..."
                className="pl-9"
              />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8 text-sw-text-mid">Caricamento...</div>
          ) : filtered.length === 0 ? (
            <div className="text-center py-8 text-sw-text-mid">
              {filter ? 'Nessun risultato' : 'Nessun sizing eseguito'}
            </div>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-sw-border">
                  <th className="text-left py-3 text-sw-text-mid font-medium">Progetto</th>
                  <th className="text-left py-3 text-sw-text-mid font-medium">Cliente</th>
                  <th className="text-center py-3 text-sw-text-mid font-medium">Score</th>
                  <th className="text-center py-3 text-sw-text-mid font-medium">Size</th>
                  <th className="text-center py-3 text-sw-text-mid font-medium">Status</th>
                  <th className="text-left py-3 text-sw-text-mid font-medium">Data</th>
                  <th className="text-right py-3 text-sw-text-mid font-medium">Azioni</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map(sizing => (
                  <tr key={sizing.id} className="border-b border-sw-border/50 hover:bg-sw-bg/50">
                    <td className="py-3 font-medium">{sizing.project_name}</td>
                    <td className="py-3 text-sw-text-mid">{sizing.client_name || '—'}</td>
                    <td className="py-3 text-center font-semibold">{sizing.normalized_score}</td>
                    <td className="py-3 text-center">
                      <Badge variant={SIZE_BADGE[sizing.resulting_size] || 'secondary'}>
                        {sizing.resulting_size}
                      </Badge>
                    </td>
                    <td className="py-3 text-center">
                      <Badge variant={sizing.status === 'COMPLETED' ? 'success' : 'secondary'}>
                        {sizing.status}
                      </Badge>
                    </td>
                    <td className="py-3 text-sw-text-mid">
                      {new Date(sizing.sizing_date).toLocaleDateString('it-IT')}
                    </td>
                    <td className="py-3 text-right space-x-1">
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => navigate(`/history/${sizing.id}`)}
                      >
                        <Eye size={14} />
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => window.open(`/api/sizings/${sizing.id}/export/pdf`, '_blank')}
                      >
                        <Download size={14} />
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
