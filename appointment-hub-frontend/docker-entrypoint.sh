#!/bin/sh

# Replace environment variables in built files
# This allows runtime configuration of the React app

if [ ! -z "$REACT_APP_API_URL" ]; then
    echo "Setting API URL to: $REACT_APP_API_URL"
    find /usr/share/nginx/html -name "*.js" -exec sed -i "s|http://localhost:5002/api|$REACT_APP_API_URL|g" {} \;
fi

# Start nginx
exec "$@"

