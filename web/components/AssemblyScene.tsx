"use client";

import { useEffect, useRef, useState } from "react";
import type { EspecieMapa } from "./tipos-escena";
import type { EstratoMeta, Forma, ItemEnsamblaje } from "@/lib/types";

interface Creatura {
  sp: number;
  x: number;
  y: number;
  vx: number;
  vy: number;
  r: number;
  color: string;
  phase: number;
  alpha: number;
  yTop: number;
  yBot: number;
}

interface Ambiente {
  x: number;
  y: number;
  v: number;
  r: number;
  vida: number;
}

const CAP = 30; // máximo de criaturas dibujadas por especie (la tabla da el conteo exacto)

const RADIO: Record<Forma, [number, number]> = {
  pez: [7, 17],
  planta: [13, 26],
  arbol: [16, 40],
  animal: [12, 26],
};

export function AssemblyScene({
  forma,
  estratos,
  especies,
  ensamblaje,
  tema,
}: {
  forma: Forma;
  estratos: EstratoMeta[];
  especies: EspecieMapa;
  ensamblaje: ItemEnsamblaje[];
  tema: { acento: string; acento2: string; fondo: string; fondo2: string };
}) {
  const wrapRef = useRef<HTMLDivElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const creaturasRef = useRef<Creatura[]>([]);
  const ambienteRef = useRef<Ambiente[]>([]);
  const dimsRef = useRef({ w: 0, h: 0, dpr: 1 });
  const cfgRef = useRef({ forma, estratos, especies, tema });
  cfgRef.current = { forma, estratos, especies, tema };

  const [dims, setDims] = useState({ w: 0, h: 0 });

  // Tamaño responsivo (con devicePixelRatio para nitidez).
  useEffect(() => {
    const el = wrapRef.current;
    if (!el) return;
    const ro = new ResizeObserver(() => {
      const r = el.getBoundingClientRect();
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      dimsRef.current = { w: r.width, h: r.height, dpr };
      const c = canvasRef.current;
      if (c) {
        c.width = Math.round(r.width * dpr);
        c.height = Math.round(r.height * dpr);
      }
      setDims({ w: r.width, h: r.height });
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  const movil = forma === "pez" || forma === "animal";

  // Reconciliar criaturas cuando cambia el ensamblaje (o el tamaño).
  useEffect(() => {
    const { w, h } = dims;
    if (!w || !h) return;
    const n = Math.max(1, estratos.length);
    const [rmin, rmax] = RADIO[forma];

    const deseado = new Map<number, number>();
    for (const it of ensamblaje) deseado.set(it.i, Math.min(it.C, CAP));

    const tamanos = [...deseado.keys()]
      .map((sp) => especies.get(sp)?.tamano ?? 1)
      .filter((t): t is number => t != null && t > 0);
    const tmin = tamanos.length ? Math.min(...tamanos) : 1;
    const tmax = tamanos.length ? Math.max(...tamanos) : 1;
    const radio = (t: number | null) => {
      const v = t == null || tmax <= tmin ? 0.5 : (t - tmin) / (tmax - tmin);
      return rmin + v * (rmax - rmin);
    };
    const banda = (b: number) => {
      const pad = h * 0.04;
      const yTop = h * (1 - (b + 1) / n) + pad;
      const yBot = h * (1 - b / n) - pad;
      return [yTop, yBot] as const;
    };

    const previas = creaturasRef.current;
    const porSp = new Map<number, Creatura[]>();
    for (const c of previas) {
      const l = porSp.get(c.sp) ?? [];
      l.push(c);
      porSp.set(c.sp, l);
    }

    const siguientes: Creatura[] = [];
    for (const [sp, d] of deseado) {
      const esp = especies.get(sp);
      if (!esp) continue;
      const b = Math.max(0, Math.min(n - 1, esp.estrato_idx ?? 0));
      const [yTop, yBot] = banda(b);
      const r = radio(esp.tamano);
      const existentes = porSp.get(sp) ?? [];
      for (let k = 0; k < d; k++) {
        if (k < existentes.length) {
          const c = existentes[k];
          c.r = r;
          c.color = esp.color;
          c.yTop = yTop;
          c.yBot = yBot;
          siguientes.push(c);
        } else {
          const speed = movil ? 0.4 + Math.random() * 1.0 : 0;
          siguientes.push({
            sp,
            x: Math.random() * w,
            y: yTop + Math.random() * (yBot - yTop),
            vx: movil ? (Math.random() < 0.5 ? -1 : 1) * speed : 0,
            vy: movil ? (Math.random() - 0.5) * 0.3 : 0,
            r,
            color: esp.color,
            phase: Math.random() * Math.PI * 2,
            alpha: 0,
            yTop,
            yBot,
          });
        }
      }
    }
    creaturasRef.current = siguientes;
  }, [ensamblaje, especies, estratos, dims, forma, movil]);

  // Partículas ambientales (burbujas / motas) una sola vez por tamaño.
  useEffect(() => {
    const { w, h } = dims;
    if (!w || !h) return;
    ambienteRef.current = Array.from({ length: 16 }, () => ({
      x: Math.random() * w,
      y: Math.random() * h,
      v: 0.2 + Math.random() * 0.6,
      r: 1 + Math.random() * 2.5,
      vida: Math.random(),
    }));
  }, [dims]);

  // Bucle de animación (se inicia una vez).
  useEffect(() => {
    let raf = 0;
    const render = (t: number) => {
      const c = canvasRef.current;
      const ctx = c?.getContext("2d");
      const { w, h, dpr } = dimsRef.current;
      if (ctx && w && h) {
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        dibujar(ctx, w, h, t, cfgRef.current, creaturasRef.current, ambienteRef.current);
      }
      raf = requestAnimationFrame(render);
    };
    raf = requestAnimationFrame(render);
    return () => cancelAnimationFrame(raf);
  }, []);

  const vacio = ensamblaje.length === 0;

  return (
    <div
      ref={wrapRef}
      className="relative h-full w-full overflow-hidden rounded-2xl border border-borde"
    >
      <canvas ref={canvasRef} className="block h-full w-full" />
      {/* etiquetas de estrato */}
      <div className="pointer-events-none absolute inset-0 flex flex-col">
        {[...estratos].reverse().map((e) => (
          <div
            key={e.idx}
            className="flex flex-1 items-start border-t border-white/5 px-3 pt-1"
          >
            <span className="rounded bg-black/25 px-1.5 py-0.5 text-[10px] uppercase tracking-wide text-white/55">
              {e.etiqueta}
            </span>
          </div>
        ))}
      </div>
      {vacio && (
        <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
          <span className="rounded-full bg-black/40 px-4 py-2 text-sm text-white/70">
            Ejecuta el AG para ver el ensamblaje armarse aquí
          </span>
        </div>
      )}
    </div>
  );
}

// --------------------------------------------------------------------------- //
// Dibujo
// --------------------------------------------------------------------------- //
function dibujar(
  ctx: CanvasRenderingContext2D,
  w: number,
  h: number,
  t: number,
  cfg: { forma: Forma; estratos: EstratoMeta[]; tema: { fondo: string; fondo2: string } },
  cre: Creatura[],
  amb: Ambiente[]
) {
  const { forma, estratos, tema } = cfg;
  const acuatico = forma === "pez";

  // Fondo en gradiente vertical (tema del dominio).
  const g = ctx.createLinearGradient(0, 0, 0, h);
  g.addColorStop(0, tema.fondo2);
  g.addColorStop(1, tema.fondo);
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, w, h);

  // Suelo para escenas terrestres.
  if (!acuatico) {
    ctx.fillStyle = "rgba(0,0,0,0.25)";
    ctx.fillRect(0, h * (1 - 1 / Math.max(1, estratos.length)), w, h);
  }

  // Separadores de banda.
  const n = Math.max(1, estratos.length);
  ctx.strokeStyle = "rgba(255,255,255,0.06)";
  ctx.lineWidth = 1;
  for (let b = 1; b < n; b++) {
    const y = h * (1 - b / n);
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(w, y);
    ctx.stroke();
  }

  // Partículas ambientales.
  for (const p of amb) {
    if (acuatico) {
      p.y -= p.v;
      if (p.y < -4) {
        p.y = h + 4;
        p.x = Math.random() * w;
      }
    } else {
      p.x += p.v * 0.4;
      p.y += Math.sin(t * 0.001 + p.vida * 6) * 0.2;
      if (p.x > w + 4) p.x = -4;
    }
    ctx.beginPath();
    ctx.fillStyle = acuatico ? "rgba(255,255,255,0.12)" : "rgba(255,255,255,0.08)";
    ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
    ctx.fill();
  }

  // Criaturas.
  for (const c of cre) {
    c.alpha = Math.min(1, c.alpha + 0.025);
    if (c.vx !== 0 || c.vy !== 0) {
      c.x += c.vx;
      c.y += c.vy;
      const m = c.r + 6;
      if (c.x < -m) c.x = w + m;
      if (c.x > w + m) c.x = -m;
      if (c.y < c.yTop) c.vy = Math.abs(c.vy);
      if (c.y > c.yBot) c.vy = -Math.abs(c.vy);
    }
    ctx.save();
    ctx.globalAlpha = c.alpha;
    const bob = Math.sin(t * 0.003 + c.phase) * 2;
    if (forma === "pez") dibujarPez(ctx, c, bob);
    else if (forma === "animal") dibujarAnimal(ctx, c, bob);
    else if (forma === "arbol") dibujarArbol(ctx, c, t);
    else dibujarPlanta(ctx, c, t);
    ctx.restore();
  }
}

function dibujarPez(ctx: CanvasRenderingContext2D, c: Creatura, bob: number) {
  const dir = c.vx < 0 ? -1 : 1;
  ctx.translate(c.x, c.y + bob);
  ctx.scale(dir, 1);
  // cola
  ctx.fillStyle = c.color;
  ctx.beginPath();
  ctx.moveTo(-c.r * 0.9, 0);
  ctx.lineTo(-c.r * 1.5, -c.r * 0.55);
  ctx.lineTo(-c.r * 1.5, c.r * 0.55);
  ctx.closePath();
  ctx.fill();
  // cuerpo
  ctx.beginPath();
  ctx.ellipse(0, 0, c.r, c.r * 0.6, 0, 0, Math.PI * 2);
  ctx.fill();
  // ojo
  ctx.fillStyle = "rgba(255,255,255,0.9)";
  ctx.beginPath();
  ctx.arc(c.r * 0.45, -c.r * 0.12, c.r * 0.14, 0, Math.PI * 2);
  ctx.fill();
}

function dibujarAnimal(ctx: CanvasRenderingContext2D, c: Creatura, bob: number) {
  const dir = c.vx < 0 ? -1 : 1;
  ctx.translate(c.x, c.y + bob);
  ctx.scale(dir, 1);
  ctx.strokeStyle = "rgba(0,0,0,0.4)";
  ctx.lineWidth = Math.max(1, c.r * 0.12);
  // patas
  for (const px of [-c.r * 0.5, c.r * 0.5]) {
    ctx.beginPath();
    ctx.moveTo(px, c.r * 0.4);
    ctx.lineTo(px, c.r * 0.85);
    ctx.stroke();
  }
  // cuerpo
  ctx.fillStyle = c.color;
  ctx.beginPath();
  ctx.ellipse(0, 0, c.r, c.r * 0.66, 0, 0, Math.PI * 2);
  ctx.fill();
  // cabeza
  ctx.beginPath();
  ctx.arc(c.r * 0.9, -c.r * 0.2, c.r * 0.45, 0, Math.PI * 2);
  ctx.fill();
}

function dibujarPlanta(ctx: CanvasRenderingContext2D, c: Creatura, t: number) {
  const sway = Math.sin(t * 0.0016 + c.phase) * 0.1;
  ctx.translate(c.x, c.yBot);
  ctx.rotate(sway);
  // tallo
  ctx.strokeStyle = "#3f7d3a";
  ctx.lineWidth = Math.max(1.5, c.r * 0.16);
  ctx.beginPath();
  ctx.moveTo(0, 0);
  ctx.lineTo(0, -c.r * 1.4);
  ctx.stroke();
  // hojas
  ctx.fillStyle = "#4e9a45";
  for (const s of [-1, 1]) {
    ctx.beginPath();
    ctx.ellipse(s * c.r * 0.35, -c.r * 0.7, c.r * 0.4, c.r * 0.2, s * 0.6, 0, Math.PI * 2);
    ctx.fill();
  }
  // flor / fruto (color del grupo)
  ctx.fillStyle = c.color;
  ctx.beginPath();
  ctx.arc(0, -c.r * 1.5, c.r * 0.5, 0, Math.PI * 2);
  ctx.fill();
}

function dibujarArbol(ctx: CanvasRenderingContext2D, c: Creatura, t: number) {
  const sway = Math.sin(t * 0.0012 + c.phase) * 0.05;
  ctx.translate(c.x, c.yBot);
  // tronco
  ctx.fillStyle = "#6b4a2b";
  ctx.fillRect(-c.r * 0.12, -c.r * 1.1, c.r * 0.24, c.r * 1.1);
  ctx.rotate(sway);
  // copa (color del uso/grupo)
  ctx.fillStyle = c.color;
  ctx.globalAlpha = ctx.globalAlpha * 0.95;
  ctx.beginPath();
  ctx.arc(0, -c.r * 1.4, c.r * 0.85, 0, Math.PI * 2);
  ctx.fill();
  ctx.beginPath();
  ctx.arc(-c.r * 0.55, -c.r * 1.05, c.r * 0.55, 0, Math.PI * 2);
  ctx.fill();
  ctx.beginPath();
  ctx.arc(c.r * 0.55, -c.r * 1.05, c.r * 0.55, 0, Math.PI * 2);
  ctx.fill();
}
