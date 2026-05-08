import { api } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { AnomaliasTable } from "./_table";

export const dynamic = "force-dynamic";
export const revalidate = 60;

export default async function AnomaliasPage() {
  const anomalias = await api.anomalias();
  const counts = anomalias.reduce(
    (acc, a) => {
      acc[a.verdict] = (acc[a.verdict] ?? 0) + 1;
      return acc;
    },
    {} as Record<string, number>,
  );

  return (
    <div className="mx-auto w-full max-w-[1600px] px-4 py-10 sm:px-6 lg:px-10">
      <header className="mb-8">
        <span className="text-mono uppercase tracking-wider text-cloud-gray">
          · Auditoría IA
        </span>
        <h1 className="text-heading mt-2">Anomalías top 20</h1>
        <p className="mt-2 max-w-2xl text-body text-steel-gray">
          Contratos con valores estadísticamente atípicos, clasificados por IA con
          sustento expandible. Clic en cualquier fila para ver el razonamiento.
        </p>
        <div className="mt-4 flex flex-wrap gap-2">
          <Badge variant="success">Verídico · {counts.VERIDICO ?? 0}</Badge>
          <Badge variant="warning">Revisar · {counts.REVISAR ?? 0}</Badge>
          <Badge variant="danger">Falso · {counts.FALSO ?? 0}</Badge>
        </div>
      </header>

      <AnomaliasTable rows={anomalias} />
    </div>
  );
}
