/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        gov: {
          navy: "#0f172a",
          dark: "#1e293b",
          blue: "#1d4ed8",
          bluelight: "#eff6ff",
          emerald: "#059669",
          emeraldlight: "#ecfdf5",
          amber: "#d97706",
          amberlight: "#fffbeb",
          rose: "#e11d48",
          roselight: "#fff1f2",
          slate: "#64748b",
          border: "#e2e8f0",
          background: "#f8fafc",
        },
      },
    },
  },
  plugins: [],
};
