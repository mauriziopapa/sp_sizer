import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import type { ProjectInfo } from '@/pages/SizerWizard'

interface Props {
  info: ProjectInfo
  onChange: (info: ProjectInfo) => void
}

export default function ProjectInfoStep({ info, onChange }: Props) {
  const update = (field: keyof ProjectInfo, value: string) => {
    onChange({ ...info, [field]: value })
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Dati Progetto</CardTitle>
        <CardDescription>Inserisci le informazioni di base del progetto da classificare</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <label className="text-sm font-medium text-sw-text">Nome Progetto *</label>
            <Input
              value={info.project_name}
              onChange={(e) => update('project_name', e.target.value)}
              placeholder="es. Implementazione CRM Acme Corp"
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium text-sw-text">Cliente</label>
            <Input
              value={info.client_name}
              onChange={(e) => update('client_name', e.target.value)}
              placeholder="es. Acme Corp"
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium text-sw-text">Compilato da (AM)</label>
            <Input
              value={info.compiled_by}
              onChange={(e) => update('compiled_by', e.target.value)}
              placeholder="Nome Account Manager"
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium text-sw-text">Validato da (PM)</label>
            <Input
              value={info.validated_by}
              onChange={(e) => update('validated_by', e.target.value)}
              placeholder="Nome Project Manager"
            />
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
