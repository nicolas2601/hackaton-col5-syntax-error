import { Skeleton } from "@/components/ui/skeleton";

export default function Loading() {
  return (
    <div className="mx-auto w-full max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
      <Skeleton className="h-8 w-40" />
      <Skeleton className="mt-3 h-12 w-72" />
      <Skeleton className="mt-2 h-5 w-full max-w-xl" />
      <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-32 w-full" />
        ))}
      </div>
      <div className="mt-8 grid grid-cols-1 gap-4 lg:grid-cols-12">
        <Skeleton className="h-72 lg:col-span-6" />
        <Skeleton className="h-72 lg:col-span-6" />
        <Skeleton className="h-72 lg:col-span-4" />
        <Skeleton className="h-72 lg:col-span-8" />
      </div>
    </div>
  );
}
