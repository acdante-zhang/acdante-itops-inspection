import type { NextConfig } from 'next';

const PYTHON_BACKEND = process.env.PYTHON_API_URL || 'http://127.0.0.1:8000';

const nextConfig: NextConfig = {
  allowedDevOrigins: ['*.dev.coze.site'],
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '*',
        pathname: '/**',
      },
    ],
  },
  async rewrites() {
    return [
      // Proxy /api/v1/* to Python backend when PYTHON_API_URL is set
      // Falls back to Next.js mock API if backend is not available
      {
        source: '/api/v1/:path*',
        destination: `${PYTHON_BACKEND}/api/v1/:path*`,
      },
    ];
  },
};

export default nextConfig;
