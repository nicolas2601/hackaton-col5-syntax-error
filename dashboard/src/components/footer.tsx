import Link from "next/link";
import { Github, ExternalLink } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t border-lava-cloud bg-off-white">
      <div className="mx-auto grid max-w-7xl gap-8 px-4 py-12 sm:grid-cols-2 sm:px-6 lg:grid-cols-4 lg:px-8">
        <div className="col-span-2">
          <div className="flex items-center gap-2">
            <span className="grid h-8 w-8 place-items-center rounded-[8px] bg-electric-violet text-white text-[14px] font-semibold">
              S
            </span>
            <span className="font-display text-[18px] font-semibold tracking-[-0.02em]">
              SECOP<span className="text-electric-violet">.</span>II
            </span>
          </div>
          <p className="mt-3 max-w-md text-[13px] text-steel-gray">
            Dashboard de transparencia sobre la contratación pública en Colombia.
            1M+ registros analizados con IA y heurísticas estadísticas.
          </p>
          <p className="mt-3 text-mono text-cloud-gray">
            Hackathon Colombia 5.0 · Tikno Studio
          </p>
        </div>

        <div>
          <h4 className="text-[12px] uppercase tracking-wider text-cloud-gray">Navegación</h4>
          <ul className="mt-3 space-y-2 text-[13px]">
            <li><Link href="/dashboard" className="text-deep-indigo hover:text-electric-violet">Dashboard</Link></li>
            <li><Link href="/mapa" className="text-deep-indigo hover:text-electric-violet">Mapa Colombia</Link></li>
            <li><Link href="/anomalias" className="text-deep-indigo hover:text-electric-violet">Anomalías</Link></li>
            <li><Link href="/pareto" className="text-deep-indigo hover:text-electric-violet">Pareto</Link></li>
            <li><Link href="/genero" className="text-deep-indigo hover:text-electric-violet">Brecha de género</Link></li>
          </ul>
        </div>

        <div>
          <h4 className="text-[12px] uppercase tracking-wider text-cloud-gray">Recursos</h4>
          <ul className="mt-3 space-y-2 text-[13px]">
            <li>
              <a
                href="https://api-ronda2.tikno.pro/docs"
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1 text-deep-indigo hover:text-electric-violet"
              >
                API Docs <ExternalLink className="h-3 w-3" />
              </a>
            </li>
            <li>
              <a
                href="https://www.colombiacompra.gov.co/secop-ii"
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1 text-deep-indigo hover:text-electric-violet"
              >
                SECOP II oficial <ExternalLink className="h-3 w-3" />
              </a>
            </li>
            <li>
              <a
                href="https://www.datos.gov.co/"
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1 text-deep-indigo hover:text-electric-violet"
              >
                Datos abiertos <ExternalLink className="h-3 w-3" />
              </a>
            </li>
            <li>
              <a
                href="https://github.com/tikno"
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1 text-deep-indigo hover:text-electric-violet"
              >
                <Github className="h-3 w-3" /> GitHub
              </a>
            </li>
          </ul>
        </div>
      </div>

      <div className="border-t border-lava-cloud">
        <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-2 px-4 py-4 text-[12px] text-cloud-gray sm:flex-row sm:px-6 lg:px-8">
          <span>© {new Date().getFullYear()} SECOP II Dashboard. Datos públicos.</span>
          <span className="font-mono">build · transparency-mvp</span>
        </div>
      </div>
    </footer>
  );
}
