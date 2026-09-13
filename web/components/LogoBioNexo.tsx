// Logotipo BioNexo (mismo del cartel): hexágono con degradado teal + red de nexos
// (hoja bio verde, nodo central ámbar y nodos azul/teal/verde-oscuro).
export function LogoBioNexo({ size = 56 }: { size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 190 190"
      role="img"
      aria-label="Logotipo BioNexo"
    >
      <defs>
        <linearGradient id="bionexo-lg" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#13A091" />
          <stop offset="1" stopColor="#0B5F57" />
        </linearGradient>
      </defs>
      {/* hexágono (modularidad / motor) */}
      <path
        d="M95 14 L160 51 L160 139 L95 176 L30 139 L30 51 Z"
        fill="none"
        stroke="url(#bionexo-lg)"
        strokeWidth="9"
        strokeLinejoin="round"
      />
      {/* red de nexos (nodos conectados) */}
      <g stroke="#0E2E2B" strokeWidth="6" strokeLinecap="round">
        <line x1="62" y1="74" x2="95" y2="95" />
        <line x1="95" y1="95" x2="128" y2="74" />
        <line x1="95" y1="95" x2="95" y2="134" />
      </g>
      {/* nodo bio: hoja */}
      <path
        d="M62 74 c-16 -2 -26 -16 -24 -30 c14 -2 28 8 28 22 c0 4 -1 6 -4 8 Z"
        fill="#5AA63B"
      />
      {/* nodos */}
      <circle cx="95" cy="95" r="13" fill="#E0922B" />
      <circle cx="128" cy="74" r="10" fill="#2F6FB3" />
      <circle cx="95" cy="134" r="10" fill="#14A0A0" />
      <circle cx="62" cy="74" r="7" fill="#2E7D4F" />
    </svg>
  );
}
