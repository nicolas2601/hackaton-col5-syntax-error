"use client";

import { useEffect } from "react";
import { Button } from "@/components/ui/button";
import { AlertTriangle } from "lucide-react";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="mx-auto flex min-h-[60vh] w-full max-w-3xl flex-col items-center justify-center px-4 py-20 text-center">
      <span className="grid h-12 w-12 place-items-center rounded-[12px] bg-rose-50 text-rose-600">
        <AlertTriangle className="h-6 w-6" />
      </span>
      <h1 className="text-heading mt-4">Algo salió mal</h1>
      <p className="mt-2 max-w-lg text-body text-steel-gray">
        Hubo un error procesando los datos. Si el problema persiste, revisá el
        estado del API SECOP II.
      </p>
      {error.digest && (
        <p className="mt-2 text-mono text-cloud-gray">digest · {error.digest}</p>
      )}
      <Button variant="primary" className="mt-6" onClick={reset}>
        Reintentar
      </Button>
    </div>
  );
}
