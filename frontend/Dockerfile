# Stage 1: Build
FROM node:20 AS builder

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# Build the application
# Note: VITE_ variables must be present at build time or handled via runtime config.
# We assume they are passed via build args or .env file present during build context.
RUN npm run build

# Stage 2: Serve
FROM node:20-alpine

WORKDIR /app

# Install 'serve' package globally to serve static files
RUN npm install -g serve

# Copy built assets from builder stage
COPY --from=builder /app/dist ./dist

EXPOSE 3000

# Start server on port 3000, SPA mode (-s)
CMD ["serve", "-s", "dist", "-l", "3000"]
