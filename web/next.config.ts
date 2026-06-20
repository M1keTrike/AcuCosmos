import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  // Ancla la raíz al directorio de web/ (hay otros lockfiles arriba en el sistema).
  turbopack: { root: path.join(__dirname) },
};

export default nextConfig;
