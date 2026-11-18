require('dotenv').config();

const config = {
  port: process.env.PORT || 4000,
  mongoUri: process.env.MONGO_URI || 'mongodb://localhost:27017/ai_task_platform',
  jwtSecret: process.env.JWT_SECRET || 'replace_with_a_secure_secret',
  jwtExpiresIn: process.env.JWT_EXPIRES_IN || '1d',
  redisUrl: process.env.REDIS_URL || 'redis://localhost:6379',
  frontendUrl: process.env.FRONTEND_URL || 'http://localhost:5173',
};

module.exports = config;