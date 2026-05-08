import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";

export default function NotFound() {
  return (
    <div className="mx-auto flex min-h-[60vh] w-full max-w-3xl flex-col items-center justify-center px-4 py-20 text-center">
      <span className="pill pill-violet">404</span>
      <h1 className="text-display mt-6">Ruta no encontrada</h1>
      <p className="mt-4 max-w-lg text-body text-steel-gray">
        La página que buscás no existe o fue removida del servidor de transparencia.
      </p>
      <Button variant="primary" size="lg" className="mt-8" asChild>
        <Link href="/">
          Volver al inicio
          <ArrowRight className="h-4 w-4" />
        </Link>
      </Button>
    </div>
  );
}
