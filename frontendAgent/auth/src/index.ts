import express from 'express';
import cors from 'cors';
import bodyParser from 'body-parser';
import dotenv from 'dotenv';
import authRouter from './routes/auth.routes';

// Load environment variables
dotenv.config();

const app = express();
const port = process.env.AUTH_PORT || 3001;

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Basic health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

// Use auth routes
app.use('/auth', authRouter);

// Start server
app.listen(port, () => {
  console.log(`Auth service listening on port ${port}`);
}); 