# ---------------------------
# 1) Builder stage
# ---------------------------
FROM node:20-slim AS builder

# Create app directory
WORKDIR /app

# Copy package.json and package-lock.json first (better for caching)
COPY package*.json ./

# Install dependencies (includes devDependencies needed for building)
RUN npm install

# Copy all source code
COPY . .

# Build the project
RUN npm run build

# ---------------------------
# 2) Production stage
# ---------------------------
FROM node:20-alpine AS production

# Create app directory
WORKDIR /app

# Copy only the production dependency files from the builder
COPY --from=builder /app/package*.json ./

# Install only production dependencies
RUN npm install --omit=dev --ignore-scripts

# Copy the built Next.js output and any other needed files
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public

# Expose the port that Next.js runs on
EXPOSE 3000

# Start the Next.js application
CMD ["npm", "start"]
