const express = require('express');
const router = express.Router();
const taskController = require('../controllers/taskController');
const { authenticate } = require('../middleware/authMiddleware');

router.post('/', authenticate, taskController.createTask);
router.get('/', authenticate, taskController.getTasks);
router.get('/:id', authenticate, taskController.getTask);
router.put('/:id', authenticate, taskController.updateTask);
router.delete('/:id', authenticate, taskController.deleteTask);
router.get('/:id/logs', authenticate, taskController.getTaskLogs);

module.exports = router;