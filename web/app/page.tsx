"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useState } from "react";
import { apiDominios } from "@/lib/api";
import type { DominioMeta } from "@/lib/types";
import { DomainPanel } from "@/components/DomainPanel";
import { HeroSelector } from "@/components/HeroSelector";

export default function Home() {
  const [dominios, setDominios] = useState<DominioMeta[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sel, setSel] = useState<DominioMeta | null>(null);

  useEffect(() => {
    apiDominios()
      .then((d) => setDominios(d.filter((x) => !x.error)))
      .catch((e) => setError(String(e)))
      .finally(() => setCargando(false));
  }, []);

  return (
    <AnimatePresence mode="wait">
      {sel ? (
        <DomainPanel key={sel.id} dominio={sel} onBack={() => setSel(null)} />
      ) : (
        <motion.div
          key="hero"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0, y: -12 }}
          transition={{ duration: 0.3 }}
          className="flex flex-1 flex-col"
        >
          <HeroSelector
            dominios={dominios}
            cargando={cargando}
            error={error}
            onSelect={setSel}
          />
        </motion.div>
      )}
    </AnimatePresence>
  );
}
