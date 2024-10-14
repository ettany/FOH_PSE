import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
	plugins: [react()],
	server: {
		host: "0.0.0.0",
		proxy: {
			"/api": {
				target: "https://frolicking-gingersnap-da7582.netlify.app/api",
				changeOrigin: false,
				secure: false,
				ws: true,
			},
		},
	},
});
