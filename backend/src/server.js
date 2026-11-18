const app = require('./app');
const connectDB = require('./config/db');
const { connectRedis } = require('./config/redis');
const config = require('./config/env');

const startServer = async () => {
  await connectDB();
  await connectRedis();

  app.listen(config.port, () => {
    console.log(`Server running on port ${config.port}`);
  });
};

startServer();