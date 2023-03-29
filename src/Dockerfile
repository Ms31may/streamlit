   # Base Image to use
   FROM python:3.9-slim-buster

   # Set the working directory
   WORKDIR /app

   # Install the required packages for Streamlit and Pyfiresql
   RUN pip install protobuf==3.17.3 streamlit pyfiresql django plotly

   # Copy the rest of the application code into the container
   COPY . /app

   # Expose port 9000
   EXPOSE 9000

   # Set the entrypoint command to use the global environment
   CMD ["streamlit", "run", "main.py", "--server.port=9000", "--server.address=0.0.0.0"]