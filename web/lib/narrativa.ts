// Capa de copy/traducción: convierte cada dominio técnico en una "misión" con
// lenguaje humano, diálogos de la mascota guía y una explicación de para qué
// sirve en la vida real. Hay un fallback genérico para dominios sin texto propio.
import type { DominioMeta } from "./types";

export type PasoId =
  | "bienvenida"
  | "mundo"
  | "mision"
  | "evolucion"
  | "equipo"
  | "reveal";

export interface Narrativa {
  mascota: string; // nombre de la mascota guía
  emoji: string; // carita/ícono de la mascota
  misionTitulo: string; // título de la misión (paso "tu misión")
  objetivo: string; // frase de objetivo del jugador (tarjeta de mundo)
  unidad: string; // qué representa cada "individuo" (pez, planta, animal…)
  // diálogos cortos de la mascota por paso
  dialogos: Record<PasoId, string>;
  // por qué importa en la vida real (la recompensa de la expo)
  paraQueSirve: string;
}

// --------------------------------------------------------------------------- //
// Narrativa por dominio
// --------------------------------------------------------------------------- //
const POR_DOMINIO: Record<string, Narrativa> = {
  peces_ornamental: {
    mascota: "Nina",
    emoji: "🐠",
    misionTitulo: "Arma el acuario de tus sueños",
    objetivo: "Junta peces que se vean increíbles y convivan en paz.",
    unidad: "peces",
    dialogos: {
      bienvenida:
        "¡Hola! Soy Nina. Vamos a diseñar juntos un acuario perfecto: bonito, sano y sin peleas.",
      mundo: "¿Listo? Elige el mundo que quieras diseñar. ¡El acuario es mi favorito!",
      mision:
        "Cada reto tiene su propia agua y presupuesto. Elige uno y yo me encargo del resto.",
      evolucion:
        "Mira: la computadora prueba miles de acuarios y se queda con los mejores, ronda tras ronda.",
      equipo:
        "¡Estos son tus peces ganadores! Te muestro quiénes son buenos amigos y quiénes mejor ni juntarlos.",
      reveal:
        "¿Viste lo que pasó? Eso fue un algoritmo genético trabajando para ti. Te cuento para qué sirve.",
    },
    paraQueSirve:
      "Diseñar un acuario comunitario es difícil: hay peces que pelean, otros que ensucian mucho y un filtro que no da abasto. Esta IA encuentra en segundos la combinación más bonita y sana que cabe en tu presupuesto.",
  },
  plantas_jardin: {
    mascota: "Verde",
    emoji: "🌱",
    misionTitulo: "Diseña un huerto que se cuida solo",
    objetivo: "Combina plantas que se ayudan entre sí y atraen polinizadores.",
    unidad: "plantas",
    dialogos: {
      bienvenida:
        "¡Hola! Soy Verde. Vamos a diseñar un huerto donde las plantas se ayuden entre ellas.",
      mundo: "Elige tu mundo. ¿Te animas con el huerto? Las plantas tienen mejores amigas de lo que crees.",
      mision: "Cada terreno tiene su clima y presupuesto. Escoge un reto y empezamos.",
      evolucion:
        "La computadora prueba miles de huertos y va quedándose con los que mejor funcionan juntos.",
      equipo:
        "¡Tu huerto ganador! Algunas plantas son grandes amigas (se cuidan); otras compiten por el espacio.",
      reveal:
        "Acabas de usar un algoritmo genético. Te explico por qué esto importa en la vida real.",
    },
    paraQueSirve:
      "En un huerto, algunas plantas se ayudan (fijan nitrógeno, atraen polinizadores) y otras se estorban. La IA arma la mezcla más productiva y equilibrada para tu clima y tu presupuesto.",
  },
  fauna_acuicola: {
    mascota: "Coral",
    emoji: "🐟",
    misionTitulo: "Diseña una granja acuática productiva",
    objetivo: "Combina especies de agua que producen más sin desequilibrar el estanque.",
    unidad: "ejemplares",
    dialogos: {
      bienvenida:
        "¡Hola! Soy Coral. Vamos a diseñar una granja de agua que produzca mucho y se mantenga sana.",
      mundo: "Elige tu mundo. La granja acuática es pura estrategia: ¿le entras?",
      mision: "Cada estanque tiene su capacidad y presupuesto. Elige un reto.",
      evolucion:
        "La computadora prueba miles de combinaciones y conserva las que más producen en equilibrio.",
      equipo:
        "¡Tu granja ganadora! Verás qué especies se complementan y cuáles compiten por el oxígeno.",
      reveal:
        "Eso fue un algoritmo genético. Te cuento para qué sirve fuera de esta pantalla.",
    },
    paraQueSirve:
      "En acuicultura, mezclar bien las especies (peces, camarones…) multiplica la producción sin agotar el oxígeno del estanque. La IA encuentra la combinación más rentable y estable para tu presupuesto.",
  },
  arboles_bosque: {
    mascota: "Roble",
    emoji: "🌳",
    misionTitulo: "Diseña un bosque que captura CO₂",
    objetivo: "Planta árboles que capturan carbono y se ayudan a crecer.",
    unidad: "árboles",
    dialogos: {
      bienvenida:
        "¡Hola! Soy Roble. Vamos a diseñar un bosque que capture mucho CO₂ y crezca fuerte.",
      mundo: "Elige tu mundo. ¿Plantamos un bosque que limpie el aire?",
      mision: "Cada terreno tiene su clima y presupuesto. Escoge un reto y plantamos.",
      evolucion:
        "La computadora prueba miles de bosques y se queda con los que más carbono capturan en equilibrio.",
      equipo:
        "¡Tu bosque ganador! Algunos árboles se ayudan (mejoran el suelo); otros compiten por la luz.",
      reveal:
        "Acabas de usar un algoritmo genético. Te explico por qué esto importa de verdad.",
    },
    paraQueSirve:
      "Reforestar bien no es plantar lo mismo en todos lados: hay árboles que mejoran el suelo para otros y especies que capturan más CO₂. La IA diseña el bosque que más carbono captura para tu terreno y presupuesto.",
  },
  fauna_terrestre: {
    mascota: "Trino",
    emoji: "🐄",
    misionTitulo: "Diseña una granja integrada",
    objetivo: "Combina animales que se complementan y diversifican la producción.",
    unidad: "animales",
    dialogos: {
      bienvenida:
        "¡Hola! Soy Trino. Vamos a diseñar una granja donde los animales se complementen.",
      mundo: "Elige tu mundo. La granja integrada es un rompecabezas precioso: ¿le entras?",
      mision: "Cada finca tiene su tamaño, clima y presupuesto. Elige un reto.",
      evolucion:
        "La computadora prueba miles de granjas y conserva las que mejor se equilibran.",
      equipo:
        "¡Tu granja ganadora! Verás qué animales se complementan y cuáles compiten por el espacio.",
      reveal:
        "Eso fue un algoritmo genético. Te cuento para qué sirve en el mundo real.",
    },
    paraQueSirve:
      "Integrar ganado y aves bien hecho diversifica ingresos: unos pastan lo que otros ignoran, las gallinas controlan plagas, las abejas polinizan. La IA arma la combinación más productiva y equilibrada para tu finca.",
  },
};

// --------------------------------------------------------------------------- //
// Fallback genérico (para cualquier dominio sin texto propio)
// --------------------------------------------------------------------------- //
function narrativaGenerica(dom: DominioMeta): Narrativa {
  const n = dom.etiqueta.toLowerCase();
  return {
    mascota: "Eco",
    emoji: dom.emoji || "🌍",
    misionTitulo: `Diseña tu ${n}`,
    objetivo: "Combina especies que funcionan mejor juntas.",
    unidad: "individuos",
    dialogos: {
      bienvenida: "¡Hola! Soy Eco. Vamos a diseñar juntos el mejor ecosistema posible.",
      mundo: "Elige el mundo que quieras diseñar.",
      mision: "Elige un reto y yo me encargo del resto.",
      evolucion:
        "La computadora prueba miles de combinaciones y se queda con las mejores, ronda tras ronda.",
      equipo: "¡Este es tu equipo ganador! Te muestro quiénes se llevan bien.",
      reveal: "Acabas de usar un algoritmo genético. Te explico para qué sirve.",
    },
    paraQueSirve: `Combinar bien las especies de un(a) ${n} es un problema con miles de posibilidades. La IA encuentra en segundos la mejor combinación que cabe en tu presupuesto.`,
  };
}

export function narrativa(dom: DominioMeta): Narrativa {
  return POR_DOMINIO[dom.id] ?? narrativaGenerica(dom);
}

// --------------------------------------------------------------------------- //
// Metadatos amigables de métricas (para las "fortalezas")
// --------------------------------------------------------------------------- //
interface MetaMetrica {
  etiqueta: string;
  emoji: string;
  menorEsMejor?: boolean;
}

const METRICAS: Record<string, MetaMetrica> = {
  A_e: { etiqueta: "Belleza", emoji: "✨" },
  I_b: { etiqueta: "Variedad de vida", emoji: "🌈" },
  R_v: { etiqueta: "Comodidad", emoji: "🛋️" },
  N_c: { etiqueta: "Paz (sin peleas)", emoji: "🕊️", menorEsMejor: true },
  M_s: { etiqueta: "Equilibrio", emoji: "⚖️", menorEsMejor: true },
  B_div: { etiqueta: "Diversidad", emoji: "🧬" },
  co2: { etiqueta: "CO₂ capturado", emoji: "🌍" },
  biodiv: { etiqueta: "Variedad de vida", emoji: "🌈" },
  eq_pares: { etiqueta: "Buena química", emoji: "🤝" },
  carga: { etiqueta: "Equilibrio", emoji: "⚖️", menorEsMejor: true },
  valor: { etiqueta: "Producción", emoji: "💰" },
};

export function metaMetrica(clave: string): MetaMetrica {
  return METRICAS[clave] ?? { etiqueta: clave, emoji: "•" };
}

export function metricaMenorEsMejor(clave: string): boolean {
  return METRICAS[clave]?.menorEsMejor ?? false;
}
