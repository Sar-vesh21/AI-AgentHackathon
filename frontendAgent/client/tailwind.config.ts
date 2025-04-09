import type { Config } from "tailwindcss";
import tailwindAnimate from "tailwindcss-animate";

export default {
    darkMode: ["class"],
    content: ["src/**/*.{ts,tsx}", "components/**/*.{ts,tsx}"],
    theme: {
    	extend: {
    		fontFamily: {
    			sans: [
    				'Inter',
    				'ui-sans-serif',
    				'system-ui',
    				'sans-serif',
    				'Apple Color Emoji',
    				'Segoe UI Emoji',
    				'Segoe UI Symbol',
    				'Noto Color Emoji'
    			]
    		},
    		borderRadius: {
    			lg: 'var(--radius)',
    			md: 'calc(var(--radius) - 2px)',
    			sm: 'calc(var(--radius) - 4px)'
    		},
            container: {
                center: true,
                padding: "2rem",
            },
    		colors: {
    			border: "rgb(38, 38, 38)",
    			input: "rgb(38, 38, 38)",
    			ring: "rgb(38, 38, 38)",
    			background: "rgb(0, 0, 0)",
    			foreground: "rgb(250, 250, 250)",
    			surface: {
    				DEFAULT: "rgb(23, 23, 23)",
    				light: "rgb(38, 38, 38)",
    			},
    			primary: {
    				DEFAULT: "rgb(16, 185, 129)",
    				foreground: "rgb(250, 250, 250)",
    				light: "rgba(16, 185, 129, 0.1)",
    			},
    			secondary: {
    				DEFAULT: "rgb(38, 38, 38)",
    				foreground: "rgb(250, 250, 250)",
    			},
    			destructive: {
    				DEFAULT: "rgb(239, 68, 68)",
    				foreground: "rgb(250, 250, 250)",
    			},
    			muted: {
    				DEFAULT: "rgb(38, 38, 38)",
    				foreground: "rgb(115, 115, 115)",
    			},
    			accent: {
    				DEFAULT: "rgb(38, 38, 38)",
    				foreground: "rgb(250, 250, 250)",
    			},
    			popover: {
    				DEFAULT: "rgb(23, 23, 23)",
    				foreground: "rgb(250, 250, 250)",
    			},
    			card: {
    				DEFAULT: "rgb(23, 23, 23)",
    				foreground: "rgb(250, 250, 250)",
    			},
    			chart: {
    				'1': "rgb(16, 185, 129)",
    				'2': "rgb(59, 130, 246)",
    				'3': "rgb(239, 68, 68)",
    				'4': "rgb(245, 158, 11)",
    				'5': "rgb(168, 85, 247)",
    			},
    			sidebar: {
    				DEFAULT: "rgb(23, 23, 23)",
    				foreground: "rgb(250, 250, 250)",
    				primary: "rgb(16, 185, 129)",
    				'primary-foreground': "rgb(250, 250, 250)",
    				accent: "rgb(38, 38, 38)",
    				'accent-foreground': "rgb(250, 250, 250)",
    				border: "rgb(38, 38, 38)",
    				ring: "rgb(38, 38, 38)",
    			}
    		},
            backgroundImage: {
                'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
                'gradient-dark': 'linear-gradient(to bottom, rgb(17, 17, 17), rgb(0, 0, 0))',
            }
    	}
    },
    plugins: [tailwindAnimate],
} satisfies Config;
