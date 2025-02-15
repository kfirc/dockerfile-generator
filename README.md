# Dockerfile-Generator

## Background

The Dockerfile-Generator tool is designed to automate the process of wrapping existing scripts into Docker containers using generative AI. It leverages the OpenAI and Google APIs to generate Dockerfiles for provided scripts, which could be written in any scripting language. Once the Dockerfile is generated, the tool builds and tests the Docker image, ensuring that the wrapped script runs correctly. The tool is designed to be generic, making it adaptable to different scripts, and it comes with example usage that verifies the successful operation of the wrapped scripts within Docker containers.

## Instructions for Running the Tool

1. **Set Up Environment Variables**:
   Create a `.env` file in the root of your project directory with the following content:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   GOOGLE_API_KEY=your_google_api_key_here
   DEBUG_MODE=false
   ```

2. **Build the Docker Image**:
   Open your terminal and navigate to the project directory. Run the following command to build the Docker image:
   ```bash
   docker build -t dockerfile-generator .
   ```

3. **Run the Docker Container**:
   To run the tool, use the following command, replacing the paths with your actual script and example file paths:
   ```bash
   docker run --rm -v ./examples/sample_scripts:/mnt/host \
     -v /var/run/docker.sock:/var/run/docker.sock \
     dockerfile-generator /mnt/host/vowel_counter.js /mnt/host/README_vowel_counter.md
   ```

   - The `-v` flag mounts the `sample_scripts` directory from your host to the container, allowing the tool to access your scripts.
   - The second `-v` flag allows the container to communicate with the Docker daemon on your host, enabling it to build and run Docker images.

4. **Verify the Output**:
   After running the command, check the output logs in your terminal to ensure that the Dockerfile was generated successfully and that the image was built and tested correctly.

5. **Debugging**:
If you run into issues, make sure Docker is running and your environment variables are set correctly. For more detailed logs, enable debug mode by setting DEBUG_MODE=true in your .env file or by adding the --debug flag to the command.

By following these steps, you should be able to run the tool and generate Dockerfiles for your scripts effectively.
