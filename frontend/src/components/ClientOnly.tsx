"use client";

import React, { useEffect, useState } from "react";

/**
 * {
 *   func   : ClientOnly
 *   desc   : Render null tren Server SSR de khong sinh ra bat ky the div nao cho extension Bitdefender chen bis_skin_checked
 *   input  : children (React.ReactNode)
 *   output : React.ReactNode | null
 *   loop   : 0 loops
 * }
 */
export function ClientOnly({ children }: { children: React.ReactNode }) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return null;
  }

  return <>{children}</>;
}
