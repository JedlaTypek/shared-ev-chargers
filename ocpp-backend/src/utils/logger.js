import pino from 'pino';

const logger = pino({
  level: process.env.LOG_LEVEL || 'info', // 'debug' pro vývoj
  transport: process.env.NODE_ENV !== 'production' ? {
    target: 'pino-pretty',
    options: {
      colorize: true,
      translateTime: 'SYS:standard',
    }
  } : undefined,
  base: {
    service: 'ocpp-backend', // Název služby pro logy
  }
});

export default logger;