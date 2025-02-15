import os
import argparse
import logging
from dotenv import load_dotenv
from src.controllers.image_generation_controller import ImageGenerationController
from src.controllers.llm_provider_controller import LLMProviderController


def setup_logging():
    level = logging.DEBUG if os.getenv("DEBUG_MODE") == "True" else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s - %(message)s - %(name)s')


def parse_args():
    parser = argparse.ArgumentParser(description='Analyze script and generate Dockerfile')
    parser.add_argument('script_path', help='Path to the script file within the repository')
    parser.add_argument('example_path', help='Path to the markdown file containing usage examples')
    parser.add_argument('--model', default='openai', help='Specify the LLM model to use (default: openai)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    return parser.parse_args()

def main():
    load_dotenv()
    args = parse_args()

    if args.debug:
        os.environ["DEBUG_MODE"] = "True"

    setup_logging()

    # Run the docker generation process
    llm_provider_controller = LLMProviderController(args.model)
    llm_provider = llm_provider_controller.get_llm_provider()
    image_generation_controller = ImageGenerationController(llm_provider)
    success = image_generation_controller.run(args.script_path, args.example_path)

    exit(0 if success else 1)

if __name__ == "__main__":
    main() 