const Task = require('../models/Task');
const { addTaskToStream } = require('../config/redis');

const VALID_OPERATIONS = ['uppercase', 'lowercase', 'reverse', 'word_count'];

/**
 * POST /api/tasks
 * Create a new task with pending status and push its id to Redis stream.
 */
exports.createTask = async (req, res, next) => {
  try {
    const { title, inputText, operation } = req.body;

    if (!title || !inputText || !operation) {
      return res.status(400).json({ message: 'title, inputText and operation are required' });
    }

    if (!VALID_OPERATIONS.includes(operation)) {
      return res.status(400).json({ message: 'Invalid operation. Supported: uppercase, lowercase, reverse, word_count' });
    }

    const task = await Task.create({
      title,
      inputText,
      operation,
      status: 'pending',
      userId: req.user.id,
    });

    await addTaskToStream(task._id);

    res.status(201).json({ message: 'Task created successfully', task });
  } catch (error) {
    next(error);
  }
};

/**
 * GET /api/tasks
 * List all tasks belonging to the authenticated user.
 */
exports.getTasks = async (req, res, next) => {
  try {
    const tasks = await Task.find({ userId: req.user.id }).sort({ createdAt: -1 });
    res.json({ tasks });
  } catch (error) {
    next(error);
  }
};

/**
 * GET /api/tasks/:id
 * Get a single task (only if it belongs to the authenticated user).
 */
exports.getTask = async (req, res, next) => {
  try {
    const task = await Task.findOne({ _id: req.params.id, userId: req.user.id });
    if (!task) {
      return res.status(404).json({ message: 'Task not found' });
    }
    res.json({ task });
  } catch (error) {
    next(error);
  }
};

/**
 * PUT /api/tasks/:id
 * Update a task (only if it belongs to the authenticated user).
 */
exports.updateTask = async (req, res, next) => {
  try {
    const { title, inputText, operation } = req.body;
    const updateData = {};

    if (title !== undefined) updateData.title = title;
    if (inputText !== undefined) updateData.inputText = inputText;
    if (operation !== undefined) {
      if (!VALID_OPERATIONS.includes(operation)) {
        return res.status(400).json({ message: 'Invalid operation' });
      }
      updateData.operation = operation;
    }

    const task = await Task.findOneAndUpdate(
      { _id: req.params.id, userId: req.user.id },
      updateData,
      { new: true, runValidators: true }
    );

    if (!task) {
      return res.status(404).json({ message: 'Task not found' });
    }

    res.json({ message: 'Task updated successfully', task });
  } catch (error) {
    next(error);
  }
};

/**
 * DELETE /api/tasks/:id
 * Delete a task (only if it belongs to the authenticated user).
 */
exports.deleteTask = async (req, res, next) => {
  try {
    const task = await Task.findOneAndDelete({ _id: req.params.id, userId: req.user.id });
    if (!task) {
      return res.status(404).json({ message: 'Task not found' });
    }
    res.json({ message: 'Task deleted successfully' });
  } catch (error) {
    next(error);
  }
};

/**
 * GET /api/tasks/:id/logs
 * Get the logs of a task (only if it belongs to the authenticated user).
 */
exports.getTaskLogs = async (req, res, next) => {
  try {
    const task = await Task.findOne({ _id: req.params.id, userId: req.user.id }).select('logs');
    if (!task) {
      return res.status(404).json({ message: 'Task not found' });
    }
    res.json({ logs: task.logs || [] });
  } catch (error) {
    next(error);
  }
};