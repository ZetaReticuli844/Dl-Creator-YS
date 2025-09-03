// Simple JSON logger for frontend
class Logger {
  constructor(service = 'frontend') {
    this.service = service;
  }

  formatMessage(level, message, extra = {}) {
    return JSON.stringify({
      timestamp: new Date().toISOString(),
      level: level.toUpperCase(),
      service: this.service,
      message: message,
      ...extra
    });
  }

  info(message, extra = {}) {
    console.log(this.formatMessage('info', message, extra));
  }

  warn(message, extra = {}) {
    console.warn(this.formatMessage('warn', message, extra));
  }

  error(message, extra = {}) {
    console.error(this.formatMessage('error', message, extra));
  }

  debug(message, extra = {}) {
    console.debug(this.formatMessage('debug', message, extra));
  }
}

export default new Logger('dl-creator-frontend');
