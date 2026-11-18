const mongoose = require('mongoose');

const taskSchema = new mongoose.Schema(
  {
    title: { type: String, required: true, trim: true },
    inputText: { type: String, required: true },
    operation: {
      type: String,
      enum: ['uppercase', 'lowercase', 'reverse', 'word_count'],
      required: true,
    },
    status: { type: String, enum: ['pending', 'running', 'success', 'failed'], default: 'pending' },
    result: { type: String },
    logs: [{ type: String }],
    error: { type: String },
    userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
  },
  { timestamps: true }
);

taskSchema.index({ userId: 1, createdAt: -1 });
taskSchema.index({ status: 1, createdAt: -1 });

module.exports = mongoose.model('Task', taskSchema);