"use client";

import { Fragment, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { ChevronDown } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { formatCOP } from "@/lib/utils";
import type { Anomalia, AnomaliaVerdict } from "@/types";

const VERDICT_VARIANT: Record<AnomaliaVerdict, "success" | "warning" | "danger"> = {
  VERIDICO: "success",
  REVISAR: "warning",
  FALSO: "danger",
};

const SUSTENTO_PREVIEW = 140;

export function AnomaliasTable({ rows }: { rows: Anomalia[] }) {
  const [open, setOpen] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

  return (
    <section className="card-simple p-0">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-12"></TableHead>
            <TableHead>ID</TableHead>
            <TableHead>Entidad</TableHead>
            <TableHead>Contratista</TableHead>
            <TableHead className="text-right">Valor</TableHead>
            <TableHead>Modalidad</TableHead>
            <TableHead>Fecha</TableHead>
            <TableHead className="text-right">Veredicto</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.map((row) => {
            const isOpen = open === row.id;
            const isExpanded = expanded[row.id];
            const sustento = row.sustento ?? "";
            const tooLong = sustento.length > SUSTENTO_PREVIEW;
            const previewText =
              tooLong && !isExpanded
                ? `${sustento.slice(0, SUSTENTO_PREVIEW).trim()}…`
                : sustento;
            return (
              <Fragment key={row.id}>
                <TableRow
                  onClick={() => setOpen(isOpen ? null : row.id)}
                  className="cursor-pointer transition-colors hover:bg-ghost-fill/60"
                >
                  <TableCell>
                    <motion.span
                      animate={{ rotate: isOpen ? 180 : 0 }}
                      transition={{ duration: 0.18, ease: [0.22, 1, 0.36, 1] }}
                      className="inline-block text-cloud-gray"
                    >
                      <ChevronDown className="h-4 w-4" />
                    </motion.span>
                  </TableCell>
                  <TableCell className="font-mono text-[12px] text-cloud-gray">
                    {row.id}
                  </TableCell>
                  <TableCell className="font-medium text-midnight-ink">
                    {row.entidad}
                  </TableCell>
                  <TableCell>{row.contratista}</TableCell>
                  <TableCell className="text-right font-mono">
                    {formatCOP(row.valor, { compact: true })}
                  </TableCell>
                  <TableCell>{row.modalidad}</TableCell>
                  <TableCell className="font-mono text-[12px] text-steel-gray">
                    {row.fecha}
                  </TableCell>
                  <TableCell className="text-right">
                    <Badge variant={VERDICT_VARIANT[row.verdict]}>
                      {row.verdict}
                    </Badge>
                  </TableCell>
                </TableRow>
                <AnimatePresence initial={false}>
                  {isOpen && (
                    <motion.tr
                      key={`${row.id}-detail`}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      transition={{ duration: 0.15 }}
                      className="bg-ghost-fill"
                    >
                      <td colSpan={8} className="p-0">
                        <motion.div
                          initial={{ height: 0 }}
                          animate={{ height: "auto" }}
                          exit={{ height: 0 }}
                          transition={{
                            duration: 0.25,
                            ease: [0.22, 1, 0.36, 1],
                          }}
                          className="overflow-hidden"
                        >
                          <div className="grid gap-4 px-5 py-4 sm:grid-cols-[180px,1fr]">
                            <div>
                              <div className="text-[11px] uppercase tracking-wider text-cloud-gray">
                                Sustento IA
                              </div>
                              <div className="mt-1 text-[12px] text-steel-gray">
                                Heurística estadística + LLM
                              </div>
                            </div>
                            <div>
                              <p
                                className={`text-[13px] leading-relaxed text-deep-indigo ${
                                  !isExpanded && tooLong
                                    ? "line-clamp-2"
                                    : ""
                                }`}
                              >
                                {previewText}
                              </p>
                              {tooLong && (
                                <button
                                  type="button"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    setExpanded((prev) => ({
                                      ...prev,
                                      [row.id]: !prev[row.id],
                                    }));
                                  }}
                                  className="mt-2 text-[11px] font-medium text-electric-violet hover:underline"
                                >
                                  {isExpanded ? "ver menos" : "ver más"}
                                </button>
                              )}
                            </div>
                          </div>
                        </motion.div>
                      </td>
                    </motion.tr>
                  )}
                </AnimatePresence>
              </Fragment>
            );
          })}
        </TableBody>
      </Table>
    </section>
  );
}
