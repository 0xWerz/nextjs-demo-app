import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    // Allow domains for SSRF testing
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'httpbin.org',
        pathname: '/**',
      },
      {
        // DNS rebinding test - user's domain
        protocol: 'http',
        hostname: 'qyst.werz.xyz',
        pathname: '/**',
      },
      {
        // Also allow any subdomain of werz.xyz
        protocol: 'http',
        hostname: '*.werz.xyz',
        pathname: '/**',
      },
    ],
  },
};

export default nextConfig;
