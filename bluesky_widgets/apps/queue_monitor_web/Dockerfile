# Dockerfile for BlueSky Queue Monitor Web
FROM nginx:alpine

# Copy web application files
COPY . /usr/share/nginx/html/

# Copy nginx configuration template
COPY nginx.conf /etc/nginx/nginx.conf

# Set environment variable for queue server URL
ENV QUEUE_SERVER_URL=https://default-queueserver.bnl.gov:443

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]