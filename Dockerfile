# Use the official Apify SDK for Python image as base
FROM apify/actor-python:3.11

# Copy requirements.txt to the container
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and its dependencies
RUN pip install playwright apify && \
    playwright install chromium && \
    playwright install-deps chromium

# Copy the rest of the source code
COPY . ./

# Run the Actor
CMD python3 -u main.py
