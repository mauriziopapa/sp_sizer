import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '@/lib/api'
import ResultStep from '@/components/sizer/ResultStep'
import { Button } from '@/components/ui/button'
import { ArrowLeft } from 'lucide-react'
import type { SizingResult } from '@/pages/SizerWizard'

export default function SizingDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [result, setResult] = useState<SizingResult | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get(`/sizings/${id}`).then(res => {
      setResult(res.data)
      setLoading(false)
    })
  }, [id])

  if (loading) {
    return <div className="text-center py-8 text-sw-text-mid">Caricamento...</div>
  }

  if (!result) {
    return <div className="text-center py-8 text-sw-text-mid">Sizing non trovato</div>
  }

  return (
    <div className="max-w-4xl mx-auto">
      <Button variant="ghost" onClick={() => navigate('/history')} className="mb-4">
        <ArrowLeft size={16} className="mr-2" /> Torna allo storico
      </Button>
      <ResultStep result={result} />
    </div>
  )
}
