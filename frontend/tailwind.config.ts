import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        risk: {
          low: '#10b981', // emerald-500
          moderate: '#f59e0b', // amber-500
          high: '#f97316', // orange-500
          extreme: '#ef4444', // red-500
        },
        gray: {
          950: '#0a0a0a',
          900: '#171717',
          850: '#1f1f1f',
          800: '#262626',
        }
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "gradient-conic":
          "conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))",
      },
    },
  },
  plugins: [],
};
export default config;
