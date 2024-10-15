import axios from "axios";
import tokens from "./tokens.service";

// Create an Axios instance
const instance = axios.create({
    baseURL: process.env.API_URL, // Fallback for local development
    headers: {
        "Content-Type": "application/json",
    },
});

instance.interceptors.request.use(
	(config) => {
		const token = tokens.getToken();
		if (token) {
			config.headers["Authorization"] = "Bearer " + token;
		}
		return config;
	},
	(error) => {
		return Promise.reject(error);
	},
);

export default instance;
