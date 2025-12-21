
from jinja2 import Environment, FileSystemLoader
import os

template_dir = os.path.abspath('app/templates')
env = Environment(loader=FileSystemLoader(template_dir))

try:
    env.get_template('customer/detail.html')
    print("Syntax OK")
except Exception as e:
    print(f"Syntax Error: {e}")
