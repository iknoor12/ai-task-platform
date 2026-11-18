const { createClient } = require('redis');
const config = require('./env');

const redisClient = createClient({ url: config.redisUrl });

redisClient.on('error', (err) => {
  console.error('Redis error:', err.message);
});

const connectRedis = async () => {
  try {
    await redisClient.connect();
    console.log('Redis connected');
  } catch (error) {
    console.error('Redis connection error:', error.message);
    process.exit(1);
  }
};

/**
 * Push a task id to the Redis stream named task_stream.
 * Other workers can consume this stream to process tasks.
 */
const addTaskToStream = async (taskId) => {
  await redisClient.xAdd('task_stream', '*', {
    taskId: taskId.toString()
  });
};

module.exports = { redisClient, connectRedis, addTaskToStream };