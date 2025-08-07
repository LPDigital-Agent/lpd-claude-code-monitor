/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ['localhost'],
  },
  async rewrites() {
    return [
      {
        source: '/api/socket/:path*',
        destination: 'http://localhost:5002/:path*',
      },
      {
        source: '/api/flask/:path*',
        destination: 'http://localhost:5002/:path*',
      },
    ]
  },
}