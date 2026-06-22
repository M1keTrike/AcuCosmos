"use client";

import { Canvas, useFrame } from "@react-three/fiber";
import { Grid, OrbitControls } from "@react-three/drei";
import { Bloom, EffectComposer } from "@react-three/postprocessing";
import { useMemo, useRef } from "react";
import * as THREE from "three";
import type { EspecieMapa } from "@/components/tipos-escena";
import type { EstratoMeta, Forma, ItemEnsamblaje } from "@/lib/types";

const CAP_SP = 14; // máximo de criaturas dibujadas por especie
const CAP_TOTAL = 180; // tope global por rendimiento
const SPACING = 2.1; // separación vertical entre estratos
const TMP = new THREE.Vector3();

// Pseudo-aleatorio determinista (puro): posiciones estables entre renders.
function frand(n: number): number {
  const x = Math.sin(n * 12.9898) * 43758.5453;
  return x - Math.floor(x);
}

interface Bicho {
  key: string;
  forma: Forma;
  color: string;
  x: number;
  y: number;
  z: number;
  phase: number;
}

function yDeEstrato(idx: number, n: number): number {
  return (idx - (n - 1) / 2) * SPACING;
}

function construir(
  ensamblaje: ItemEnsamblaje[],
  especies: EspecieMapa,
  n: number,
  forma: Forma
): Bicho[] {
  const bichos: Bicho[] = [];
  let total = 0;
  for (const it of ensamblaje) {
    const esp = especies.get(it.i);
    if (!esp) continue;
    const banda = Math.max(0, Math.min(n - 1, esp.estrato_idx ?? 0));
    const yBanda = yDeEstrato(banda, n);
    const cuantos = Math.min(it.C, CAP_SP);
    for (let k = 0; k < cuantos; k++) {
      if (total >= CAP_TOTAL) return bichos;
      const s = it.i * 97 + k * 13;
      bichos.push({
        key: `${it.i}-${k}`,
        forma,
        color: esp.color,
        x: (frand(s + 1) - 0.5) * 5.6,
        y: yBanda,
        z: (frand(s + 2) - 0.5) * 5.6,
        phase: frand(s + 3) * Math.PI * 2,
      });
      total++;
    }
  }
  return bichos;
}

// --------------------------------------------------------------------------- //
// Geometrías y materiales compartidos (montados una vez en Contenido)
// --------------------------------------------------------------------------- //
function useRecursos(colores: string[]) {
  const geoms = useMemo(
    () => ({
      esfera: new THREE.SphereGeometry(0.32, 16, 16),
      cola: new THREE.ConeGeometry(0.18, 0.42, 8),
      tallo: new THREE.CylinderGeometry(0.05, 0.07, 0.7, 6),
      flor: new THREE.SphereGeometry(0.22, 14, 14),
      tronco: new THREE.CylinderGeometry(0.08, 0.12, 0.6, 6),
      copa: new THREE.IcosahedronGeometry(0.42, 0),
      cabeza: new THREE.SphereGeometry(0.18, 12, 12),
    }),
    []
  );

  const mats = useMemo(() => {
    const m = new Map<string, THREE.MeshStandardMaterial>();
    for (const c of colores) {
      if (m.has(c)) continue;
      m.set(
        c,
        new THREE.MeshStandardMaterial({
          color: new THREE.Color(c),
          emissive: new THREE.Color(c),
          emissiveIntensity: 0.75,
          roughness: 0.35,
          metalness: 0.1,
        })
      );
    }
    return m;
  }, [colores]);

  const matTallo = useMemo(
    () => new THREE.MeshStandardMaterial({ color: "#3f7d3a", roughness: 0.6 }),
    []
  );
  const matTronco = useMemo(
    () => new THREE.MeshStandardMaterial({ color: "#6b4a2b", roughness: 0.7 }),
    []
  );

  return { geoms, mats, matTallo, matTronco };
}

type Geoms = ReturnType<typeof useRecursos>["geoms"];

function Criatura({
  bicho,
  geoms,
  mat,
  matTallo,
  matTronco,
}: {
  bicho: Bicho;
  geoms: Geoms;
  mat: THREE.Material;
  matTallo: THREE.Material;
  matTronco: THREE.Material;
}) {
  const ref = useRef<THREE.Group>(null);
  // Estado de desplazamiento; se inicializa dentro de useFrame (fuera del render).
  const mov = useRef<{ x: number; z: number; vx: number; vz: number } | null>(null);
  const movil = bicho.forma === "pez" || bicho.forma === "animal";
  const R = 3.0; // se mueven dentro del anillo del estrato

  useFrame((state, dt) => {
    const g = ref.current;
    if (!g) return;
    const t = state.clock.elapsedTime;
    // Entrada suave (escala 0 → 1).
    g.scale.lerp(TMP.set(1, 1, 1), 0.07);

    if (movil) {
      if (!mov.current) {
        const ang = bicho.phase; // dirección inicial determinista
        const vel = 0.7 + frand(bicho.x * 7.1 + bicho.z * 3.3 + 5) * 0.9;
        mov.current = {
          x: bicho.x,
          z: bicho.z,
          vx: Math.cos(ang) * vel,
          vz: Math.sin(ang) * vel,
        };
      }
      const m = mov.current;
      m.x += m.vx * dt;
      m.z += m.vz * dt;
      // Rebote suave en el borde del anillo.
      if (m.x > R) m.x = R - (m.x - R);
      else if (m.x < -R) m.x = -R - (m.x + R);
      if (m.z > R) m.z = R - (m.z - R);
      else if (m.z < -R) m.z = -R - (m.z + R);
      if (Math.abs(m.x) >= R) m.vx = -m.vx;
      if (Math.abs(m.z) >= R) m.vz = -m.vz;
      g.position.set(m.x, bicho.y + Math.sin(t * 1.4 + bicho.phase) * 0.12, m.z);
      g.rotation.y = Math.atan2(m.vz, m.vx); // mira hacia donde nada/camina
    } else {
      g.position.y = bicho.y + Math.sin(t * 1.4 + bicho.phase) * 0.12;
      g.rotation.z = Math.sin(t * 0.8 + bicho.phase) * 0.05;
    }
  });

  return (
    <group ref={ref} position={[bicho.x, bicho.y, bicho.z]} scale={0}>
      {bicho.forma === "pez" && (
        <>
          <mesh geometry={geoms.esfera} material={mat} scale={[1.2, 0.8, 0.7]} dispose={null} />
          <mesh
            geometry={geoms.cola}
            material={mat}
            position={[-0.42, 0, 0]}
            rotation={[0, 0, Math.PI / 2]}
            dispose={null}
          />
        </>
      )}
      {bicho.forma === "animal" && (
        <>
          <mesh geometry={geoms.esfera} material={mat} scale={[1.1, 0.9, 1.25]} dispose={null} />
          <mesh geometry={geoms.cabeza} material={mat} position={[0.32, 0.16, 0]} dispose={null} />
        </>
      )}
      {bicho.forma === "planta" && (
        <>
          <mesh geometry={geoms.tallo} material={matTallo} position={[0, 0.05, 0]} dispose={null} />
          <mesh geometry={geoms.flor} material={mat} position={[0, 0.5, 0]} dispose={null} />
        </>
      )}
      {bicho.forma === "arbol" && (
        <>
          <mesh geometry={geoms.tronco} material={matTronco} position={[0, 0, 0]} dispose={null} />
          <mesh geometry={geoms.copa} material={mat} position={[0, 0.5, 0]} dispose={null} />
        </>
      )}
    </group>
  );
}

function Particulas({ color }: { color: string }) {
  const ref = useRef<THREE.Points>(null);
  const geom = useMemo(() => {
    const N = 240;
    const arr = new Float32Array(N * 3);
    for (let i = 0; i < N; i++) {
      arr[i * 3] = (frand(i + 11) - 0.5) * 20;
      arr[i * 3 + 1] = (frand(i + 22) - 0.5) * 14;
      arr[i * 3 + 2] = (frand(i + 33) - 0.5) * 20;
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.BufferAttribute(arr, 3));
    return g;
  }, []);

  useFrame((_, dt) => {
    const p = ref.current;
    if (!p) return;
    // El array es propiedad de three (vía ref), no un local del render.
    const attr = p.geometry.attributes.position as THREE.BufferAttribute;
    const arr = attr.array as Float32Array;
    for (let i = 1; i < arr.length; i += 3) {
      arr[i] += dt * 0.35;
      if (arr[i] > 7) arr[i] = -7;
    }
    attr.needsUpdate = true;
  });

  return (
    <points ref={ref} geometry={geom}>
      <pointsMaterial
        size={0.07}
        color={color}
        transparent
        opacity={0.55}
        sizeAttenuation
        depthWrite={false}
        blending={THREE.AdditiveBlending}
      />
    </points>
  );
}

function Contenido({
  forma,
  estratos,
  especies,
  ensamblaje,
  tema,
}: Props) {
  const n = Math.max(1, estratos.length);
  const bichos = useMemo(
    () => construir(ensamblaje, especies, n, forma),
    [ensamblaje, especies, n, forma]
  );
  const colores = useMemo(() => bichos.map((b) => b.color), [bichos]);
  const { geoms, mats, matTallo, matTronco } = useRecursos(colores);

  const yFloor = yDeEstrato(0, n) - 1.0;

  return (
    <>
      <ambientLight intensity={0.5} />
      <pointLight position={[6, 8, 6]} intensity={60} color={tema.acento} distance={40} />
      <pointLight position={[-6, -4, -6]} intensity={40} color={tema.acento2} distance={40} />

      {/* Plataformas de estrato (anillos neón) */}
      {estratos.map((e, i) => (
        <mesh key={e.idx} position={[0, yDeEstrato(i, n), 0]} rotation={[-Math.PI / 2, 0, 0]}>
          <ringGeometry args={[3.2, 3.42, 72]} />
          <meshBasicMaterial
            color={tema.acento}
            transparent
            opacity={0.25}
            side={THREE.DoubleSide}
          />
        </mesh>
      ))}

      {/* Rejilla futurista en el piso */}
      <Grid
        position={[0, yFloor, 0]}
        args={[26, 26]}
        cellSize={1}
        cellThickness={0.6}
        cellColor={tema.acento}
        sectionSize={4}
        sectionThickness={1.2}
        sectionColor={tema.acento2}
        fadeDistance={28}
        fadeStrength={1.5}
        infiniteGrid
      />

      {bichos.map((b) => (
        <Criatura
          key={b.key}
          bicho={b}
          geoms={geoms}
          mat={mats.get(b.color) ?? matTallo}
          matTallo={matTallo}
          matTronco={matTronco}
        />
      ))}

      <Particulas color={tema.acento2} />

      <OrbitControls
        enablePan={false}
        enableZoom
        autoRotate
        autoRotateSpeed={0.5}
        minDistance={7}
        maxDistance={18}
        minPolarAngle={0.5}
        maxPolarAngle={1.55}
        target={[0, 0, 0]}
      />
    </>
  );
}

interface Props {
  forma: Forma;
  estratos: EstratoMeta[];
  especies: EspecieMapa;
  ensamblaje: ItemEnsamblaje[];
  tema: { acento: string; acento2: string; fondo: string; fondo2: string };
}

export function Escena3D(props: Props) {
  return (
    <Canvas
      camera={{ position: [0, 1.5, 11], fov: 45 }}
      dpr={[1, 2]}
      gl={{ antialias: true }}
    >
      <color attach="background" args={[props.tema.fondo]} />
      <fog attach="fog" args={[props.tema.fondo, 10, 26]} />
      <Contenido {...props} />
      <EffectComposer>
        <Bloom
          intensity={1.0}
          luminanceThreshold={0.22}
          luminanceSmoothing={0.9}
          mipmapBlur
        />
      </EffectComposer>
    </Canvas>
  );
}
