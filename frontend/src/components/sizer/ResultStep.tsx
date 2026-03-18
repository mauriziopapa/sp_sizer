import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Download, AlertTriangle, Shield, CheckCircle } from 'lucide-react'
import type { SizingResult } from '@/pages/SizerWizard'

interface Props {
  result: SizingResult
}

const SIZE_CONFIG: Record<string, { color: string; emoji: string; bg: string }> = {
  SMALL: { color: 'text-sw-green', emoji: '🟢', bg: 'bg-sw-green/10' },
  PMI: { color: 'text-sw-orange', emoji: '🟡', bg: 'bg-sw-orange/10' },
  ENTERPRISE: { color: 'text-sw-red', emoji: '🔴', bg: 'bg-sw-red/10' },
}

export default function ResultStep({ result }: Props) {
  const sizeConfig = SIZE_CONFIG[result.resulting_size] || SIZE_CONFIG.SMALL
  const globalCompleteness = result.completeness?.global ?? 0
  const criticalFlags = result.triggered_risk_flags_detail?.filter(f => f.severity === 'CRITICAL') || []

  const handleExportPDF = () => {
    window.open(`/api/sizings/${result.id}/export/pdf`, '_blank')
  }

  return (
    <div className="space-y-4">
      {/* Main score card */}
      <Card>
        <CardContent className="pt-6">
          <div className="text-center space-y-4">
            <div className="text-6xl">{sizeConfig.emoji}</div>
            <div>
              <div className={`text-4xl font-bold ${sizeConfig.color}`}>
                {result.normalized_score}
              </div>
              <div className="text-sm text-sw-text-mid mt-1">su 100</div>
            </div>
            <div className={`inline-block rounded-card px-6 py-3 ${sizeConfig.bg}`}>
              <span className={`text-2xl font-bold ${sizeConfig.color}`}>
                {result.resulting_size}
              </span>
            </div>

            {/* Score gauge */}
            <div className="w-full max-w-md mx-auto">
              <div className="relative h-4 rounded-full bg-sw-border overflow-hidden">
                <div className="absolute inset-y-0 left-0 bg-sw-green" style={{ width: '40%' }} />
                <div className="absolute inset-y-0 left-[40%] bg-sw-orange" style={{ width: '30%' }} />
                <div className="absolute inset-y-0 left-[70%] bg-sw-red" style={{ width: '30%' }} />
                <div
                  className="absolute top-0 w-1 h-full bg-sw-navy rounded"
                  style={{ left: `${result.normalized_score}%`, transform: 'translateX(-50%)' }}
                />
              </div>
              <div className="flex justify-between text-xs text-sw-text-sub mt-1">
                <span>0 - SMALL</span>
                <span>41 - PMI</span>
                <span>71 - ENTERPRISE</span>
                <span>100</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Completeness */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <CheckCircle size={18} className={globalCompleteness >= 0.75 ? 'text-sw-green' : 'text-sw-orange'} />
            Completezza: {Math.round(globalCompleteness * 100)}%
          </CardTitle>
        </CardHeader>
        <CardContent>
          {globalCompleteness < 0.75 && (
            <div className="p-3 rounded-input bg-sw-orange/10 text-sw-orange text-sm mb-3">
              Attenzione: completezza inferiore al 75%. Il sizing non può essere marcato come completato.
            </div>
          )}
          <div className="grid grid-cols-2 gap-4">
            {Object.entries(result.completeness)
              .filter(([k]) => k !== 'global')
              .map(([section, pct]) => (
                <div key={section} className="flex items-center justify-between">
                  <span className="text-sm text-sw-text-mid">{section}</span>
                  <span className="text-sm font-semibold">{Math.round((pct as number) * 100)}%</span>
                </div>
              ))}
          </div>
        </CardContent>
      </Card>

      {/* Section scores */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Punteggi per Sezione</CardTitle>
        </CardHeader>
        <CardContent>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-sw-border">
                <th className="text-left py-2 text-sw-text-mid font-medium">Sezione</th>
                <th className="text-right py-2 text-sw-text-mid font-medium">Punteggio</th>
                <th className="text-right py-2 text-sw-text-mid font-medium">Massimo</th>
                <th className="text-right py-2 text-sw-text-mid font-medium">%</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(result.section_scores).map(([code, scores]) => (
                <tr key={code} className="border-b border-sw-border/50">
                  <td className="py-2 font-medium">{code}</td>
                  <td className="py-2 text-right">{scores.raw}</td>
                  <td className="py-2 text-right text-sw-text-mid">{scores.max}</td>
                  <td className="py-2 text-right font-semibold">
                    {scores.max > 0 ? Math.round((scores.raw / scores.max) * 100) : 0}%
                  </td>
                </tr>
              ))}
              <tr className="font-bold">
                <td className="py-2">TOTALE</td>
                <td className="py-2 text-right">{result.total_raw_score}</td>
                <td className="py-2 text-right text-sw-text-mid">{result.total_max_score}</td>
                <td className="py-2 text-right">{result.normalized_score}%</td>
              </tr>
            </tbody>
          </table>
        </CardContent>
      </Card>

      {/* Governance rules */}
      {result.governance_rules?.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Shield size={18} className="text-sw-blue" />
              Governance Applicata ({result.resulting_size})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-sw-border">
                  <th className="text-left py-2 text-sw-text-mid font-medium">Elemento</th>
                  <th className="text-left py-2 text-sw-text-mid font-medium">Valore</th>
                </tr>
              </thead>
              <tbody>
                {result.governance_rules.map((rule, i) => (
                  <tr key={i} className="border-b border-sw-border/50">
                    <td className="py-2 font-medium">{rule.element}</td>
                    <td className="py-2">{rule.value}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>
      )}

      {/* Risk flags */}
      {result.triggered_risk_flags_detail?.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <AlertTriangle size={18} className="text-sw-red" />
              Risk Flags Attivati
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {criticalFlags.length >= 2 && (
              <div className="p-3 rounded-input bg-sw-red/10 text-sw-red text-sm font-semibold">
                {'>'}= 2 risk flags CRITICAL: coinvolgimento COO/SPO obbligatorio prima di G1
              </div>
            )}
            {result.triggered_risk_flags_detail.map(flag => (
              <div key={flag.code} className="flex items-start gap-3 p-3 rounded-input bg-sw-bg">
                <Badge variant={flag.severity === 'CRITICAL' ? 'destructive' : 'warning'}>
                  {flag.severity}
                </Badge>
                <div>
                  <div className="font-medium text-sm">{flag.label}</div>
                  <div className="text-xs text-sw-text-mid mt-0.5">{flag.description}</div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Actions */}
      <div className="flex justify-center gap-4 pt-4">
        <Button onClick={handleExportPDF} variant="outline">
          <Download size={16} className="mr-2" /> Esporta PDF
        </Button>
      </div>
    </div>
  )
}
