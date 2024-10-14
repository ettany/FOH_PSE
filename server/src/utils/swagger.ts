import { Express } from "express";
import swaggerJsdoc from "swagger-jsdoc";
import swaggerUi from "swagger-ui-express";
import swaggerAutogen from "swagger-autogen";
import { version } from "../../package.json"; // Make sure the path is correct
import dotenv from "dotenv";

dotenv.config();

const outputFile = "./swagger-output.json"; // Path for the output file
const endpointsFiles = ["./routes"]; // Paths for your routes

function swaggerDocs(app: Express, port: number) {
    const doc = {
        info: {
            title: "Stock Trading Simulator API",
            description: "A REST API for the Stock Trading Simulator",
            version,
        },
        host: "frolicking-gingersnap-da7582.netlify.app", // Your deployed backend link
        securityDefinitions: {
            bearerAuth: {
                type: "http",
                scheme: "bearer",
                bearerFormat: "JWT",
            },
        },
        servers: [
            { url: `https://frolicking-gingersnap-da7582.netlify.app/api` }, // Adjusted URL
        ],
    };

    const autogen = swaggerAutogen({
        openapi: "3.0.0",
        servers: [{ url: "/x" }], // Adjust as needed
    })(outputFile, endpointsFiles, doc).then(() => {
        const swaggerDocument = require("." + outputFile);
        app.use(
            "/api/docs",
            swaggerUi.serve,
            swaggerUi.setup(swaggerDocument, {
                swaggerOptions: { persistAuthorization: true },
            }),
        );
        console.log(`Swagger docs available at https://frolicking-gingersnap-da7582.netlify.app/api/docs`);
    });
}

export { swaggerDocs };
